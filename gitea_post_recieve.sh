# Source environment variables
if [ -f /etc/ephergent/build.env ]; then
  echo "Sourcing ephergent build environment variables..."
  source /etc/ephergent/build.env
else
  echo "ERROR: Build environment file /etc/ephergent/build.env not found!" >&2
  # Optionally exit if the file is critical
  # exit 1
fi

# Define paths
REPO_DIR="/srv/git/ephergent/ephergent_api.git" 
WORKING_DIR="/srv/ephergent_api"
VENV_DIR="/srv/ephergent_api/venv"
LOG_FILE="/home/git/ephergent_api_build.log"

echo "Starting post-receive hook at $(date)" >> "$LOG_FILE" 2>&1

# Clean approach: Remove and recreate working directory each time
rm -rf "$WORKING_DIR"
mkdir -p "$WORKING_DIR"
git clone "$REPO_DIR" "$WORKING_DIR" >> "$LOG_FILE" 2>&1

# Check if clone was successful
if [ ! -d "$WORKING_DIR/.git" ]; then
    echo "ERROR: Failed to clone repository" >> "$LOG_FILE" 2>&1
    exit 1
fi

cd "$WORKING_DIR" || exit 1

# Ensure API_SECRET is loaded (optional check)
if [ -z "$API_SECRET" ]; then
    echo "ERROR: API_SECRET is not set after sourcing env file!" >&2
    # exit 1
fi

# Activate the virtual environment and install requirements
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt
deactivate


echo "Post-receive hook completed at $(date)" >> "$LOG_FILE" 2>&1
exit 0
