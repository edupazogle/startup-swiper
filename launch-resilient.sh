#!/bin/bash

###############################################################################
# Startup Swiper - Resilient Launch Script
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
PID_DIR="$PROJECT_ROOT/logs/pids"

# Ports
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5000}

# Create directories
mkdir -p "$LOGS_DIR" "$PID_DIR"
API_LOG="$LOGS_DIR/api.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"
API_PID="$PID_DIR/api.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_port() {
    local p=$1
    netstat -tuln 2>/dev/null | grep -q ":$p " || lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1
}

kill_port() {
    local p=$1
    log_info "Checking port $p..."
    if check_port "$p"; then
        log_warning "Port $p in use. Killing process..."
        fuser -k $p/tcp 2>/dev/null || lsof -ti:$p | xargs kill -9 2>/dev/null || true
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
        log_warning "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        pip install --upgrade pip
        pip install -r "$API_DIR/requirements.txt"
        log_success "Virtual environment created and dependencies installed"
    else
        source "$VENV_PATH/bin/activate"
        log_success "Virtual environment activated"
    fi
}

verify_database() {
    log_info "=== Verifying Database ==="
    if [ ! -f "$PROJECT_ROOT/startup_swiper.db" ]; then
        log_warning "Database file not found. Creating..."
        cd "$API_DIR"
        python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database created successfully')
" && log_success "Database initialized" || log_error "Database initialization failed"
        cd "$PROJECT_ROOT"
        return
    fi
    
    cd "$API_DIR"
    python -c "
from database import SessionLocal
import db_queries

db = SessionLocal()
try:
    count = db_queries.count_startups(db)
    print(f'✓ Database connected: {count} startups')
except Exception as e:
    print(f'Database check: {e}')
finally:
    db.close()
" && log_success "Database verified" || log_warning "Database check had issues"
    cd "$PROJECT_ROOT"
}

launch_api() {
    log_info "=== Launching API Service ==="
    [ -d "$API_DIR" ] || { log_error "API directory not found"; return 1; }
    
    # Kill existing API process if exists
    if [ -f "$API_PID" ]; then
        local old_pid=$(cat "$API_PID")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_info "Stopping existing API process ($old_pid)..."
            kill "$old_pid" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$API_PID"
    fi
    
    cd "$API_DIR"
    log_info "Starting FastAPI server on port $API_PORT..."
    
    # Start API with proper error handling
    nohup uvicorn main:app --host 0.0.0.0 --port $API_PORT --reload \
        --log-level info \
        --access-log \
        > "$API_LOG" 2>&1 &
    
    local api_pid=$!
    echo $api_pid > "$API_PID"
    
    # Wait and verify
    log_info "Waiting for API to start (PID: $api_pid)..."
    for i in {1..30}; do
        if check_port $API_PORT; then
            log_success "API service started (http://localhost:$API_PORT)"
            log_info "API Docs: http://localhost:$API_PORT/docs"
            cd "$PROJECT_ROOT"
            return 0
        fi
        if ! kill -0 $api_pid 2>/dev/null; then
            log_error "API process died. Check logs: $API_LOG"
            tail -20 "$API_LOG"
            cd "$PROJECT_ROOT"
            return 1
        fi
        sleep 1
    done
    
    log_error "API failed to start within 30 seconds"
    cd "$PROJECT_ROOT"
    return 1
}

launch_frontend() {
    log_info "=== Launching Frontend Service ==="
    [ -d "$FRONTEND_DIR" ] || { log_warning "Frontend directory not found"; return 0; }
    
    # Kill existing frontend process if exists
    if [ -f "$FRONTEND_PID" ]; then
        local old_pid=$(cat "$FRONTEND_PID")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_info "Stopping existing frontend process ($old_pid)..."
            kill "$old_pid" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$FRONTEND_PID"
    fi
    
    cd "$FRONTEND_DIR"
    
    if [ ! -d node_modules ]; then
        log_info "Installing frontend dependencies..."
        npm install || { log_error "npm install failed"; return 1; }
    else
        log_success "Frontend dependencies already installed"
    fi
    
    log_info "Starting frontend development server on port $FRONTEND_PORT..."
    nohup npm run dev -- --host 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
    
    local frontend_pid=$!
    echo $frontend_pid > "$FRONTEND_PID"
    
    # Wait and verify
    log_info "Waiting for frontend to start (PID: $frontend_pid)..."
    for i in {1..30}; do
        if check_port $FRONTEND_PORT; then
            log_success "Frontend started (http://localhost:$FRONTEND_PORT)"
            cd "$PROJECT_ROOT"
            return 0
        fi
        if ! kill -0 $frontend_pid 2>/dev/null; then
            log_warning "Frontend process died. Check logs: $FRONTEND_LOG"
            cd "$PROJECT_ROOT"
            return 1
        fi
        sleep 1
    done
    
    log_warning "Frontend may not have started within 30 seconds"
    cd "$PROJECT_ROOT"
}

monitor_services() {
    log_info "=== Monitoring Services ==="
    while true; do
        sleep 30
        
        # Check API
        if [ -f "$API_PID" ]; then
            local api_pid=$(cat "$API_PID")
            if ! kill -0 "$api_pid" 2>/dev/null; then
                log_error "API service died unexpectedly. Restarting..."
                rm -f "$API_PID"
                launch_api || {
                    log_error "Failed to restart API. Exiting."
                    exit 1
                }
            fi
        fi
        
        # Check Frontend
        if [ -f "$FRONTEND_PID" ]; then
            local frontend_pid=$(cat "$FRONTEND_PID")
            if ! kill -0 "$frontend_pid" 2>/dev/null; then
                log_warning "Frontend service died. Restarting..."
                rm -f "$FRONTEND_PID"
                launch_frontend
            fi
        fi
    done
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
        [ -f "$API_PID" ] && echo "  PID: $(cat $API_PID)"
    else
        echo -e "${RED}✗${NC} API Service (Port $API_PORT): NOT RUNNING"
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✓${NC} Frontend Service (Port $FRONTEND_PORT): RUNNING"
        echo "  URL: http://localhost:$FRONTEND_PORT"
        [ -f "$FRONTEND_PID" ] && echo "  PID: $(cat $FRONTEND_PID)"
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
        curl -s http://localhost:$API_PORT/health 2>/dev/null | head -5 || echo "Health check unavailable"
        echo ""
    fi
}

cleanup() {
    log_info "=== Cleaning up ==="
    
    if [ -f "$API_PID" ]; then
        local pid=$(cat "$API_PID")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Stopping API (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$API_PID"
    fi
    
    if [ -f "$FRONTEND_PID" ]; then
        local pid=$(cat "$FRONTEND_PID")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Stopping Frontend (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID"
    fi
    
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
    log_info "Services will automatically restart if they crash"
    echo ""
    
    # Monitor and restart services if needed
    monitor_services
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
    logs)
        case "${2:-}" in
            api)
                tail -f "$API_LOG"
                ;;
            frontend)
                tail -f "$FRONTEND_LOG"
                ;;
            *)
                echo "Usage: $0 logs [api|frontend]"
                ;;
        esac
        ;;
    *)
        main
        ;;
esac
