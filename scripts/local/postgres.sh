#!/bin/bash
set -euo pipefail

load_env() {
  [[ -f ".env.local" ]] && export $(grep -E '^DB_' .env.local | xargs)
  : "${DB_NAME:?Missing DB_NAME}"
  : "${DB_USER:?Missing DB_USER}" 
  : "${DB_PASSWORD:?Missing DB_PASSWORD}"
  : "${DB_HOST:=127.0.0.1}"
  : "${DB_PORT:=5432}"
}

case "${1:-}" in
  up)
    load_env
    sudo systemctl start postgresql
    
    sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || \
      sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    
    sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
      sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    ;;
    
  down)
    sudo systemctl stop postgresql
    ;;
    
  status)
    load_env
    echo "Service: $(sudo systemctl is-active postgresql)"
    echo "Connection: $(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT 'OK'" 2>/dev/null || echo 'FAILED')"
    ;;
    
  *)
    echo "Usage: $0 {up|down|status}"
    exit 1
    ;;
esac