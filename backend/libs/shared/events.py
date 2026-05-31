import json
import logging
from datetime import datetime, date
from typing import Callable, Awaitable, Optional
from uuid import uuid4

import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode, IncomingMessage

from backend.libs.shared.models import EventMessage

logger = logging.getLogger("schoolrail.events")

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class EventBus:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.RobustChannel] = None
        self._exchange: Optional[aio_pika.Exchange] = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self.amqp_url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange("schoolrail.events", ExchangeType.TOPIC, durable=True)

    async def publish(self, event_type: str, tenant_id: str, payload: dict) -> None:
        event = EventMessage(
            event_id=str(uuid4()),
            event_type=event_type,
            tenant_id=tenant_id,
            payload=payload,
            timestamp=datetime.utcnow(),
        )
        message = Message(
            body=json.dumps(event.model_dump(), cls=DateTimeEncoder).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=event.event_id,
        )
        routing_key = f"tenant.{tenant_id}.{event_type}"
        await self._exchange.publish(message, routing_key)
        logger.info("event_published", extra={"event_type": event_type, "tenant_id": tenant_id, "routing_key": routing_key})

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()

class EventConsumer:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.RobustChannel] = None
        self._queue: Optional[aio_pika.Queue] = None
        self._handlers: dict[str, list[Callable[[EventMessage], Awaitable[None]]]] = {}
        self._dlx: Optional[aio_pika.Exchange] = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self.amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.declare_exchange("schoolrail.events", ExchangeType.TOPIC, durable=True)
        self._dlx = await self._channel.declare_exchange("schoolrail.events.dlx", ExchangeType.FANOUT, durable=True)
        dlq = await self._channel.declare_queue("schoolrail.events.dead.letter", durable=True)
        await dlq.bind(self._dlx)
        self._queue = await self._channel.declare_queue(self.queue_name, durable=True)
        await self._queue.consume(self._on_message)

    def subscribe(self, event_type: str, handler: Callable[[EventMessage], Awaitable[None]]) -> None:
        pattern = f"tenant.*.{event_type}"
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            self._channel.queue_bind(self._queue, "schoolrail.events", pattern)
        self._handlers[event_type].append(handler)

    async def _on_message(self, message: IncomingMessage) -> None:
        async with message.process(ignore_processed=True):
            try:
                data = json.loads(message.body.decode())
                event = EventMessage(**data)
                handlers = self._handlers.get(event.event_type, [])
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error("handler_error", extra={"event_type": event.event_type, "error": str(e)})
                await message.ack()
            except Exception as e:
                logger.error("event_processing_error", extra={"error": str(e)})
                await message.reject(requeue=False)
                if self._dlx:
                    await self._dlx.publish(
                        Message(body=message.body, delivery_mode=DeliveryMode.PERSISTENT),
                        "",
                    )

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
