#!/bin/bash
set -e

SERVICE=${SERVICE_NAME:-gateway}
PORT=${SERVICE_PORT:-8000}

case $SERVICE in
  gateway)
    MODULE="backend.services.gateway.main:app"
    ;;
  auth)
    MODULE="backend.services.auth.main:app"
    ;;
  fleet)
    MODULE="backend.services.fleet.main:app"
    ;;
  routing)
    MODULE="backend.services.routing.main:app"
    ;;
  students)
    MODULE="backend.services.students.main:app"
    ;;
  geo)
    MODULE="backend.services.geo.main:app"
    ;;
  tenant)
    MODULE="backend.services.tenant.main:app"
    ;;
  worker)
    exec celery -A backend.workers.celery_app worker -Q "${WORKER_QUEUES:-optimization,reports,notifications,sync}" -l info -c 4
    ;;
  *)
    echo "Unknown service: $SERVICE"
    echo "Valid: gateway, auth, fleet, routing, students, geo, tenant, worker"
    exit 1
    ;;
esac

exec uvicorn $MODULE --host 0.0.0.0 --port $PORT --log-level info --proxy-headers --forwarded-allow-ips '*'
