#!/bin/bash

# Source environment variables for the build/deploy process
# This file should contain secrets like API_SECRET, MAILGUN_API_KEY etc.
# AND configuration like FLASK_CONFIG=prod, FLASK_DEBUG=0
ENV_CONFIG_FILE="/etc/ephergent/build.env"
if [ -f "$ENV_CONFIG_FILE" ]; then
  echo "Sourcing ephergent build environment variables from $ENV_CONFIG_FILE..."
  # Source variables into the script's environment
  set -a # Automatically export all variables subsequently defined or modified
  source "$ENV_CONFIG_FILE"
  set +a # Stop automatically exporting
else
  echo "ERROR: Build environment file $ENV_CONFIG_FILE not found!" >&2
  exit 1
fi

# Define paths
REPO_DIR="/srv/git/ephergent/ephergent_api.git" # Gitea's bare repo path
WORKING_DIR="/srv/ephergent_api"              # Where the code will be checked out
VENV_DIR="$WORKING_DIR/venv"                  # Path to the virtual environment
LOG_FILE="/home/git/ephergent_api_build.log"  # Log file for the hook script
SERVICE_NAME="ephergent-api.service"          # Name of the systemd service

# --- Logging Function ---
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# --- Main Script ---
log "Starting post-receive hook..."

# Ensure log file directory exists (adjust path/user as needed)
mkdir -p "$(dirname "$LOG_FILE")"
chown git:git "$(dirname "$LOG_FILE")" || log "Warning: Could not chown log directory."
touch "$LOG_FILE"
chown git:git "$LOG_FILE" || log "Warning: Could not chown log file."

# Clean approach: Remove and recreate working directory each time
log "Removing old working directory: $WORKING_DIR"
rm -rf "$WORKING_DIR" >> "$LOG_FILE" 2>&1
log "Creating new working directory: $WORKING_DIR"
mkdir -p "$WORKING_DIR" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Failed to create working directory $WORKING_DIR"
    exit 1
fi

log "Cloning repository from $REPO_DIR to $WORKING_DIR"
# Use --depth 1 for faster clones if history isn't needed for deployment
git clone --depth 1 "$REPO_DIR" "$WORKING_DIR" >> "$LOG_FILE" 2>&1

# Check if clone was successful by looking for a common file/dir
if [ ! -f "$WORKING_DIR/app.py" ]; then
    log "ERROR: Failed to clone repository into $WORKING_DIR"
    exit 1
fi
log "Repository cloned successfully."

cd "$WORKING_DIR" || { log "ERROR: Failed to cd into $WORKING_DIR"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to create virtual environment."
        exit 1
    fi
else
    log "Virtual environment already exists in $VENV_DIR"
fi

# Activate the virtual environment
log "Activating virtual environment."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    log "ERROR: Failed to activate virtual environment."
    # Attempt to deactivate just in case it partially activated
    deactivate > /dev/null 2>&1
    exit 1
fi

# Install/Upgrade dependencies
log "Installing/updating requirements from requirements.txt"
pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Failed to install requirements."
    deactivate
    exit 1
fi
log "Requirements installed successfully."

# Deactivate virtual environment (no longer needed for the script itself)
deactivate
log "Deactivated virtual environment."

# Copy the central configuration to the .env file the app uses
log "Copying $ENV_CONFIG_FILE to $WORKING_DIR/.env"
cp "$ENV_CONFIG_FILE" "$WORKING_DIR/.env" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Failed to copy environment configuration."
    exit 1
fi
# Ensure the .env file has appropriate permissions (readable by the app user)
# Adjust owner/group as necessary (e.g., www-data, or a dedicated app user like 'ephergent')
# Example: chown ephergent:ephergent "$WORKING_DIR/.env"
# Example: chmod 600 "$WORKING_DIR/.env" # Restrict permissions if needed
log "Setting ownership and permissions for $WORKING_DIR"
# Set ownership to the user/group defined in the systemd service file
chown -R ephergent:ephergent "$WORKING_DIR" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set ownership for $WORKING_DIR"
# Set appropriate permissions (adjust as needed for security)
chmod -R 750 "$WORKING_DIR" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set permissions for $WORKING_DIR"
chmod 640 "$WORKING_DIR/.env" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set permissions for .env file"


# Restart the application service using systemd
# IMPORTANT: The user running this script (e.g., 'git') needs passwordless sudo rights
#            for 'systemctl restart $SERVICE_NAME'.
#            Configure this via 'sudo visudo' or a file in /etc/sudoers.d/
#            Example entry in sudoers:
#            git ALL=(ALL) NOPASSWD: /bin/systemctl restart ephergent-api.service
log "Attempting to restart the application service: $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Failed to restart $SERVICE_NAME. Check sudo permissions and service status."
    # Decide if this is a fatal error for the hook
    # exit 1
else
    log "Service $SERVICE_NAME restarted successfully."
fi

log "Post-receive hook completed successfully."
exit 0
