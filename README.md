# VFIO Scripts

A collection of scripts for managing single GPU passthrough using VFIO, allowing you to use your GPU in virtual machines.

Notice that this repository by itself does not aim for being a guide. Instead, you should check credits and acknowledgements section for that.

The tutorial below assumes you have knowledge on this topic.

## Features

- Single GPU Passthrough support
- Automated handling of display manager and GPU drivers
- Support for both NVIDIA and AMD GPUs
- Logging of operations for debugging
- Support for systemd and runit init systems
- Hooks integration with libvirt

## Components

- `qemu`: Hook script that manages VM lifecycle events (prepare/release)
- `vfio-startup`: Handles unbinding GPU from host system (stops display manager, unloads GPU drivers)
- `vfio-teardown`: Restores GPU to host system (reloads GPU drivers, restarts display manager)

## Installation

1. Clone this repository
2. Run the installation script as root:
   ```bash
   sudo ./install.sh
   ```

The install script will:
- Copy vfio-startup and vfio-teardown to /usr/local/bin/
- Install qemu hook to /etc/libvirt/hooks/qemu (if not already present)
- Set appropriate executable permissions

After installing the hook, to enable it for your vm use:

```bash
sudo ./enable-hooks.py VM-NAME-HERE
```

Disabling hooks:
```bash
sudo ./disable-hooks.py VM-NAME-HERE
sudo ./disable-hooks.py --all # disables all hooks

# Note that this will still have hook for a VM named "__no_vm_specified"
# I don't know the possibility and reason of that name being ever used for a VM
# but keep this in your mind.
```

Troubleshooting:
```bash
sudo ./export_logs.sh
# Exports logs to ./logs 
```



## Usage
To have single GPU passthrough

1) Make sure IOMMU is enabled on your system.
2) Make sure your VBIOS supports GPU passthrough. If not, [patch it](https://github.com/QaidVoid/Complete-Single-GPU-Passthrough?tab=readme-ov-file#vbios-patching)
3) Create a VM using virtual machine manager, __Make sure to use UEFI.__
4) Setup the VM normally, __DO NOT INSTALL ANY GUEST TOOLS__.
5) After you finish setting it up, remove the components that emulate graphics and display.
6) [Harden your VM] to make it look like a normal machine for drivers(https://github.com/QaidVoid/Complete-Single-GPU-Passthrough?tab=readme-ov-file#video-card-driver-virtualisation-detection)
7) Add USB devices
8) Add all PCI devices from your GPU's IOMMU group.

9) After setting up the VM, use 
```bash
sudo ./enable-hooks.py VM-NAME-HERE
```


## Requirements

- libvirt
- QEMU/KVM
- A GPU compatible with VFIO passthrough
- A Linux system with systemd or runit
- Python 3.9+

## Tested with
Arch Linux on KDE Plasma 6 with Nvidia 3060


## License

For the linux community! With all respect to original authors of these scripts.


VFIO hook scripts are not originally made by me. I combined and slightly modified them to get single gpu passthrough with KDE Plasma working functionally as originally I was having problems. 

Credits:
- https://gitlab.com/risingprismtv/single-gpu-passthrough     
- https://github.com/ledisthebest/LEDs-single-gpu-passthrough

Acknowledgements:
- https://docs.vrchat.com/docs/using-vrchat-in-a-virtual-machine for VM hardening
- https://github.com/QaidVoid/Complete-Single-GPU-Passthrough

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.


