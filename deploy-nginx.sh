#!/bin/bash

###############################################################################
# NGINX Configuration Deployment Script
# This script should be run on the production server to update NGINX config
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

echo "=========================================="
echo "  NGINX Configuration Deployment"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root or with sudo"
    exit 1
fi

NGINX_CONF_SOURCE="/home/appuser/startup-swiper/nginx-production.conf"
NGINX_CONF_DEST="/etc/nginx/sites-available/tilyn.ai"
NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/tilyn.ai"

# Backup existing configuration
if [ -f "$NGINX_CONF_DEST" ]; then
    log_info "Backing up existing NGINX configuration..."
    cp "$NGINX_CONF_DEST" "$NGINX_CONF_DEST.backup.$(date +%Y%m%d_%H%M%S)"
    log_success "Backup created"
fi

# Copy new configuration
log_info "Installing new NGINX configuration..."
cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"
log_success "Configuration copied"

# Create symbolic link if it doesn't exist
if [ ! -L "$NGINX_CONF_ENABLED" ]; then
    log_info "Enabling site configuration..."
    ln -s "$NGINX_CONF_DEST" "$NGINX_CONF_ENABLED"
    log_success "Site enabled"
fi

# Remove default site if it exists
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    log_info "Removing default site..."
    rm -f /etc/nginx/sites-enabled/default
fi

# Test NGINX configuration
log_info "Testing NGINX configuration..."
if nginx -t; then
    log_success "NGINX configuration is valid"
    
    # Reload NGINX
    log_info "Reloading NGINX..."
    systemctl reload nginx
    log_success "NGINX reloaded successfully"
    
    # Check NGINX status
    if systemctl is-active --quiet nginx; then
        log_success "NGINX is running"
    else
        log_error "NGINX is not running!"
        systemctl status nginx
        exit 1
    fi
else
    log_error "NGINX configuration test failed!"
    log_warning "Restoring backup..."
    if [ -f "$NGINX_CONF_DEST.backup."* ]; then
        cp "$NGINX_CONF_DEST.backup."* "$NGINX_CONF_DEST"
        log_warning "Backup restored. Please check the configuration."
    fi
    exit 1
fi

echo ""
echo "=========================================="
log_success "NGINX Configuration Deployed!"
echo "=========================================="
echo ""
echo "Test your endpoints:"
echo "  curl https://tilyn.ai/api/health"
echo "  curl -X POST https://tilyn.ai/auth/register -H 'Content-Type: application/json' -d '{\"email\":\"test@test.com\",\"password\":\"test123\",\"username\":\"test\"}'"
echo ""
