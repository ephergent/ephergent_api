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
WORKING_DIR="/srv/ephergent_api"              # Where the code is checked out (MUST exist and be owned by user running script)
VENV_DIR="$WORKING_DIR/venv"                  # Path to the virtual environment
LOG_FILE="/home/git/ephergent_api_build.log"  # Log file for the hook script
SERVICE_NAME="ephergent-api.service"          # Name of the systemd service
GIT_BRANCH="main"                             # Or "master", or detect dynamically if needed

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

# --- Deployment Steps ---

# Navigate to the working directory (should already exist and be owned by 'git')
log "Changing to working directory: $WORKING_DIR"
cd "$WORKING_DIR" || { log "ERROR: Failed to cd into $WORKING_DIR. Ensure it exists and the 'git' user has permissions."; exit 1; }

# Check if this is a git repository. If not, clone into it.
if [ ! -d ".git" ]; then
    log "Working directory is not a git repository. Cloning..."
    # Clone into the current directory (.)
    # Clean out the directory first in case there are leftover files
    rm -rf ./* ./.??* >> "$LOG_FILE" 2>&1 # Remove existing files/hidden files (be careful with this)
    git clone --depth 1 --branch "$GIT_BRANCH" "$REPO_DIR" . >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to clone repository into existing directory $WORKING_DIR"
        exit 1
    fi
    log "Repository cloned successfully."
else
    log "Working directory is a git repository. Fetching and resetting..."
    # Ensure remote is set correctly (usually 'origin')
    git remote set-url origin "$REPO_DIR" >> "$LOG_FILE" 2>&1

    # Fetch the latest changes from the bare repository
    git fetch origin "$GIT_BRANCH" --depth 1 >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to fetch from origin."
        # Attempt to continue, maybe reset works
    fi

    # Reset the local repository to match the fetched branch HEAD
    # This overwrites local changes and unstaged files
    log "Resetting repository to origin/$GIT_BRANCH"
    git reset --hard "origin/$GIT_BRANCH" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to reset repository."
        exit 1
    fi

    # Clean untracked files and directories (-d for directories, -f for files, -x to ignore .gitignore rules)
    # Use -f twice (-ff) if you really want to force cleaning even nested git repos (usually not needed/dangerous)
    log "Cleaning untracked files and directories..."
    git clean -fdx >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "Warning: git clean command failed."
    fi
    log "Repository updated and cleaned."
fi


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

# Set ownership and permissions for the application files
# This ensures the user running the app (ephergent) can read/execute files
log "Setting ownership and permissions for $WORKING_DIR"
# Set ownership to the user/group defined in the systemd service file
# Use -R for recursive operation
#sudo chown -R ephergent:ephergent "$WORKING_DIR" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set ownership for $WORKING_DIR"
# Set appropriate permissions (adjust as needed for security)
# Example: Directories 750 (rwxr-x---), Files 640 (rw-r-----)
# Find directories and set permissions
#sudo find "$WORKING_DIR" -type d -exec chmod 750 {} \; >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set directory permissions"
# Find files and set permissions
#sudo find "$WORKING_DIR" -type f -exec chmod 640 {} \; >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set file permissions"
# Ensure the .env file is readable by the app user but not others
#sudo chmod 640 "$WORKING_DIR/.env" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set permissions for .env file"
# Ensure the gunicorn executable in venv is executable by the app user
#if [ -f "$VENV_DIR/bin/gunicorn" ]; then
#    sudo chmod u+x "$VENV_DIR/bin/gunicorn" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set execute permission on gunicorn"
#fi
# Ensure python in venv is executable
#if [ -f "$VENV_DIR/bin/python" ]; then
#    sudo chmod u+x "$VENV_DIR/bin/python" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set execute permission on python"
#fi
# Ensure activate script is executable if needed (though usually sourced, not executed directly by app)
#if [ -f "$VENV_DIR/bin/activate" ]; then
#    sudo chmod u+x "$VENV_DIR/bin/activate" >> "$LOG_FILE" 2>&1 || log "Warning: Failed to set execute permission on activate script"
#fi


# Restart the application service using systemd
# IMPORTANT: The user running this script (e.g., 'git') needs passwordless sudo rights
#            for 'systemctl restart $SERVICE_NAME' AND for the chown/chmod commands above.
#            Configure this via 'sudo visudo' or a file in /etc/sudoers.d/
#            Example entry in sudoers:
#            git ALL=(ALL) NOPASSWD: /bin/systemctl restart ephergent-api.service, /bin/chown, /bin/chmod, /usr/bin/find
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
