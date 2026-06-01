FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /etc/keys && \
    openssl genrsa -out /etc/keys/private.pem 2048 2>/dev/null && \
    openssl rsa -in /etc/keys/private.pem -pubout -out /etc/keys/public.pem 2>/dev/null

ENV PYTHONPATH=/app

EXPOSE 8000

COPY scripts/run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
