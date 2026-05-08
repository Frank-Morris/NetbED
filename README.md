# NetbED: Automated Cybersecurity Lab Deployer

**Francis Morris · B00386292 · BEng (Hons) Cyber Security · University of the West of Scotland · 2026**

NetbED is a portable, automated cybersecurity lab deployer that provisions a fully configured five-node virtualised enterprise network through a graphical user interface (GUI). No command-line interaction or manual configuration is required but is possible. It is intended for cybersecurity students, researchers and security professionals who require a consistent, reproducible and isolated lab environment for security testing and practice.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Launching NetbED](#launching-netbed)
- [Using the GUI](#using-the-gui)
- [Accessing the Virtual Machines](#accessing-the-virtual-machines)
- [Network Topology](#network-topology)
- [Troubleshooting](#troubleshooting)
- [Known Issues & Limitations](#known-issues--limitations)

---

## System Requirements

| Requirement | Minimum Specification |
|---|---|
| Operating System | Windows 10 x86-64 |
| Processor | x86-64 architecture (Intel or AMD) |
| RAM | 16 GB |
| Storage | 106 GB free disk space |
| Virtualisation | VT-x or AMD-V enabled in BIOS |

> **Note:** ARM architecture (Apple M-series) is **not** supported. NetbED must be run on an x86-64 machine. This is a hard constraint due to the pfSense Vagrant box only being available for x86-64.

---

## Prerequisites

All software listed below is free and open source.

### 1. Oracle VirtualBox

1. Go to https://www.virtualbox.org/wiki/Downloads
2. Download the installer for your operating system
3. Run the installer and accept all default settings
4. Restart your machine after installation

### 2. HashiCorp Vagrant

1. Go to https://developer.hashicorp.com/vagrant/downloads
2. Download the installer for your operating system
3. Run the installer and accept all default settings
4. Open a Command Prompt and verify installation:
vagrant --version

You should see a version number. If you see an error, restart your machine and try again.

### 3. vagrant-reload Plugin

Open a Command Prompt and run:
vagrant plugin install vagrant-reload

### 4. Python 3

1. Go to https://www.python.org/downloads/
2. Download the latest Python 3 installer
3. Run the installer — **tick "Add Python to PATH"** before clicking Install

Verify installation:
python --version

Tkinter comes pre-installed with Python and does not require a separate installation step.

---

## Installation

1. Download or clone the NetbED project folder to your machine
2. Place the folder somewhere accessible, for example your Desktop or Documents folder
3. The project folder should contain the following:
```text
NetbED/
├── Vagrantfile
├── main.py
├── pfsense_config.xml
├── README.md
├── Ansible/
│   ├── attacker.yml
│   └── web-server.yml
└── Scripts/
├── dc_hostname.ps1
├── dc_ipconfig.ps1
├── hostname.ps1
└── ipconfig.ps1
```
> **Note:** If any of these files are missing the application will not function correctly.

---

## Launching NetbED

1. Open a Command Prompt
2. Navigate to the NetbED project folder:
cd C:\Users\YourName\Desktop\NetbED

3. Launch the application:
python main.py

The NetbED control panel will open.

---

## Using the GUI

### Overview of the Control Panel

- **Configure Nodes** - opens the node selection window
- **Start Lab** - deploys the selected nodes
- **Suspend Lab** - saves the running memory state of the selected nodes to disk
- **Resume Lab** - restores selected nodes from a suspended state without re-provisioning
- **Delete Lab** - permanently removes the selected nodes
- **Create Snapshot** - saves the current state of a running machine with a named snapshot
- **Restore Snapshot** - restores a machine to a previously saved snapshot
- **Snapshot listbox** - displays saved snapshot names for the current session
- **Console Output window** - streams live Vagrant output during deployment

---

### Selecting Nodes

By default, all nodes deploy when you click Start Lab. To select specific nodes:

1. Click **Configure Nodes**
2. A popup window will appear showing all five nodes:
   - pfSense *(selected by default - required for all deployments)*
   - Domain Controller
   - Windows Client
   - Kali Linux
   - Web Server
3. Tick the nodes you want to deploy
4. Click **Confirm**

> **Note:** pfSense must always be selected. It acts as the central gateway and firewall for all other nodes.

---

### Deploying the Lab

1. Select your desired nodes using **Configure Nodes**
2. Click **Start Lab**
3. The console output window will begin streaming live deployment progress
4. All buttons are disabled during deployment to prevent conflicts
5. Full five-node deployment typically takes **15–30 minutes** depending on hardware and internet connection speed
6. On first run, Vagrant will download the box images from the internet. Subsequent deployments use locally cached boxes and will be significantly faster
7. When deployment is complete the console displays a completion message and all buttons re-enable

---

### Suspending and Resuming the Lab

Suspend saves the full running memory state of each machine to disk, allowing them to be resumed exactly where they left off without re-provisioning.

**To suspend:**
1. Select nodes using **Configure Nodes**
2. Click **Suspend Lab**

**To resume:**
1. Select the same nodes using **Configure Nodes**
2. Click **Resume Lab**
3. Machines return to their running state without re-provisioning and all network configuration is preserved

---

### Deleting the Lab

1. Select the nodes you want to delete using **Configure Nodes**
2. Click **Delete Lab**
3. A confirmation dialog will appear - click **Yes** to proceed

> **Warning:** This action cannot be undone. Use snapshots to save state before deleting.

---

### Creating a Snapshot

1. Ensure the machine you want to snapshot is running
2. Click **Create Snapshot**
3. Enter a name for the snapshot when prompted and click **OK**
4. The snapshot name will appear in the listbox

> **Note:** Snapshot functionality is currently limited to one node at a time. If no node is selected, the snapshot defaults to all active machines.

---

### Restoring a Snapshot

1. Select the snapshot name from the listbox
2. Click **Restore Snapshot**

> **Note:** Snapshot names in the listbox are cleared when the application is restarted. The snapshots themselves remain saved in VirtualBox Manager and are accessible there after a restart.

---

## Accessing the Virtual Machines

Access each machine through VirtualBox Manager by double-clicking the machine you want to open:

**Username**: Vagrant

**Password**: Vagrant

>**Note:** This is the username and Password for all Virtual Machines.

For the Linux nodes you can also SSH in from the project directory:
vagrant ssh attacker,
vagrant ssh web-server

---

## Network Topology

NetbED provisions a simulated enterprise network segmented across three isolated internal networks, all routed through pfSense. The attacker cannot reach the LAN directly - all traffic must pass through pfSense where firewall rules enforce the boundaries.

| Node | Operating System | IP Address | Role |
|---|---|---|---|
| pfSense | FreeBSD | LAN: 10.0.1.1 · DMZ: 10.0.4.1 · Attacker: 10.0.3.1 | Firewall and central gateway |
| Domain Controller | Windows Server 2016 | 10.0.1.2 | DNS server and domain controller |
| Windows Client | Windows 10 | 10.0.1.3 | Corporate endpoint |
| Web Server | Ubuntu 22.04 | 10.0.4.2 | DMZ web server running Apache |
| Kali Linux | Kali Linux Rolling | 10.0.3.2 | Attacker node |

**Firewall rules:**

| Traffic | Rule |
|---|---|
| LAN → Internet | Permitted via pfSense NAT |
| Attacker → DMZ (web server) | Permitted |
| Attacker → LAN | **Blocked** |
| DMZ → LAN | **Blocked** |

---

## Troubleshooting

| Issue | Likely Cause | Resolution |
| :--- | :--- | :--- |
| `Start Lab / vagrant up` fails immediately | Vagrant or VirtualBox not installed correctly | Reinstall both and ensure the `vagrant-reload` plugin is installed |
| Machines time out during provisioning | Insufficient RAM on host | Click Start Lab again, Vagrant will resume from where it failed, Close other applications to free memory and retry |
| Python not found | Python not added to PATH | Reinstall Python and tick **Add Python to PATH** |
| GUI does not open | Python not installed or wrong version | Verify with `python --version` |
| Snapshot names missing after restart | Listbox is cleared on application restart | Snapshots are still in VirtualBox Manager |
| Deployment fails mid-way through | Box download interrupted | Click `Start Lab` again, Vagrant will resume from where it failed |
| Deployment conflict after `Delete Lab / vagrant destroy` | VirtualBox VM folder persisted on disk | Manually delete the leftover VM folder from your VirtualBox VMs directory, then retry |

---

## Known Issues & Limitations

**ARM architecture not supported**
The pfSense Vagrant box is only available for x86-64 architecture. This is a hard constraint — there is currently no arm64-compatible pfSense box available on the Vagrant Cloud.

**Active Directory domain promotion not implemented**
The Domain Controller is provisioned with DNS configuration as foundational infrastructure. Full scripted domain promotion and Windows Client domain join are not yet implemented and remain a planned future enhancement.

**Snapshot listbox does not persist between application restarts**
Snapshot names are held in memory only and are cleared when NetbED is closed. The snapshots themselves remain saved in VirtualBox Manager and are accessible there, but cannot be restored through the NetbED interface after a restart without manually re-entering the snapshot name.

**VirtualBox VM folders can persist after `Delete Lab / agrant destroy`**
In some cases VirtualBox VM folders are not fully removed after `vagrant destroy` completes. If a subsequent deployment fails with a naming conflict, manually delete the leftover folder from your VirtualBox VMs directory before retrying.

---

*NetbED — Francis Morris · B00386292 · BEng (Hons) Cyber Security · University of the West of Scotland · 2026*.
