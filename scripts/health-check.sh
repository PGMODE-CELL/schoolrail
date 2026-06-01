#!/bin/bash
# Health check for all SchoolRail services
set -e

SERVICES=(
    "gateway:8000"
    "auth-service:8001"
    "fleet-service:8002"
    "routing-service:8003"
    "student-service:8004"
    "geo-service:8005"
    "tenant-service:8006"
    "admin:3000"
    "prometheus:9090"
    "grafana:3001"
    "jaeger:16686"
)

echo "SchoolRail Health Check"
echo "======================"
ALL_OK=true

for svc in "${SERVICES[@]}"; do
    NAME="${svc%%:*}"
    PORT="${svc##*:}"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://localhost:$PORT/health" 2>/dev/null || echo "000")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "301" ]; then
        echo "  ✅ $NAME (:$PORT) — $STATUS"
    else
        echo "  ❌ $NAME (:$PORT) — $STATUS"
        ALL_OK=false
    fi
done

echo ""
if [ "$ALL_OK" = true ]; then
    echo "✅ All services healthy"
    echo ""
    echo "Access:"
    echo "  Admin Panel: http://localhost:3000"
    echo "  API Gateway: http://localhost:8000"
    echo "  Grafana:     http://localhost:3001 (admin/admin)"
    echo "  Jaeger:      http://localhost:16686"
    echo "  MinIO:       http://localhost:9001 (schoolrail/password123)"
    echo "  RabbitMQ:    http://localhost:15672 (schoolrail/password)"
    echo "  MailHog:     http://localhost:8025"
    echo ""
    echo "Login: admin@schoolrail.com / admin123"
else
    echo "❌ Some services are unhealthy"
    exit 1
fi
