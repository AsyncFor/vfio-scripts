#!/usr/bin/env python3
import sys
import os
import re
import shutil
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <vmname>")
        sys.exit(1)

    if os.geteuid() != 0:
        print(f"Please run as root (sudo {sys.argv[0]} {sys.argv[1]})")
        sys.exit(1)

    vmname = sys.argv[1]
    hooks_file = Path("/etc/libvirt/hooks/qemu")

    if not hooks_file.exists():
        print(f"Error: Hooks file {hooks_file} not found")
        sys.exit(1)

    # Create backup
    backup_file = hooks_file.with_suffix(".bak")
    shutil.copy2(hooks_file, backup_file)

    # Read current content
    content = hooks_file.read_text()

    # Check if VM already exists in hooks
    if f'$OBJECT == "{vmname}"' in content:
        print(f"VM {vmname} already exists in hooks")
        sys.exit(0)

    # Find first if statement
    pattern = r'if \[\[ \$OBJECT == "([^"]*)" \]\];'
    match = re.search(pattern, content)
    
    if match:
        current_vm = match.group(1)
        if current_vm == '__no_vm_specified':
            # Replace the placeholder with our VM
            new_content = re.sub(pattern, f'if [[ $OBJECT == "{vmname}" ]];', content)
        else:
            # Add our VM to the condition
            new_content = re.sub(pattern, f'if [[ $OBJECT == "{current_vm}" || $OBJECT == "{vmname}" ]];', content)
    else:
        print("Error: Could not find if statement in hooks file")
        sys.exit(1)

    try:
        # Write changes
        hooks_file.write_text(new_content)
        print(f"Successfully enabled hooks for VM: {vmname}")
        print(f"Backup created at: {backup_file}")
    except Exception as e:
        print(f"Error writing to {hooks_file}: {e}")
        # Restore backup on error
        shutil.copy2(backup_file, hooks_file)
        sys.exit(1)

if __name__ == "__main__":
    main()
