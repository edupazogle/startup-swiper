#!/bin/bash

###############################################################################
# Startup Swiper - Simplified Launch Script (uses existing venv)
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
API_DIR="$PROJECT_ROOT/api"
FRONTEND_DIR="$PROJECT_ROOT/app/startup-swipe-schedu"
LOGS_DIR="$PROJECT_ROOT/logs"

# Ports
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5000}

mkdir -p "$LOGS_DIR"
API_LOG="$LOGS_DIR/api.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_port() {
    local p=$1
    lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1
}

kill_port() {
    local p=$1
    log_info "Checking port $p..."
    if check_port "$p"; then
        log_warning "Port $p in use. Killing process..."
        fuser -k $p/tcp 2>/dev/null || true
        sleep 2
        if check_port "$p"; then
            log_error "Failed to free port $p"
            return 1
        else
            log_success "Port $p freed successfully"
        fi
    else
        log_success "Port $p already free"
    fi
}

clear_all_ports() {
    log_info "=== Clearing All Ports ==="
    kill_port $API_PORT
    kill_port $FRONTEND_PORT
    log_success "All ports cleared"
}

activate_venv() {
    log_info "=== Activating Virtual Environment ==="
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_info "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r api/requirements.txt"
        return 1
    fi
    # shellcheck disable=SC1091
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
}

verify_database() {
    log_info "=== Verifying Database ==="
    cd "$API_DIR"
    python -c "
from database import SessionLocal
import db_queries

db = SessionLocal()
count = db_queries.count_startups(db)
stats = db_queries.get_enrichment_stats(db)
print(f'✓ Database connected: {count} startups')
print(f'✓ Enriched: {stats[\"enriched_count\"]} ({stats[\"enrichment_percentage\"]}%)')
db.close()
" && log_success "Database verified" || log_error "Database check failed"
    cd "$PROJECT_ROOT"
}

launch_api() {
    log_info "=== Launching API Service ==="
    [ -d "$API_DIR" ] || { log_error "API directory not found"; return 1; }
    
    cd "$API_DIR"
    log_info "Starting FastAPI server on port $API_PORT..."
    nohup uvicorn main:app --host 0.0.0.0 --port $API_PORT --reload > "$API_LOG" 2>&1 &
    echo $! > "$LOGS_DIR/api.pid"
    sleep 5
    cd "$PROJECT_ROOT"
    
    if check_port $API_PORT; then
        log_success "API service started (http://localhost:$API_PORT)"
        log_info "API Docs: http://localhost:$API_PORT/docs"
    else
        log_error "Failed to start API service"
        return 1
    fi
}

launch_frontend() {
    log_info "=== Launching Frontend Service ==="
    [ -d "$FRONTEND_DIR" ] || { log_warning "Frontend directory not found"; return 0; }
    
    cd "$FRONTEND_DIR"
    
    if [ ! -d node_modules ]; then
        log_info "Installing frontend dependencies..."
        npm install
    else
        log_success "Frontend dependencies already installed"
    fi
    
    log_info "Starting frontend development server on port $FRONTEND_PORT..."
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$LOGS_DIR/frontend.pid"
    sleep 8
    cd "$PROJECT_ROOT"
    
    if check_port $FRONTEND_PORT; then
        log_success "Frontend started (http://localhost:$FRONTEND_PORT)"
    else
        log_warning "Frontend may not have started (check logs)"
    fi
}

show_status() {
    log_info "=== Service Status ==="
    echo ""
    echo "Port Status:"
    echo "------------"
    
    if check_port $API_PORT; then
        echo -e "${GREEN}✓${NC} API Service (Port $API_PORT): RUNNING"
        echo "  URL: http://localhost:$API_PORT"
        echo "  Docs: http://localhost:$API_PORT/docs"
        echo "  Health: http://localhost:$API_PORT/health"
    else
        echo -e "${RED}✗${NC} API Service (Port $API_PORT): NOT RUNNING"
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✓${NC} Frontend Service (Port $FRONTEND_PORT): RUNNING"
        echo "  URL: http://localhost:$FRONTEND_PORT"
    else
        echo -e "${RED}✗${NC} Frontend Service (Port $FRONTEND_PORT): NOT RUNNING"
    fi
    
    echo ""
    echo "Log Files:"
    echo "----------"
    echo "API logs: tail -f $API_LOG"
    echo "Frontend logs: tail -f $FRONTEND_LOG"
    echo ""
    
    # Test API health
    if check_port $API_PORT; then
        log_info "Testing API health..."
        curl -s http://localhost:$API_PORT/health | head -5 || true
        echo ""
    fi
}

cleanup() {
    log_info "=== Cleaning up ==="
    
    [ -f "$LOGS_DIR/api.pid" ] && {
        kill $(cat "$LOGS_DIR/api.pid") 2>/dev/null || true
        rm "$LOGS_DIR/api.pid"
    }
    
    [ -f "$LOGS_DIR/frontend.pid" ] && {
        kill $(cat "$LOGS_DIR/frontend.pid") 2>/dev/null || true
        rm "$LOGS_DIR/frontend.pid"
    }
    
    clear_all_ports
    log_success "Cleanup complete"
}

main() {
    echo ""
    echo "=========================================="
    echo "   Startup Swiper - Launch Platform"
    echo "=========================================="
    echo ""
    
    trap cleanup INT TERM EXIT
    
    clear_all_ports
    echo ""
    
    activate_venv || exit 1
    echo ""
    
    verify_database
    echo ""
    
    launch_api || exit 1
    echo ""
    
    launch_frontend
    echo ""
    
    show_status
    
    log_success "Platform launched successfully!"
    echo ""
    log_info "Press Ctrl+C to stop all services"
    echo ""
    
    # Keep script running
    while true; do
        sleep 60
        # Optionally check if services are still running
        if ! check_port $API_PORT; then
            log_error "API service died unexpectedly"
            break
        fi
    done
}

case "${1:-}" in
    start)
        main
        ;;
    stop)
        cleanup
        log_success "All services stopped"
        ;;
    status)
        show_status
        ;;
    restart)
        cleanup
        sleep 2
        main
        ;;
    *)
        main
        ;;
esac
