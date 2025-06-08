#!/usr/bin/env python3
import sys
import os
import re
import shutil
from pathlib import Path

def count_vms(content):
    """Count number of VMs in the if condition"""
    pattern = r'\$OBJECT == "([^"]*)"'
    return len(re.findall(pattern, content))

def disable_all_vms(content):
    """Replace all VM conditions with __no_vm_specified"""
    pattern = r'if \[\[(.*?)\]\];'
    match = re.search(pattern, content)
    if match:
        return re.sub(pattern, 'if [[ $OBJECT == "__no_vm_specified" ]];', content)
    return content

def disable_single_vm(content, vmname):
    """Remove specific VM from the conditions"""
    # Pattern to match the entire if condition
    pattern = r'if \[\[(.*?)\]\];'
    match = re.search(pattern, content)
    if not match:
        return None

    condition = match.group(1)
    vm_count = count_vms(content)

    if vm_count == 1:
        # If this is the last VM, replace with placeholder
        return re.sub(pattern, 'if [[ $OBJECT == "__no_vm_specified" ]];', content)
    
    # Remove the specific VM condition
    if vm_count == 2:
        # If there are two VMs, remove the || part and simplify
        pattern = r'\$OBJECT == "' + re.escape(vmname) + r'" \|\| '
        new_condition = re.sub(pattern, '', condition)
        if new_condition == condition:  # VM was second part
            pattern = r' \|\| \$OBJECT == "' + re.escape(vmname) + r'"'
            new_condition = re.sub(pattern, '', condition)
    else:
        # Remove the VM condition and cleanup
        pattern = r'\$OBJECT == "' + re.escape(vmname) + r'" \|\| '
        new_condition = re.sub(pattern, '', condition)
        if new_condition == condition:  # VM wasn't at start
            pattern = r' \|\| \$OBJECT == "' + re.escape(vmname) + r'"'
            new_condition = re.sub(pattern, '', condition)

    return re.sub(r'if \[\[(.*?)\]\];', f'if [{new_condition}];', content)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <vmname|--all>")
        sys.exit(1)

    if os.geteuid() != 0:
        print(f"Please run as root (sudo {sys.argv[0]} {sys.argv[1]})")
        sys.exit(1)

    hooks_file = Path("/etc/libvirt/hooks/qemu")

    if not hooks_file.exists():
        print(f"Error: Hooks file {hooks_file} not found")
        sys.exit(1)

    # Create backup
    backup_file = hooks_file.with_suffix(".bak")
    shutil.copy2(hooks_file, backup_file)

    # Read current content
    content = hooks_file.read_text()

    if sys.argv[1] == "--all":
        new_content = disable_all_vms(content)
        action_msg = "all VMs"
    else:
        vmname = sys.argv[1]
        if f'$OBJECT == "{vmname}"' not in content:
            print(f"VM {vmname} not found in hooks")
            sys.exit(0)
        new_content = disable_single_vm(content, vmname)
        action_msg = f"VM: {vmname}"

    if new_content is None:
        print("Error: Could not find if statement in hooks file")
        sys.exit(1)

    try:
        # Write changes
        hooks_file.write_text(new_content)
        print(f"Successfully disabled hooks for {action_msg}")
        print(f"Backup created at: {backup_file}")
    except Exception as e:
        print(f"Error writing to {hooks_file}: {e}")
        # Restore backup on error
        shutil.copy2(backup_file, hooks_file)
        sys.exit(1)

if __name__ == "__main__":
    main()
