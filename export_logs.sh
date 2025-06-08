#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Get the actual user who ran sudo (if script is run with sudo)
if [ -n "$SUDO_USER" ]; then
    REAL_USER="$SUDO_USER"
else
    REAL_USER="$USER"
fi

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Create timestamped directory for this export
EXPORT_DIR="$LOG_DIR/$TIMESTAMP"
mkdir -p "$EXPORT_DIR"

# Function to safely copy log files
copy_log() {
    local src="$1"
    local dest="$2"
    if [ -f "$src" ]; then
        cp "$src" "$dest"
        echo "Copied $src to $dest"
    fi
}

echo "Exporting VFIO logs to $EXPORT_DIR"

# Copy all VFIO-related logs
copy_log "/tmp/vfio-processes-before.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-processes-after.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-nvidia-processes.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-amd-processes.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-remaining-modules.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-teardown.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-teardown-nvidia.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-teardown-dri.log" "$EXPORT_DIR/"
copy_log "/tmp/vfio-teardown-loaded-modules.log" "$EXPORT_DIR/"

# Create a dmesg log for additional context
dmesg | grep -i -E "vfio|nvidia|amd|gpu" > "$EXPORT_DIR/dmesg_gpu.log"

# Change ownership of the entire logs directory to the real user
chown -R "$REAL_USER:$REAL_USER" "$LOG_DIR"

echo "Logs exported to $EXPORT_DIR"
echo "Log directory ownership changed to $REAL_USER"

# List exported files
echo -e "\nExported files:"
ls -lh "$EXPORT_DIR"
