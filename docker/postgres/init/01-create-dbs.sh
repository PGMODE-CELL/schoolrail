#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE schoolrail_auth;
    CREATE DATABASE schoolrail_tenants;
    CREATE DATABASE schoolrail_analytics;
    CREATE DATABASE tenant_default;
EOSQL
