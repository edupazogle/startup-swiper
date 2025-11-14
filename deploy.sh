#!/bin/bash
# Deploy Startup Swiper to GitHub and Render.com
# This script guides you through the deployment process

set -e

echo "=========================================="
echo "🚀 Startup Swiper Deployment Assistant"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Please run this script from the project root."
    exit 1
fi

echo "Step 1: Checking Git status..."
if [ -d ".git" ]; then
    echo "✓ Git repository initialized"
else
    echo "⚠️  Git not initialized. Run: git init"
    exit 1
fi

echo ""
echo "Step 2: Current git status"
git status --short | head -20

echo ""
echo "Step 3: Environment Variables Check"
echo "========================================"
echo ""
echo "For Render.com, you'll need these environment variables:"
echo ""
echo "Backend (API Service):"
echo "  DATABASE_URL=sqlite:///./startup_swiper.db"
echo "  VAPID_PUBLIC_KEY=BIJjEmB_TRF29nRJ8uaOR_n3N5PnpxRd8I1r_2WHcSt0mMTCFnhwGAP6A2aWBKhUkwt82pDaNMAoRnodbQP1k3M"
echo "  VAPID_PRIVATE_KEY=jsvWNpTlUb7j_DfNAJL1qSkjT65pOO-YrUNTYure8Tw"
echo "  SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "your_secret_key_here")"
echo ""
echo "Frontend (Web Service):"
echo "  VITE_API_URL=https://YOUR-API-NAME.onrender.com"
echo ""
echo "========================================"
echo ""

read -p "Have you created a GitHub repository? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/startup-swiper.git): " REPO_URL
    
    # Check if remote already exists
    if git remote | grep -q "origin"; then
        echo "Remote 'origin' already exists. Updating..."
        git remote set-url origin "$REPO_URL"
    else
        echo "Adding remote 'origin'..."
        git remote add origin "$REPO_URL"
    fi
    
    echo ""
    echo "Step 4: Pushing to GitHub..."
    git push -u origin main
    
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "=========================================="
    echo "Next Steps:"
    echo "=========================================="
    echo ""
    echo "1. Go to https://render.com"
    echo "2. Click 'New' → 'Blueprint'"
    echo "3. Connect your GitHub repository: $REPO_URL"
    echo "4. Click 'Apply'"
    echo ""
    echo "5. Configure Environment Variables:"
    echo "   - Go to Dashboard → API Service → Environment"
    echo "   - Add the variables listed above"
    echo ""
    echo "6. Update Frontend API URL:"
    echo "   - Go to Dashboard → Frontend Service → Environment"
    echo "   - Set VITE_API_URL to your API URL"
    echo ""
    echo "7. Wait for deployment (5-10 minutes)"
    echo ""
    echo "8. Test your deployment:"
    echo "   - Login with: nicolas.desaintromain@axa.com / 123"
    echo "   - Or any other pre-configured user"
    echo ""
    echo "=========================================="
    echo "🎉 Deployment Ready!"
    echo "=========================================="
    echo ""
    echo "Your users:"
    echo "  - nicolas.desaintromain@axa.com"
    echo "  - alice.jin@axa-uk.co.uk"
    echo "  - josep-oriol.ayats@axa.com"
    echo "  - wolfgang.sachsenhofer@axa.ch"
    echo "  - clarisse.montmaneix@axaxl.com"
    echo "  - adwaith.nair@axa.com"
    echo ""
    echo "All passwords: 123"
    echo ""
else
    echo ""
    echo "Please create a GitHub repository first:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named 'startup-swiper'"
    echo "3. Run this script again"
fi
