#!/bin/bash
set -e

# Remember to delete /srv/ephergent_api before pushing...

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
    git clone --depth 1 --branch "$GIT_BRANCH" "$REPO_DIR" "$WORKING_DIR"
else
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

# Fix permissions - critical step
sudo chown -R ephergent:ephergent "$WORKING_DIR"
sudo find "$WORKING_DIR" -type d -exec chmod 750 {} \;
sudo find "$WORKING_DIR" -type f -exec chmod 640 {} \;
sudo find "$VENV_DIR/bin" -type f -exec chmod 750 {} \;

# Restart service
if command -v systemctl &> /dev/null; then
    sudo systemctl restart ephergent-api.service
fi

echo "Deployment completed"
exit 0
