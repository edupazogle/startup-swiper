#!/bin/bash

###############################################################################
# Startup Swiper - Comprehensive Launch Script
# Handles port clearing, health checks, and service launching
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
SERVICES_DIR="$PROJECT_ROOT/services"
LOGS_DIR="$PROJECT_ROOT/logs"

# Ports
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5000}
BACKEND_PORT=${BACKEND_PORT:-3000}

mkdir -p "$LOGS_DIR"
API_LOG="$LOGS_DIR/api.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"
BACKEND_LOG="$LOGS_DIR/backend.log"
SERVICES_LOG="$LOGS_DIR/services.log"

log_info(){ echo -e "${BLUE}[INFO]${NC} $*"; }
log_success(){ echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning(){ echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error(){ echo -e "${RED}[ERROR]${NC} $*"; }

check_port(){ local p=$1; lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1; }
kill_port(){ local p=$1; log_info "Checking port $p..."; if check_port "$p"; then log_warning "Port $p in use. Killing process..."; fuser -k $p/tcp 2>/dev/null || true; sleep 2; if check_port "$p"; then log_error "Failed to free port $p"; return 1; else log_success "Port $p freed successfully"; fi; else log_success "Port $p already free"; fi; }
clear_all_ports(){ log_info "=== Clearing All Ports ==="; kill_port $API_PORT; kill_port $FRONTEND_PORT; kill_port $BACKEND_PORT; log_success "All ports cleared"; }

setup_venv(){ log_info "=== Setting up Virtual Environment ==="; if [ ! -d "$VENV_PATH" ]; then log_info "Creating virtual environment..."; python3 -m venv "$VENV_PATH"; log_success "Virtual environment created"; fi; # shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"; log_success "Virtual environment activated"; log_info "Upgrading pip..."; pip install --upgrade pip setuptools wheel --quiet; if [ -f "$API_DIR/requirements.txt" ]; then log_info "Installing API dependencies..."; pip install -r "$API_DIR/requirements.txt" --quiet; log_success "API dependencies installed"; fi; }

run_basic_tests(){ log_info "=== Running Basic Launch Tests ==="; local dirs=("$API_DIR" "$FRONTEND_DIR" "$LOGS_DIR"); for d in "${dirs[@]}"; do [ -d "$d" ] && log_success "✓ $d exists" || log_warning "✗ $d not found"; done; if [[ "$VIRTUAL_ENV" != "" ]]; then log_success "✓ Virtual environment active: $VIRTUAL_ENV"; else log_warning "✗ Virtual environment not active"; fi; for pkg in fastapi uvicorn sqlalchemy; do python -c "import $pkg" 2>/dev/null && log_success "✓ $pkg installed" || log_warning "✗ $pkg missing"; done; command -v node >/dev/null && log_success "✓ Node.js $(node --version)" || log_warning "✗ Node.js not found"; command -v npm >/dev/null && log_success "✓ npm $(npm --version)" || log_warning "✗ npm not found"; for p in $API_PORT $FRONTEND_PORT $BACKEND_PORT; do check_port $p && log_warning "✗ Port $p in use" || log_success "✓ Port $p free"; done; log_success "Basic tests completed"; }

launch_api(){ log_info "=== Launching API Service ==="; [ -d "$API_DIR" ] || { log_error "API directory not found"; return 1; };
  cd "$API_DIR"
  log_info "Initializing database..."
  python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)" 2>/dev/null || true
  log_info "Starting FastAPI server on port $API_PORT..."
  uvicorn main:app --host 0.0.0.0 --port $API_PORT --reload >"$API_LOG" 2>&1 &
  echo $! >"$LOGS_DIR/api.pid"
  sleep 3
  cd "$PROJECT_ROOT"
  if check_port $API_PORT; then log_success "API service started (http://localhost:$API_PORT)"; else log_error "Failed to start API service"; return 1; fi }

launch_frontend(){ log_info "=== Launching Frontend Service ==="; [ -d "$FRONTEND_DIR" ] || { log_warning "Frontend directory not found"; return 0; };
  cd "$FRONTEND_DIR"
  if [ ! -d node_modules ] || [ ! -d node_modules/@vitejs ]; then
    log_info "Installing frontend dependencies..."
    npm install --include=dev 2>&1 | tee -a "$FRONTEND_LOG"
  else
    log_success "Frontend dependencies already installed"
  fi
  log_info "Starting frontend development server on port $FRONTEND_PORT..."
  FRONTEND_PORT="$FRONTEND_PORT" npm run dev >"$FRONTEND_LOG" 2>&1 &
  echo $! >"$LOGS_DIR/frontend.pid"
  sleep 6
  cd "$PROJECT_ROOT"
  if check_port $FRONTEND_PORT; then log_success "Frontend started (http://localhost:$FRONTEND_PORT)"; else log_warning "Frontend may not have started (check logs)"; fi }

launch_backend(){ log_info "=== Launching Backend Service ==="; if [ -d "$PROJECT_ROOT/backend" ]; then log_info "Backend service detected"; log_warning "Backend launch not implemented - add commands as needed"; else log_info "No separate backend service (API acts as backend)"; fi }

launch_services(){ log_info "=== Launching Additional Services ==="; if [ -d "$SERVICES_DIR" ]; then log_info "Services directory found"; [ -d "$SERVICES_DIR/cbinsights" ] && log_info "CB Insights service detected" || true; log_info "Additional services checked"; else log_info "No additional services directory"; fi }

show_status(){ log_info "=== Service Status ==="; echo ""; echo "Port Status:"; echo "------------"; if check_port $API_PORT; then echo -e "${GREEN}✓${NC} API Service (Port $API_PORT): RUNNING"; echo "  URL: http://localhost:$API_PORT"; echo "  Docs: http://localhost:$API_PORT/docs"; else echo -e "${RED}✗${NC} API Service (Port $API_PORT): NOT RUNNING"; fi; if check_port $FRONTEND_PORT; then echo -e "${GREEN}✓${NC} Frontend Service (Port $FRONTEND_PORT): RUNNING"; echo "  URL: http://localhost:$FRONTEND_PORT"; else echo -e "${RED}✗${NC} Frontend Service (Port $FRONTEND_PORT): NOT RUNNING"; fi; if check_port $BACKEND_PORT; then echo -e "${GREEN}✓${NC} Backend Service (Port $BACKEND_PORT): RUNNING"; else echo -e "${YELLOW}ℹ${NC} Backend Service (Port $BACKEND_PORT): NOT RUNNING (may not be needed)"; fi; echo ""; echo "Log Files:"; echo "----------"; echo "API logs: $API_LOG"; echo "Frontend logs: $FRONTEND_LOG"; echo "Backend logs: $BACKEND_LOG"; echo ""; }

CLEANUP_DONE=false
cleanup(){ if [ "$CLEANUP_DONE" = true ]; then return 0; fi; CLEANUP_DONE=true; log_info "=== Cleaning up ==="; [ -f "$LOGS_DIR/api.pid" ] && { kill $(cat "$LOGS_DIR/api.pid") 2>/dev/null || true; rm "$LOGS_DIR/api.pid"; }; [ -f "$LOGS_DIR/frontend.pid" ] && { kill $(cat "$LOGS_DIR/frontend.pid") 2>/dev/null || true; rm "$LOGS_DIR/frontend.pid"; }; clear_all_ports; }

main(){ echo ""; echo "=========================================="; echo "   Startup Swiper - Launch Script"; echo "=========================================="; echo ""; trap cleanup INT TERM; clear_all_ports; echo ""; setup_venv; echo ""; run_basic_tests; echo ""; launch_api; launch_frontend; echo ""; launch_backend; echo ""; launch_services; echo ""; show_status; log_success "All services launched (persistent)"; echo ""; log_info "Run './launch.sh stop' to terminate services"; while true; do sleep 60; done; }

case "${1:-}" in
  start) main ;;
  stop) cleanup; log_success "All services stopped" ;;
  status) show_status ;;
  restart) cleanup; sleep 2; main ;;
  test) setup_venv; run_basic_tests ;;
  *) main ;;
esac
