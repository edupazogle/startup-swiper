#!/bin/bash
# Setup GitHub Secrets for Deployment
# Run this script to get the values needed for GitHub Secrets

set -e

echo "🔐 GitHub Secrets Setup Helper"
echo "==============================="
echo ""
echo "You need to add these secrets to your GitHub repository:"
echo ""
echo "📍 Go to: Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo "---"
echo ""

# DO_SSH_PRIVATE_KEY
echo "1️⃣  DO_SSH_PRIVATE_KEY"
echo "   Name: DO_SSH_PRIVATE_KEY"
echo "   Value: (Copy the ENTIRE output below, including BEGIN and END lines)"
echo ""
if [ -f ~/.ssh/id_rsa ]; then
    cat ~/.ssh/id_rsa
    echo ""
else
    echo "   ⚠️  No SSH key found at ~/.ssh/id_rsa"
    echo "   Generate one with: ssh-keygen -t rsa -b 4096"
    echo ""
fi

echo "---"
echo ""

# DO_HOST
echo "2️⃣  DO_HOST"
echo "   Name: DO_HOST"
echo "   Value: tilyn.ai"
echo ""

echo "---"
echo ""

# DO_USER
echo "3️⃣  DO_USER"
echo "   Name: DO_USER"
echo "   Value: root"
echo ""

echo "---"
echo ""
echo "✅ Once you've added all secrets, push to main branch to trigger deployment!"
echo ""
echo "📚 For more info, see: .github/DEPLOYMENT.md"
