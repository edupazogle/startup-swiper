#!/bin/bash

###############################################################################
# Startup Swiper - Comprehensive Launch Script
# This script handles port clearing, health checks, and service launching
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
API_DIR="$PROJECT_ROOT/api"
FRONTEND_DIR="$PROJECT_ROOT/app/startup-swipe-schedu"
SERVICES_DIR="$PROJECT_ROOT/services"
LOGS_DIR="$PROJECT_ROOT/logs"

# Ports configuration
API_PORT=8000
FRONTEND_PORT=5000
BACKEND_PORT=3000

# Log files
mkdir -p "$LOGS_DIR"
API_LOG="$LOGS_DIR/api.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"
BACKEND_LOG="$LOGS_DIR/backend.log"
SERVICES_LOG="$LOGS_DIR/services.log"

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

###############################################################################
# Port Management
###############################################################################

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

kill_port() {
    local port=$1
    log_info "Checking port $port..."
    
    if check_port $port; then
        log_warning "Port $port is in use. Killing process..."
        fuser -k $port/tcp 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            log_error "Failed to free port $port"
            return 1
        else
            log_success "Port $port freed successfully"
        fi
    else
        log_success "Port $port is already free"
    fi
    return 0
}

clear_all_ports() {
    log_info "=== Clearing All Ports ==="
    kill_port $API_PORT
    kill_port $FRONTEND_PORT
    kill_port $BACKEND_PORT
    log_success "All ports cleared"
}

###############################################################################
# Virtual Environment Setup
###############################################################################

setup_venv() {
    log_info "=== Setting up Virtual Environment ==="
    
    if [ ! -d "$VENV_PATH" ]; then
        log_info "Creating virtual environment at $VENV_PATH..."
        python3 -m venv "$VENV_PATH"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel --quiet
    
    # Install API dependencies
    if [ -f "$API_DIR/requirements.txt" ]; then
        log_info "Installing API dependencies..."
        pip install -r "$API_DIR/requirements.txt" --quiet
        log_success "API dependencies installed"
    fi
}

###############################################################################
# Health Checks
###############################################################################

run_basic_tests() {
    log_info "=== Running Basic Launch Tests ==="
    
    # Test 1: Check if required directories exist
    log_info "Test 1: Checking directory structure..."
    local dirs=("$API_DIR" "$FRONTEND_DIR" "$LOGS_DIR")
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "✓ $dir exists"
        else
            log_warning "✗ $dir not found"
        fi
    done
    
    # Test 2: Check if virtual environment is activated
    log_info "Test 2: Checking virtual environment..."
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log_success "✓ Virtual environment is active: $VIRTUAL_ENV"
    else
        log_warning "✗ Virtual environment not active"
    fi
    
    # Test 3: Check Python packages
    log_info "Test 3: Checking Python packages..."
    local packages=("fastapi" "uvicorn" "sqlalchemy")
    for pkg in "${packages[@]}"; do
        if python -c "import $pkg" 2>/dev/null; then
            log_success "✓ $pkg is installed"
        else
            log_warning "✗ $pkg not found"
        fi
    done
    
    # Test 4: Check if Node.js is available (for frontend)
    log_info "Test 4: Checking Node.js..."
    if command -v node &> /dev/null; then
        log_success "✓ Node.js is installed: $(node --version)"
    else
        log_warning "✗ Node.js not found"
    fi
    
    # Test 5: Check if npm is available
    log_info "Test 5: Checking npm..."
    if command -v npm &> /dev/null; then
        log_success "✓ npm is installed: $(npm --version)"
    else
        log_warning "✗ npm not found"
    fi
    
    # Test 6: Verify ports are free
    log_info "Test 6: Checking ports availability..."
    local ports=($API_PORT $FRONTEND_PORT $BACKEND_PORT)
    for port in "${ports[@]}"; do
        if check_port $port; then
            log_warning "✗ Port $port is in use"
        else
            log_success "✓ Port $port is free"
        fi
    done
    
    log_success "Basic tests completed"
}

###############################################################################
# Service Launchers
###############################################################################

launch_api() {
    log_info "=== Launching API Service ==="
    
    if [ ! -d "$API_DIR" ]; then
        log_error "API directory not found: $API_DIR"
        return 1
    fi
    
    cd "$API_DIR"
    
    # Ensure database tables are created
    log_info "Initializing database..."
    python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)" 2>/dev/null || true
    
    # Start API server
    log_info "Starting FastAPI server on port $API_PORT..."
    nohup uvicorn main:app --host 0.0.0.0 --port $API_PORT --reload > "$API_LOG" 2>&1 &
    local api_pid=$!
    echo $api_pid > "$LOGS_DIR/api.pid"
    
    # Wait and verify
    sleep 3
    if check_port $API_PORT; then
        log_success "API service started successfully (PID: $api_pid)"
        log_info "API URL: http://localhost:$API_PORT"
        log_info "API Docs: http://localhost:$API_PORT/docs"
    else
        log_error "Failed to start API service"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
}

