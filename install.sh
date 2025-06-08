#!/bin/bash

set -e # Exit on error

# Create libvirt hooks directory if it doesn't exist
HOOK_DIR="/etc/libvirt/hooks"
mkdir -p "$HOOK_DIR"
# Check if the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Use sudo."
    exit 1
fi
# Define the source and destination directories
SOURCE_DIR="$(dirname "$(realpath "$0")")"
DEST_DIR="/usr/local/bin"

# Copy qemu hook if it doesn't already exist
if [ -f "$HOOK_DIR/qemu" ]; then
    echo "qemu hook already exists in $HOOK_DIR, skipping..."
else
    if [ -f "$SOURCE_DIR/qemu" ]; then
        cp "$SOURCE_DIR/qemu" "$HOOK_DIR/qemu"
        chmod +x "$HOOK_DIR/qemu"
        echo "Moved and made executable: qemu hook"
    else
        echo "File not found: $SOURCE_DIR/qemu"
    fi
fi

# Define the files to be moved
FILES=("vfio-startup" "vfio-teardown")
# copy files to /usr/local/bin 
for file in "${FILES[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$DEST_DIR/"
        chmod +x "$DEST_DIR/$file"
        echo "Moved and made executable: $file"
    else
        echo "File not found: $SOURCE_DIR/$file"
    fi
done
