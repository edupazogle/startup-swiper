#!/usr/bin/env bash
# Startup Swiper unified launcher: tests, port cleanup, and full launch
set -euo pipefail

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info(){ echo -e "${BLUE}[INFO]${NC} $*"; }
success(){ echo -e "${GREEN}[SUCCESS]${NC} $*"; }
warn(){ echo -e "${YELLOW}[WARNING]${NC} $*"; }
error(){ echo -e "${RED}[ERROR]${NC} $*"; }

# Paths
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT_DIR/api"
FRONTEND_DIR="$ROOT_DIR/app/startup-swipe-schedu"
LOGS_DIR="$ROOT_DIR/logs"
VENV_PATH="$ROOT_DIR/.venv"
mkdir -p "$LOGS_DIR"
API_LOG="$LOGS_DIR/api.log"; FRONTEND_LOG="$LOGS_DIR/frontend.log"

# Ports
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5000}

check_port(){ lsof -Pi :"$1" -sTCP:LISTEN -t >/dev/null 2>&1; }
kill_port(){ local p=$1; info "Checking port $p..."; if check_port "$p"; then warn "Port $p in use. Killing..."; fuser -k "$p"/tcp >/dev/null 2>&1 || true; sleep 1; check_port "$p" && { error "Failed to free $p"; return 1; } || success "Port $p freed"; else success "Port $p free"; fi }
clear_ports(){ info "=== Clearing Ports ==="; kill_port "$API_PORT"; kill_port "$FRONTEND_PORT"; success "Ports cleared"; }

setup_venv(){ info "=== Setting up Python VENV ==="; if [ ! -d "$VENV_PATH" ]; then python3 -m venv "$VENV_PATH"; success "VENV created"; fi; # shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"; pip install -U pip setuptools wheel --quiet; if [ -f "$API_DIR/requirements.txt" ]; then info "Installing API deps"; pip install -r "$API_DIR/requirements.txt" --quiet; fi; success "VENV ready"; }

basic_tests(){ info "=== Basic Tests ==="; for d in "$API_DIR" "$FRONTEND_DIR" "$LOGS_DIR"; do [ -d "$d" ] && success "✓ $d exists" || warn "✗ $d missing"; done; command -v node >/dev/null && success "✓ node $(node -v)" || warn "✗ node missing"; command -v npm >/dev/null && success "✓ npm $(npm -v)" || warn "✗ npm missing"; python -c 'import fastapi,uvicorn,sqlalchemy' >/dev/null 2>&1 && success "✓ API py deps" || warn "✗ Missing API py deps"; for p in "$API_PORT" "$FRONTEND_PORT"; do check_port "$p" && warn "✗ Port $p busy" || success "✓ Port $p free"; done; }

start_api(){ info "=== Launching API (:$API_PORT) ==="; [ -d "$API_DIR" ] || { warn "API dir not found"; return 0; }; (
  cd "$API_DIR" && nohup uvicorn main:app --host 0.0.0.0 --port "$API_PORT" --reload >"$API_LOG" 2>&1 & echo $! >"$LOGS_DIR/api.pid"
); sleep 2; check_port "$API_PORT" && success "API up http://localhost:$API_PORT" || error "API failed (see $API_LOG)"; }

prepare_frontend(){ info "Preparing frontend deps"; cd "$FRONTEND_DIR"; rm -rf node_modules/.vite-temp 2>/dev/null || true; if [ ! -d node_modules ]; then npm install --include=dev --quiet; else npm install --include=dev --quiet; success "node_modules present"; fi; # ensure vite & plugin-react (dev deps)
npm pkg get devDependencies.vite | grep -q '"' || npm i -D vite --quiet --include=dev; npm pkg get devDependencies["@vitejs/plugin-react"] | grep -q '"' || npm i -D @vitejs/plugin-react --quiet --include=dev;
# create fallback vite config when react plugin missing
if [ ! -d node_modules/@vitejs/plugin-react ]; then
  warn "@vitejs/plugin-react missing; generating fallback vite.config.fallback.ts"
  cat > vite.config.fallback.ts <<'EOF'
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import { resolve } from 'path'
const projectRoot = process.env.PROJECT_ROOT || __dirname
export default defineConfig({
  plugins: [tailwindcss()],
  server: { port: Number(process.env.FRONTEND_PORT) || 5000, strictPort: true, host: true },
  resolve: { alias: { '@': resolve(projectRoot, 'src') } },
});
EOF
fi
}

start_frontend(){ info "=== Launching Frontend (:$FRONTEND_PORT) ==="; [ -d "$FRONTEND_DIR" ] || { warn "Frontend dir not found"; return 0; }; (
  cd "$FRONTEND_DIR";
  if [ -d node_modules/@vitejs/plugin-react ]; then
    FRONTEND_PORT="$FRONTEND_PORT" nohup npm run dev >"$FRONTEND_LOG" 2>&1 & echo $! >"$LOGS_DIR/frontend.pid";
  else
    warn "Using fallback Vite config (no React plugin)";
    FRONTEND_PORT="$FRONTEND_PORT" nohup npx --yes vite --config vite.config.fallback.ts >"$FRONTEND_LOG" 2>&1 & echo $! >"$LOGS_DIR/frontend.pid";
  fi
); sleep 6; check_port "$FRONTEND_PORT" && success "Frontend up http://localhost:$FRONTEND_PORT" || warn "Frontend may not be up (see $FRONTEND_LOG)"; }

status(){ info "=== Status ==="; check_port "$API_PORT" && echo -e "API: ${GREEN}RUNNING${NC} :$API_PORT" || echo -e "API: ${RED}DOWN${NC}"; check_port "$FRONTEND_PORT" && echo -e "FE : ${GREEN}RUNNING${NC} :$FRONTEND_PORT" || echo -e "FE : ${RED}DOWN${NC}"; echo "Logs: $API_LOG | $FRONTEND_LOG"; }

CLEANED=false
cleanup(){ $CLEANED && return 0; CLEANED=true; info "=== Cleanup ==="; for f in api frontend; do [ -f "$LOGS_DIR/$f.pid" ] && { kill "$(cat "$LOGS_DIR/$f.pid")" 2>/dev/null || true; rm -f "$LOGS_DIR/$f.pid"; }; done; clear_ports; }

main(){ trap cleanup EXIT INT TERM; clear_ports; setup_venv; basic_tests; start_api; prepare_frontend; start_frontend; status; info "Press Ctrl+C to stop"; wait; }

case "${1:-start}" in
  start) main;;
  stop) cleanup; success "Stopped";;
  status) status;;
  test) setup_venv; basic_tests;;
  restart) cleanup; sleep 1; main;;
  *) main;;
esac
