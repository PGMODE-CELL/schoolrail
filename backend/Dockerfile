FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl openssl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/backend
WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /etc/keys && \
    openssl genrsa -out /etc/keys/private.pem 2048 2>/dev/null && \
    openssl rsa -in /etc/keys/private.pem -pubout -out /etc/keys/public.pem 2>/dev/null

ENV PYTHONPATH=/app

RUN chmod +x scripts/run.sh
EXPOSE 8000

CMD ["scripts/run.sh"]