launch_frontend() {
    log_info "=== Launching Frontend Service ==="
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_warning "Frontend directory not found: $FRONTEND_DIR"
        return 0
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm install 2>&1 | tee -a "$FRONTEND_LOG"
    fi
    
    # Start frontend dev server
    log_info "Starting frontend development server on port $FRONTEND_PORT..."
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > "$LOGS_DIR/frontend.pid"
    
    # Wait and verify
    sleep 5
    if check_port $FRONTEND_PORT; then
        log_success "Frontend service started successfully (PID: $frontend_pid)"
        log_info "Frontend URL: http://localhost:$FRONTEND_PORT"
    else
        log_warning "Frontend service may not have started (check logs)"
    fi
    
    cd "$PROJECT_ROOT"
}

launch_backend() {
    log_info "=== Launching Backend Service ==="
    
    # Backend service placeholder - adjust based on actual backend requirements
    if [ -d "$PROJECT_ROOT/backend" ]; then
        log_info "Backend service detected"
        # Add backend launch commands here if needed
        log_warning "Backend launch not implemented - add commands as needed"
    else
        log_info "No separate backend service found (API serves as backend)"
    fi
}

launch_services() {
    log_info "=== Launching Additional Services ==="
    
    if [ -d "$SERVICES_DIR" ]; then
        log_info "Services directory found: $SERVICES_DIR"
        
        # CB Insights service
        if [ -d "$SERVICES_DIR/cbinsights" ]; then
            log_info "CB Insights service detected"
            # Add CB Insights service launch commands if needed
        fi
        
        log_info "Additional services checked"
    else
        log_info "No additional services directory found"
    fi
}

###############################################################################
# Service Status
###############################################################################

show_status() {
    log_info "=== Service Status ==="
    
    echo ""
    echo "Port Status:"
    echo "------------"
    
    if check_port $API_PORT; then
        echo -e "${GREEN}✓${NC} API Service (Port $API_PORT): RUNNING"
        echo "  URL: http://localhost:$API_PORT"
        echo "  Docs: http://localhost:$API_PORT/docs"
    else
        echo -e "${RED}✗${NC} API Service (Port $API_PORT): NOT RUNNING"
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✓${NC} Frontend Service (Port $FRONTEND_PORT): RUNNING"
        echo "  URL: http://localhost:$FRONTEND_PORT"
    else
        echo -e "${RED}✗${NC} Frontend Service (Port $FRONTEND_PORT): NOT RUNNING"
    fi
    
    if check_port $BACKEND_PORT; then
        echo -e "${GREEN}✓${NC} Backend Service (Port $BACKEND_PORT): RUNNING"
        echo "  URL: http://localhost:$BACKEND_PORT"
    else
        echo -e "${YELLOW}ℹ${NC} Backend Service (Port $BACKEND_PORT): NOT RUNNING (may not be needed)"
    fi
    
    echo ""
    echo "Log Files:"
    echo "----------"
    echo "API logs: $API_LOG"
    echo "Frontend logs: $FRONTEND_LOG"
    echo "Backend logs: $BACKEND_LOG"
    echo ""
}

###############################################################################
# Cleanup
###############################################################################

cleanup() {
    log_info "=== Cleaning up ==="
    
    if [ -f "$LOGS_DIR/api.pid" ]; then
        kill $(cat "$LOGS_DIR/api.pid") 2>/dev/null || true
        rm "$LOGS_DIR/api.pid"
    fi
    
    if [ -f "$LOGS_DIR/frontend.pid" ]; then
        kill $(cat "$LOGS_DIR/frontend.pid") 2>/dev/null || true
        rm "$LOGS_DIR/frontend.pid"
    fi
    
    clear_all_ports
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo ""
    echo "=========================================="
    echo "   Startup Swiper - Launch Script"
    echo "=========================================="
    echo ""
    
    # Handle cleanup on script exit
    trap cleanup EXIT INT TERM
    
    # Step 1: Clear ports
    clear_all_ports
    echo ""
    
    # Step 2: Setup virtual environment
    setup_venv
    echo ""
    
    # Step 3: Run basic tests
    run_basic_tests
    echo ""
    
    # Step 4: Launch services
    launch_api
    echo ""
    
    launch_frontend
    echo ""
    
    launch_backend
    echo ""
    
    launch_services
    echo ""
    
    # Step 5: Show status
    show_status
    
    log_success "All services launched successfully!"
    echo ""
    log_info "Press Ctrl+C to stop all services"
    echo ""
    
    # Keep script running to maintain services
    wait
}

# Handle command line arguments
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
    test)
        setup_venv
        run_basic_tests
        ;;
    *)
        main
        ;;
esac
