#!/bin/bash
# test_makefile_instructions.sh - Test all local Makefile targets

set -e

ENV=${1:-local}
QUIET=${2:-}

log() { [[ "$QUIET" == "-q" ]] && return 0; echo "$@"; }

log "🧪 Testing Makefile instructions for $ENV environment"

# Test help/list available targets
log "📋 Available targets:"
make -f makefiles/local.mk -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | grep -v Makefile | sort | uniq

# Test 1: Install dependencies
log "📦 Testing local-install-deps..."
if make -f makefiles/local.mk local-install-deps; then
    log "✅ Dependencies installation: PASSED"
else
    log "❌ Dependencies installation: FAILED"
    exit 1
fi

# Test 2: Run migrations
log "🗄️  Testing local-migrations..."
if make -f makefiles/local.mk local-migrations; then
    log "✅ Migrations: PASSED"
else
    log "❌ Migrations: FAILED"
    exit 1
fi

# Test 3: Test environment setup
log "🔍 Testing local-test-env..."
if make -f makefiles/local.mk local-test-env; then
    log "✅ Test environment: PASSED"
else
    log "❌ Test environment: FAILED"
    exit 1
fi

# Test 4: Check services (non-blocking)
log "🐳 Testing docker services availability..."
if docker compose -f docker/docker-compose.local.yml ps | grep -q "Up"; then
    log "✅ Docker services: RUNNING"
else
    log "⚠️  Docker services: NOT RUNNING (run 'make local-services' first)"
fi

# Test 5: Check PostgreSQL status
log "🐘 Testing PostgreSQL status..."
if command -v psql >/dev/null 2>&1; then
    if make -f makefiles/local.mk local-postgres-status; then
        log "✅ PostgreSQL: AVAILABLE"
    else
        log "⚠️  PostgreSQL: NOT RUNNING (run 'make local-postgres-up' first)"
    fi
else
    log "⚠️  PostgreSQL client not installed"
fi

log "🎉 Makefile instruction tests completed"
log "📝 Next steps:"
log "   1. Run 'make local-services' to start Docker services"
log "   2. Run 'make local-postgres-up' to start PostgreSQL"
log "   3. Run 'make local-django' to start Django server"
log "   4. Run 'make local-test-env' to run full API tests"