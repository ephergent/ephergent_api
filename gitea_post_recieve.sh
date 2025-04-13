#!/bin/bash
set -e

# Configuration
ENV_CONFIG_FILE="/etc/ephergent/build.env"
REPO_DIR="/srv/git/ephergent/ephergent_api.git"
WORKING_DIR="/srv/ephergent_api"
VENV_DIR="$WORKING_DIR/venv"
GIT_BRANCH="main"

echo "Starting deployment..."

# Source environment variables
if [ -f "$ENV_CONFIG_FILE" ]; then
    source "$ENV_CONFIG_FILE"
else
    echo "ERROR: Build environment file not found!"
    exit 1
fi

# Deploy code
if [ ! -d "$WORKING_DIR/.git" ]; then
    # First-time deployment
    git clone --depth 1 --branch "$GIT_BRANCH" "$REPO_DIR" "$WORKING_DIR"
else
    # Update existing deployment
    cd "$WORKING_DIR"
    git fetch origin "$GIT_BRANCH"
    git reset --hard "origin/$GIT_BRANCH"
    git clean -fdx
fi

# Create/update virtual environment
cd "$WORKING_DIR"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Install dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Set up environment file
cp "$ENV_CONFIG_FILE" "$WORKING_DIR/.env"

# Restart service (if git has permission to use systemctl)
if command -v systemctl &> /dev/null && systemctl list-units --type=service | grep -q "ephergent-api"; then
    systemctl restart ephergent-api.service || echo "Could not restart service - manual restart required"
else
    echo "Service needs to be restarted manually"
fi

echo "Deployment completed"
exit 0