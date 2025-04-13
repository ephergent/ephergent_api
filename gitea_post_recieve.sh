#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

# Configuration
ENV_CONFIG_FILE="/etc/ephergent/build.env"
REPO_DIR="/srv/git/ephergent/ephergent_api.git"
WORKING_DIR="/srv/ephergent_api"
VENV_DIR="$WORKING_DIR/venv"
LOG_FILE="/var/log/ephergent/deploy.log"
SERVICE_NAME="ephergent-api.service"
GIT_BRANCH="main"
APP_USER="ephergent"
APP_GROUP="ephergent"

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo chown git:git "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chown git:git "$LOG_FILE"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a "$LOG_FILE"
}

log "Starting deployment..."

# Source environment variables
if [ -f "$ENV_CONFIG_FILE" ]; then
    log "Sourcing environment from $ENV_CONFIG_FILE"
    set -a
    source "$ENV_CONFIG_FILE"
    set +a
else
    log "ERROR: Build environment file $ENV_CONFIG_FILE not found!"
    exit 1
fi

# Ensure working directory exists
if [ ! -d "$WORKING_DIR" ]; then
    log "Creating working directory: $WORKING_DIR"
    sudo mkdir -p "$WORKING_DIR"
    sudo chown $APP_USER:$APP_GROUP "$WORKING_DIR"
fi

# Deploy code
if [ ! -d "$WORKING_DIR/.git" ]; then
    # First-time deployment
    log "Initial deployment - cloning repository"
    sudo -u $APP_USER git clone --depth 1 --branch "$GIT_BRANCH" "$REPO_DIR" "$WORKING_DIR"
else
    # Update existing deployment
    log "Updating existing deployment"
    cd "$WORKING_DIR"
    sudo -u $APP_USER git fetch origin "$GIT_BRANCH"
    sudo -u $APP_USER git reset --hard "origin/$GIT_BRANCH"
    sudo -u $APP_USER git clean -fdx
fi

# Create/update virtual environment
cd "$WORKING_DIR"
if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment"
    sudo -u $APP_USER python3 -m venv "$VENV_DIR"
fi

# Install dependencies
log "Installing dependencies"
sudo -u $APP_USER bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Set up environment file for the application
log "Setting up application environment"
sudo cp "$ENV_CONFIG_FILE" "$WORKING_DIR/.env"
sudo chown $APP_USER:$APP_GROUP "$WORKING_DIR/.env"
sudo chmod 640 "$WORKING_DIR/.env"

# Set permissions using the wrapper script
log "Setting permissions"
sudo /usr/local/bin/set-ephergent-permissions.sh
sudo chown -R $APP_USER:$APP_GROUP "$WORKING_DIR"

# Restart service
log "Restarting $SERVICE_NAME"
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl restart "$SERVICE_NAME"
else
    sudo systemctl start "$SERVICE_NAME"
fi

# Verify service status
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    log "Service $SERVICE_NAME started successfully"
else
    log "ERROR: Service $SERVICE_NAME failed to start"
    exit 1
fi

log "Deployment completed successfully"
exit 0