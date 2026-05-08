# NetbED - Technical Documentation

**Author:** Francis Morris  
**Student ID:** B00386292  
**Programme:** BEng (Hons) Cyber Security  
**University of the West of Scotland · 2026**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Project Structure](#3-project-structure)
4. [Development Environment](#4-development-environment)
5. [Prerequisites and Dependencies](#5-prerequisites-and-dependencies)
6. [Node Reference](#6-node-reference)
7. [Vagrantfile Reference](#7-vagrantfile-reference)
8. [Firewall Configuration](#8-firewall-configuration)
9. [Provisioning Scripts Reference](#9-provisioning-scripts-reference)
10. [Engineering Challenges](#10-engineering-challenges)
11. [Known Issues and Limitations](#11-known-issues-and-limitations)
12. [Future Development](#12-future-development)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Introduction

This document provides a comprehensive technical reference for the NetbED artefact. It covers the full system architecture, project structure, configuration of all five nodes, provisioning scripts, engineering decisions made during development, known limitations and future development plans. It is intended for developers, contributors or technically able users who want to understand how the system works under the hood rather than just how to use it.

NetbED is a portable automated cybersecurity lab deployer that provisions a five-node simulated enterprise network on a local x86 host machine using a combination of Vagrant for orchestration, Ansible for Linux node configuration, PowerShell for Windows node configuration, pfSense for network segmentation and firewall enforcement, and Python with Tkinter for the graphical user interface.

---

## 2. System Architecture

### 2.1 Three Tier Model

NetbED is built around a three-tier architecture model, separating concerns across three distinct layers.

| Tier | Component | Responsibility |
|---|---|---|
| Presentation | Python / Tkinter GUI | User interface, button controls, live console output, node selection, snapshot management |
| Orchestration | HashiCorp Vagrant | VM lifecycle management, box provisioning, network adapter assignment, provisioner execution |
| Infrastructure | Oracle VirtualBox | Type 2 hypervisor hosting all five guest virtual machines |

### 2.2 Hybrid Provisioning Model

A hybrid provisioning stack handles configuration across the two operating system families in the lab. `ansible_local` handles all Linux node configuration by installing Ansible inside the guest VM itself, removing any host platform dependency. PowerShell scripts delivered via Vagrant's shell provisioner handle all Windows node configuration.

This model was adopted because Ansible cannot run natively on a Windows host machine as it relies on Linux and Unix system libraries. Rather than introducing an external Linux control node dependency, the hybrid approach keeps the artefact self-contained and deployable from any x86 Windows host.

### 2.3 Network Architecture

All five nodes communicate through three isolated Internal Network segments enforced by a central pfSense firewall. The Vagrant NAT adapter is used exclusively for management communication during provisioning and is explicitly removed from all routing tables after provisioning completes, ensuring all inter-segment traffic routes exclusively through pfSense.

| Segment | Network Name | Gateway | Nodes |
|---|---|---|---|
| Corporate LAN | intnet-lan | 10.0.1.1 | Windows Client (10.0.1.3), Domain Controller (10.0.1.2) |
| DMZ | intnet-dmz | 10.0.4.1 | Ubuntu Web Server (10.0.4.2) |
| Attacker | intnet-attacker | 10.0.3.1 | Kali Linux (10.0.3.2) |

---

## 3. Project Structure
NetbED/
├── Vagrantfile
├── main.py
├── pfsense1_config.xml
├── README.md
├── TECHNICAL.md
├── Ansible/
│   ├── attacker.yml
│   └── web-server.yml
└── Scripts/
├── dc_ipconfig.ps1
├── hostname.ps1
└── ipconfig.ps1

| File | Description |
|---|---|
| `Vagrantfile` | Core orchestration file in Ruby syntax. Defines all five node configurations including architecture detection, box selection, resource allocation, network adapter assignment and provisioner references. |
| `main.py` | Python entry point for the NetbED GUI. Contains all Tkinter interface logic, subprocess handling, threading, node selection and snapshot management. |
| `pfsense1_config.xml` | Pre-validated pfSense configuration file. Injected into the pfSense guest during provisioning to apply interface definitions and firewall rules automatically. |
| `Ansible/attacker.yml` | Ansible playbook for Kali Linux. Configures static IP on `eth1` via `community.general.nmcli`, prevents NAT route reassertion on `eth0` and removes the Vagrant NAT default gateway route. |
| `Ansible/web-server.yml` | Ansible playbook for Ubuntu. Writes Netplan config with `use-routes: false` on `enp0s3`, installs Apache while NAT is still active, defers Netplan apply until after installation, then strips the NAT default route. |
| `Scripts/hostname.ps1` | PowerShell script for the Windows Client hostname. Idempotent — only renames if the current hostname differs from the target. |
| `Scripts/ipconfig.ps1` | PowerShell script for the Windows Client. Discovers the secondary adapter, strips APIPA, applies static IP, sets DNS to the Domain Controller, disables automatic metric and removes the Vagrant NAT default gateway route. |
| `Scripts/dc_ipconfig.ps1` | PowerShell script for the Domain Controller. Applies static IP, sets DNS loopback, adds external forwarders (8.8.8.8, 1.1.1.1), disables automatic metric and removes the Vagrant NAT default gateway route. |

---

## 4. Development Environment

### 4.1 Hardware

Development was originally conducted across a hybrid workflow — an Apple M1 MacBook for coding and scripting with changes pushed to GitHub, and a dedicated x86 Windows desktop for virtualisation and testing. This approach was abandoned when it became clear that the pfSense Vagrant box is incompatible with ARM architecture. All subsequent development and testing was consolidated onto the x86 Windows desktop.

| Role | Machine |
|---|---|
| Coding and scripting | Apple M1 MacBook (VS Code, Git push) |
| Virtualisation and testing | x86 Windows Desktop (VirtualBox, Vagrant, Git pull) |

### 4.2 IDE — Visual Studio Code

| Extension | Purpose |
|---|---|
| Python | Development and execution of the GUI using Tkinter |
| Ansible | Writing Ansible playbooks in YAML with syntax highlighting and validation |
| Vagrant | Writing the Vagrantfile in Ruby with syntax support |
| PowerShell | Writing and validating Windows provisioning scripts |

### 4.3 Version Control — Git and GitHub

Git was used throughout the project with the central repository hosted on GitHub, providing portability across both development machines, a full commit history and the ability to roll back to previous working states.

```bash
git init
git config --global user.name "Frank-Morris"
git config --global user.email "francismorris22@gmail.com"
git remote add origin https://github.com/Frank-Morris/netbed.git
git add .
git commit -m "Initial commit"
git push origin main
```

A `.gitignore` file was created to exclude non-essential files. Two Personal Access Tokens were generated via GitHub Developer Settings for authentication on each machine. Tokens are time-limited and renewed on expiry.

---

## 5. Prerequisites and Dependencies

### 5.1 Hardware Requirements

| Requirement | Specification |
|---|---|
| Processor | x86-64 architecture (Intel or AMD). ARM not supported. |
| RAM | 16 GB minimum |
| Storage | 106 GB free disk space |
| Virtualisation | VT-x or AMD-V must be enabled in BIOS |

### 5.2 Software Dependencies

| Software | Version | Purpose |
|---|---|---|
| Oracle VirtualBox | 7.x | Type 2 hypervisor hosting all five guest VMs |
| HashiCorp Vagrant | Latest stable | Orchestration tool managing VM lifecycle and provisioning |
| vagrant-reload plugin | Latest stable | Required for the controlled reboot step in Windows Client provisioning |
| Python | 3.x | Required to run the NetbED GUI (`main.py`) |
| Tkinter | Standard library | GUI framework, included with Python — no separate installation required |
| Ansible | Installed by `ansible_local` | Installed automatically inside Linux guest VMs — no host installation required |

### 5.3 Installing the vagrant-reload Plugin
vagrant plugin install vagrant-reload

This plugin is not bundled with Vagrant core. Provisioning the Windows Client will fail without it.

---

## 6. Node Reference

### 6.1 pfSense Firewall

| Property | Value |
|---|---|
| Box | `Netbed/pfsense` (custom — hosted on Vagrant Cloud) |
| OS | FreeBSD |
| Role | Central gateway and firewall for all network segments |
| RAM | 512 MB |
| CPU | 1 core |
| WAN | vtnet0 (Vagrant NAT — DHCP) |
| LAN Interface | vtnet1 — 10.0.1.1 (intnet-lan) |
| Attacker Interface | em0 — 10.0.3.1 (intnet-attacker) |
| DMZ Interface | em1 — 10.0.4.1 (intnet-dmz) |
| Provisioning | File provisioner injects `pfsense1_config.xml`; shell provisioner copies to `/conf/config.xml`, clears cache, patches `rc.local` to enable `pfctl`, triggers PHP reload |

The custom `Netbed/pfsense` box was built from a configured pfSense VM with SSH pre-enabled, allowing Vagrant to connect and inject the XML without manual intervention. The provisioner re-enables the packet filter 5 seconds after configuration completes.

### 6.2 Domain Controller

| Property | Value |
|---|---|
| Box | `dstoliker/winserver2016-dc` |
| OS | Windows Server 2016 |
| Role | DNS server for intnet-lan |
| IP Address | 10.0.1.2 |
| Gateway | 10.0.1.1 (pfSense LAN) |
| DNS | 127.0.0.1 (loopback) |
| External DNS Forwarders | 8.8.8.8, 1.1.1.1 |
| RAM | 2048 MB |
| CPU | 2 cores |
| Communicator | WinRM |
| Provisioning | `Scripts/dc_ipconfig.ps1` |

### 6.3 Windows Client

| Property | Value |
|---|---|
| Box | `StefanScherer/windows_10` |
| OS | Windows 10 |
| Role | Simulated enterprise endpoint |
| IP Address | 10.0.1.3 |
| Gateway | 10.0.1.1 (pfSense LAN) |
| DNS | 10.0.1.2 (Domain Controller) |
| RAM | 4096 MB |
| CPU | 2 cores |
| VRAM | 128 MB |
| Graphics Controller | VMSVGA |
| Communicator | WinRM (`retry_limit: 30`, `retry_delay: 10`) |
| Provisioning | `Scripts/hostname.ps1` → `vagrant-reload` → `Scripts/ipconfig.ps1` |

### 6.4 Kali Linux Attacker

| Property | Value |
|---|---|
| Box | `kalilinux/rolling` (x86) |
| OS | Kali Linux |
| Role | Simulated external threat actor |
| IP Address | 10.0.3.2 |
| Gateway | 10.0.3.1 (pfSense Attacker interface) |
| RAM | 2048 MB |
| CPU | 2 cores |
| Provisioning | `ansible_local` — `Ansible/attacker.yml` |
| Network Module | `community.general.nmcli` |

### 6.5 Ubuntu Web Server

| Property | Value |
|---|---|
| Box | `ubuntu/jammy64` (x86) |
| OS | Ubuntu 22.04 LTS |
| Role | DMZ web server |
| IP Address | 10.0.4.2 |
| Gateway | 10.0.4.1 (pfSense DMZ interface) |
| RAM | 1024 MB |
| CPU | 1 core |
| Provisioning | `ansible_local` — `Ansible/web-server.yml` |
| Services | Apache HTTP Server |

---

## 7. Vagrantfile Reference

### 7.1 Architecture Detection

The Vagrantfile opens with a Ruby block that detects the host CPU architecture and selects the appropriate Vagrant boxes. The pfSense constraint limits the artefact to x86 only, but the detection logic remains in place for the Linux boxes.

```ruby
architecture = RbConfig::CONFIG['host_cpu'].downcase

if architecture.include?('arm') || architecture.include?('aarch64')
  puts "ARM architecture detected. Using ARM-compatible boxes."
  ubuntu_box = "bento/ubuntu-22.04"
  kali_box = "kali-arm/kali-me"
else
  puts "x86 architecture detected. Using standard boxes."
  ubuntu_box = "ubuntu/jammy64"
  kali_box = "kalilinux/rolling"
end
```

### 7.2 Windows Client — VirtualBox Customisations

The Windows Client includes additional VirtualBox provider customisations to ensure the display renders correctly in the VirtualBox console.

```ruby
v.customize ["modifyvm", :id, "--vram", "128"]
v.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
```

### 7.3 Windows Client — WinRM and Provisioning Chain

```ruby
client.winrm.retry_limit = 30
client.winrm.retry_delay = 10
client.vm.boot_timeout = 600

client.vm.provision "shell", path: "scripts/hostname.ps1"
client.vm.provision "reload"
client.vm.provision "shell", path: "scripts/ipconfig.ps1"
```

The `vagrant-reload` plugin injects a controlled reboot between the hostname rename and the IP configuration script. This ordering is mandatory — see Section 10.3.

### 7.4 pfSense Provisioner

```ruby
pf.vm.provision "file", source: "pfsense1_config.xml", destination: "/tmp/pfsense1_config.xml"
pf.vm.provision "shell",
  privileged: false,
  inline: "cp /tmp/pfsense1_config.xml /conf/config.xml && \
           rm -f /tmp/config.cache && \
           sed -i '' 's/pfctl -d/pfctl -e/' /etc/rc.local && \
           (daemon -f sh -c 'sleep 5 && pfctl -e') && \
           (daemon -f /usr/local/bin/php -f /etc/rc.reload_all) && \
           echo 'SUCCESS: Deployment complete. Firewall will engage in 5 seconds.'"
```

---

## 8. Firewall Configuration

The pfSense firewall enforces a default-deny ruleset. All rules are defined in `pfsense1_config.xml` and applied automatically during provisioning.

### 8.1 Interface Assignments

| Interface | pfSense Name | Adapter | IP |
|---|---|---|---|
| WAN | wan | vtnet0 | DHCP (Vagrant NAT) |
| LAN | lan | vtnet1 | 10.0.1.1/24 |
| Attacker | opt1 | em0 | 10.0.3.1/24 |
| DMZ | opt2 | em1 | 10.0.4.1/24 |

### 8.2 Firewall Rules

| Rule | Interface | Source | Destination | Protocol | Action | Description |
|---|---|---|---|---|---|---|
| 1 | WAN | Any | WAN IP port 22 | TCP | Pass | Permits SSH to pfSense during provisioning |
| 2 | LAN | LAN net | Any | IPv4 | Pass | Default allow — LAN machines reach internet via pfSense NAT |
| 3 | LAN | LAN net | Any | IPv6 | Pass | Default allow IPv6 |
| 4 | Attacker (opt1) | opt1 net | LAN net | IPv4 | Block | Prevents Kali from directly reaching internal LAN |
| 5 | Attacker (opt1) | opt1 net | DMZ (opt2) net | IPv4 | Pass | Permits Kali to reach the DMZ web server |
| 6 | DMZ (opt2) | opt2 net | LAN net | IPv4 | Block | Prevents a compromised web server reaching internal LAN |

### 8.3 NAT

Outbound NAT is set to `automatic`, allowing LAN machines to reach the internet via the pfSense WAN (Vagrant NAT) interface.

---

## 9. Provisioning Scripts Reference

### 9.1 `Scripts/hostname.ps1` — Windows Client Hostname

Runs first in the provisioning sequence. Checks the current hostname and only triggers a rename if it differs from the target, implementing idempotency to prevent unnecessary reboots on re-provision.

```powershell
Write-Host "Current host name is set to $env:COMPUTERNAME"
$hostname = "Client"

if ($env:COMPUTERNAME -ne $hostname) {
    Write-Host "Current name: $env:COMPUTERNAME"
    Write-Host "Renaming computer to '$hostname'..."
    Rename-Computer -NewName $hostname -Force
    Write-Warning "Hostname changed. A reboot is required for this to take effect."
} else {
    Write-Host "Hostname is already correctly set to '$hostname'."
}
```

**Key logic:**
- `$env:COMPUTERNAME` is compared against the target value before any action is taken
- `Rename-Computer` only fires if the names differ
- `-Force` suppresses confirmation prompts for unattended execution

---

### 9.2 `Scripts/ipconfig.ps1` — Windows Client Static IP

Runs after the vagrant-reload reboot. Dynamically discovers the secondary adapter, strips the APIPA address, applies the static IP, sets DNS to the Domain Controller, disables automatic metric and explicitly removes the Vagrant NAT default gateway route.

```powershell
Write-Host "Vagrant is running shell script to configure the static IP address."
$staticIp = "10.0.1.3"
$subnet   = 24
$gateway  = "10.0.1.1"
$dns      = "10.0.1.2"
$metric   = 10

$adapter = Get-NetAdapter | Where-Object { $_.InterfaceAlias -ne "Ethernet" -and $_.Status -eq "Up" }

if ($adapter) {
    Write-Host "Adapter found: $($adapter.InterfaceAlias)"

    Remove-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -Confirm:$false -ErrorAction SilentlyContinue

    New-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex `
                     -IPAddress $staticIp `
                     -PrefixLength $subnet `
                     -DefaultGateway $gateway

    Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses $dns

    Write-Host "Forcing Windows to stop auto-calculating the metric..."
    Set-NetIPInterface -InterfaceIndex $adapter.InterfaceIndex -AutomaticMetric Disabled -InterfaceMetric 10
    Set-NetRoute -DestinationPrefix "0.0.0.0/0" -InterfaceIndex $adapter.InterfaceIndex -RouteMetric 1 -ErrorAction SilentlyContinue

    Write-Host "Removing Vagrant NAT default route..."
    Remove-NetRoute -DestinationPrefix "0.0.0.0/0" -NextHop "10.0.2.2" -Confirm:$false -ErrorAction SilentlyContinue
} else {
    Write-Error "No valid adapter located."
}
```

**Key logic:**
- `Get-NetAdapter` with `Where-Object` excludes the Vagrant NAT adapter (named `Ethernet`) and targets only active adapters — dynamic discovery avoids hardcoding adapter names that may differ between OS versions
- `Remove-NetIPAddress` with `-Confirm:$false` strips the APIPA address; `-ErrorAction SilentlyContinue` handles cases where no APIPA is present
- `Set-DnsClientServerAddress` points the client at the Domain Controller (`10.0.1.2`) for DNS resolution
- `Set-NetIPInterface -AutomaticMetric Disabled` stops Windows from recalculating route preference automatically
- `Set-NetRoute -RouteMetric 1` forces the internal adapter's default gateway to metric 1, making pfSense the preferred route
- `Remove-NetRoute` targeting `10.0.2.2` hard-removes the Vagrant NAT default gateway, ensuring no traffic leaks through the management adapter

---

### 9.3 `Scripts/dc_ipconfig.ps1` — Domain Controller Configuration

Applies static IP, sets DNS loopback so the DC resolves its own domain, adds external DNS forwarders for internet resolution, disables automatic metric and removes the Vagrant NAT default gateway route.

```powershell
Write-Host "Configuring static IP and networking routes."
$staticIp = "10.0.1.2"
$subnet   = 24
$gateway  = "10.0.1.1"
$dns      = "127.0.0.1"
$metric   = 10

$adapter = Get-NetAdapter | Where-Object { $_.InterfaceAlias -ne "Ethernet" -and $_.Status -eq "Up" }

if ($adapter) {
    Write-Host "Adapter found: $($adapter.InterfaceAlias)"

    Remove-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -Confirm:$false -ErrorAction SilentlyContinue

    New-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex `
                     -IPAddress $staticIp `
                     -PrefixLength $subnet `
                     -DefaultGateway $gateway

    Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses $dns

    Write-Host "Forcing Windows to stop auto-calculating the metric..."
    Set-NetIPInterface -InterfaceIndex $adapter.InterfaceIndex -AutomaticMetric Disabled -InterfaceMetric 10
    Set-NetRoute -DestinationPrefix "0.0.0.0/0" -InterfaceIndex $adapter.InterfaceIndex -RouteMetric 1 -ErrorAction SilentlyContinue

    Write-Host "Configuring Active Directory DNS forwarders..."
    Add-DnsServerForwarder -IPAddress "8.8.8.8", "1.1.1.1" -PassThru -ErrorAction SilentlyContinue

    Write-Host "Removing Vagrant NAT default route..."
    Remove-NetRoute -DestinationPrefix "0.0.0.0/0" -NextHop "10.0.2.2" -Confirm:$false -ErrorAction SilentlyContinue
} else {
    Write-Error "No valid adapter located."
}
```

**Key logic:**
- Same dynamic adapter discovery as `ipconfig.ps1`
- `Set-DnsClientServerAddress` sets `127.0.0.1` so the DC resolves DNS queries against its own DNS service
- `Add-DnsServerForwarder` adds `8.8.8.8` and `1.1.1.1` so the DC can forward external domain queries — this is what allows `nslookup google.com` to resolve correctly from the Windows Client
- Metric forcing and NAT route removal follow the same logic as `ipconfig.ps1`

---

### 9.4 `Ansible/attacker.yml` — Kali Linux

Configures the Kali Linux attacker node using `community.general.nmcli` to create a persistent static IP connection. Includes three separate NAT isolation tasks to prevent the Vagrant management adapter from reasserting its default route.

```yaml
---
- name: Configure Attacker machines
  hosts: all
  become: true
  tasks:
    - name: Add Ethernet connection with static IP
      community.general.nmcli:
        conn_name: LabEth
        ifname: eth1
        type: ethernet
        ip4: 10.0.3.2/24
        gw4: 10.0.3.1
        route_metric4: 50
        state: present
        conn_reload: true
      notify: Restart Networking

    - name: Permanently ignore NAT routes on eth0
      ansible.builtin.shell: |
        nmcli device modify eth0 ipv4.ignore-auto-routes yes
        while ip route del default via 10.0.2.2 dev eth0; do :; done
      ignore_errors: true

    - name: Prevent eth0 from asserting default route on resume
      community.general.nmcli:
        conn_name: "Wired connection 1"
        type: ethernet
        ifname: eth0
        never_default4: true
        state: present

  handlers:
    - name: Restart Networking
      service:
        name: networking
        state: restarted
```

**Key logic:**
- `community.general.nmcli` communicates directly with the NetworkManager daemon — required because NetworkManager overrides `/etc/network/interfaces` on the `kalilinux/rolling` desktop image (see Section 10.4)
- `route_metric4: 50` sets route preference for the lab connection, making pfSense preferred over the NAT adapter
- `ipv4.ignore-auto-routes yes` on `eth0` instructs NetworkManager to stop accepting the DHCP-assigned default route on the NAT adapter
- The `while` loop strips all existing `10.0.2.2` default routes until none remain
- `never_default4: true` on the `eth0` connection profile permanently prevents the NAT adapter from asserting a default route, which is particularly important after a suspend/resume cycle

---

### 9.5 `Ansible/web-server.yml` — Ubuntu Web Server

Configures the Ubuntu web server with Netplan static IP configuration. Apache is installed before Netplan is applied so that package downloads can still use the Vagrant NAT adapter for internet access.

```yaml
---
- name: Configure web server
  hosts: all
  become: true
  tasks:
    - name: Write Netplan static IP config
      copy:
        dest: /etc/netplan/99-netbed-config.yaml
        mode: '0600'
        content: |
          network:
            version: 2
            renderer: networkd
            ethernets:
              enp0s8:
                dhcp4: no
                addresses:
                  - 10.0.4.2/24
                routes:
                  - to: default
                    via: 10.0.4.1
                    metric: 50
                nameservers:
                  addresses: [8.8.8.8, 8.8.4.4]
              enp0s3:
                dhcp4: yes
                dhcp6: no
                dhcp4-overrides:
                  use-routes: false
                dhcp6-overrides:
                  use-routes: false
      notify: apply Netplan

    - name: Update apt package cache
      ansible.builtin.apt:
        update_cache: true

    - name: Install Apache web server
      ansible.builtin.apt:
        name: apache2
        state: present

    - name: Force Netplan to apply now
      ansible.builtin.meta: flush_handlers

    - name: Strip all instances of NAT default gateway
      ansible.builtin.shell: |
        while ip route del default via 10.0.2.2 dev enp0s3; do :; done
      ignore_errors: true

  handlers:
    - name: apply Netplan
      command: netplan apply
```

**Key logic:**
- The Netplan config is written first but the handler is deferred — `apt update` and Apache install run while the Vagrant NAT adapter still provides internet access
- `enp0s3` is explicitly configured with `dhcp4-overrides: use-routes: false` — this prevents the DHCP lease on the NAT adapter from injecting a default route that would compete with pfSense
- `metric: 50` on the pfSense route sets explicit route preference for `enp0s8`
- `flush_handlers` fires the deferred `netplan apply` after Apache is installed, switching the network to the static IP on pfSense
- The `while` loop strips any remaining `10.0.2.2` default routes
- The file is named `99-netbed-config.yaml` — the `99` prefix ensures it always overrides `50-cloud-init.yaml` and Vagrant's `50-vagrant.yaml` under Netplan's lexicographical ordering

---

### 9.6 GUI — `main.py`

The GUI is built using Python and Tkinter. All Vagrant commands are executed via `subprocess.Popen` on a background thread to prevent the interface from freezing during long-running operations.

**Key components:**

| Component | Implementation |
|---|---|
| Node selection | `self.nodes` dictionary maps node names to `tk.BooleanVar` instances; pfSense defaults to `True` |
| Configure Nodes popup | `Toplevel` window dynamically generates a `Checkbutton` for each node |
| Button commands | Each button constructs the appropriate `vagrant` command from `get_selected_nodes()` and passes it to `run_subprocess()` |
| Live console output | `subprocess.Popen` with `stdout=subprocess.PIPE`; output read line by line and passed to `ScrolledText` via `window.after()` |
| Thread safety | All subprocess calls run on daemon threads via `threading.Thread`; UI updates scheduled via `window.after()` to avoid cross-thread Tkinter access |
| Button state management | `set_gui_state()` disables all control buttons at subprocess start and re-enables on completion, preventing concurrent Vagrant lock conflicts |
| Snapshot management | `snap_save()` prompts for a name via `simpledialog.askstring` and runs `vagrant snapshot save`; `snap_load()` reads the active listbox selection and runs `vagrant snapshot restore` |

**Threading model:**

```python
def run_subprocess(self, command):
    def execute():
        self.window.after(0, self.set_gui_state, tk.DISABLED)
        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            self.window.after(0, self.log_to_console, line)
        process.wait()
        self.window.after(0, self.set_gui_state, tk.NORMAL)
    threading.Thread(target=execute, daemon=True).start()
```

---

## 10. Engineering Challenges

### 10.1 Windows Client — APIPA Race Condition

**The challenge:** On boot, the Windows network stack attempts to auto-configure the secondary adapter via DHCP. Since `intnet-lan` has no DHCP server during provisioning, the OS defaults to an APIPA address (`169.254.x.x`) before Vagrant can intervene, blocking static IP injection.

**The solution:** `ipconfig.ps1` runs natively on the guest after provisioning. It dynamically discovers the secondary adapter by excluding the Vagrant NAT adapter, strips the APIPA address and applies the correct static IP. `-Confirm:$false` and `-ErrorAction SilentlyContinue` ensure the script runs unattended without pausing or crashing if no APIPA is present.

---

### 10.2 Windows Client — Hostname Instability

**The challenge:** Changing the NetBIOS hostname on Windows triggers a mandatory reboot. Using Vagrant's native `vm.hostname` setting caused provisioning to hang — the reboot severed the WinRM connection before Vagrant received a success signal.

**Failed mitigation:** Increasing `winrm.retry_limit` to 30 and `winrm.retry_delay` to 10 seconds did not resolve the race condition.

**The solution:** A dedicated PowerShell script (`hostname.ps1`) checks the current hostname before acting, implementing idempotency to prevent unnecessary reboots on re-provision. The `vagrant-reload` plugin injects a controlled reboot between the hostname script and the IP configuration script.

---

### 10.3 Windows Provisioning — Dependency Chain

The order of operations in the Vagrantfile is critical for Windows Client provisioning.
hostname.ps1  →  vagrant-reload  →  ipconfig.ps1

- `hostname.ps1` must run first — triggers a rename if needed
- `vagrant-reload` must happen immediately after — finalises the NetBIOS name change
- `ipconfig.ps1` must run last — if run before the reload, the APIPA race condition would reassign `169.254.x.x` during the reboot, overwriting the static IP

The `vagrant-reload` plugin is an external dependency. Provisioning will fail at the reload step if it is not installed.

---

### 10.4 Kali Linux — NetworkManager Override

**The challenge:** Initial attempts to configure the static IP used the `blockinfile` Ansible module to append config to `/etc/network/interfaces`.

**Approach A — Legacy file (failed):**

```yaml
- name: Configure Static IP on eth1
  blockinfile:
    path: /etc/network/interfaces
    block: |
      auto eth1
      iface eth1 inet static
      address 10.0.3.2
      netmask 255.255.255.0
      gateway 10.0.3.1
  notify: Restart Networking
```

The `kalilinux/rolling` box ships with a full desktop environment and NetworkManager, which overrides `/etc/network/interfaces` on every boot. The `eth1` connection reverted to DHCP and disconnected regardless, confirmed by `nmcli connection show` and `ip addr`.

**Approach B — NetworkManager API (successful):**

The `community.general.nmcli` module communicates directly with the NetworkManager daemon via its API, bypassing legacy config files entirely. NetworkManager itself creates and manages the connection profile, eliminating the conflict. See Section 9.4 for the full implementation.

---

### 10.5 Ubuntu Web Server — Netplan Race Condition

**The challenge:** A race condition occurred between the Netplan configuration files present on the Ubuntu image. Netplan processes files in lexicographical order, with higher numeric prefixes winning.

| File | Origin | Effect |
|---|---|---|
| `50-cloud-init.yaml` | Default — cloud-init | Enforces DHCP |
| `50-vagrant.yaml` | Vagrant provisioner | Sets static IP but without a default gateway |

The Vagrant provisioner applied a static IP but without a `routes` block, meaning the web server could not route traffic to pfSense — the DMZ was effectively isolated from its own gateway.

**The solution:** The Ansible playbook writes `99-netbed-config.yaml`, which wins precedence by prefix. It defines the full static IP, the pfSense gateway via a `routes` block and sets `use-routes: false` on `enp0s3` to prevent the DHCP lease from injecting a competing default route. The handler is deferred until after Apache is installed so that `apt` can still use the NAT adapter for package downloads. See Section 9.5 for the full implementation.

---

### 10.6 pfSense — Initial Configuration and Subnet Mismatch

**The challenge:** pfSense stores its entire state — interfaces, firewall rules, NAT settings — in a single XML file (`/conf/config.xml`). Automating the lab requires injecting a pre-configured XML file during boot. However, generating this file requires accessing the pfSense WebGUI from another node.

A fresh pfSense installation defaults its LAN interface to `192.168.1.1/24`. The Windows Client was on `10.0.1.3/24`. The subnet mismatch meant the client could not reach the WebGUI, making initial configuration impossible.

**The solution — "Golden XML" approach:**

1. **Manual network override:** Accessed the pfSense console directly via VirtualBox. Menu option 2 (Set interface(s) IP address) manually assigned the LAN interface to `10.0.1.1/24`
2. **WebGUI configuration:** With pfSense on the same subnet, the WebGUI was accessed at `https://10.0.1.1` from the Windows Client. Remaining interfaces and firewall rules were configured
3. **XML export:** The finalised configuration was exported via pfSense Diagnostics → Backup & Restore as `pfsense1_config.xml`
4. **Automated injection:** The exported XML is now injected on every deployment via the Vagrant shell provisioner, eliminating all manual steps for end users

A custom Vagrant box (`Netbed/pfsense`) was built from the configured VM with SSH pre-enabled, removing the requirement to manually enable SSH through the pfSense console before each deployment.

---

## 11. Known Issues and Limitations

| Issue | Cause | Current Workaround | Planned Fix |
|---|---|---|---|
| ARM architecture not supported | pfSense box is x86-64 only | Use an x86-64 host machine | No current solution |
| Active Directory domain promotion not implemented | Not completed within project timeline | DC runs DNS only | Additional PowerShell scripts for domain promotion and client domain join |
| Snapshot listbox clears on restart | In-memory list, not persisted to disk | Use VirtualBox Manager to access snapshots | JSON file persistence |
| Snapshot limited to one node at a time | Single-node selection in current implementation | Run snapshot per node individually | Query VirtualBox directly via `VBoxManage` |
| VirtualBox VM folders can persist after `vagrant destroy` | VirtualBox does not always clean up fully | Manually delete leftover folder before retrying | Investigate `vboxmanage unregistervm --delete` as post-destroy hook |
| WinRM timeout during Windows provisioning | Windows VM latency during boot | Wait and re-run `vagrant provision` on the affected node | Tuned retry parameters |

---

## 12. Future Development

### 12.1 Active Directory Domain Join

The DC is provisioned with DNS and static IP but the Windows Client is not joined to the domain. A PowerShell provisioning script to promote the DC and join the client is planned as the next enhancement, enabling domain authentication, Group Policy application and domain DNS resolution across `intnet-lan`.

### 12.2 Snapshot Persistence

Persist the snapshot list to a JSON file in the project directory, loading it on startup and updating on snapshot creation or deletion. A further improvement would query VirtualBox directly via `VBoxManage` to enumerate all available snapshots per node dynamically.

### 12.3 Multi-Lab Topology Support

Support for multiple selectable lab configurations from the GUI, each with its own node set, IP scheme, provisioning scripts and pfSense ruleset. The current modular architecture already supports this conceptually — it would be an extension of the existing structure rather than a redesign.

### 12.4 GUI Improvements

Individual machine status indicators showing whether each node is running, halted or absent, and a log export feature allowing console output to be saved to a file after provisioning.

### 12.5 Offline Deployment

All Vagrant boxes require an internet connection on first run. Packaging boxes locally for air-gapped or restricted network environments is a planned future enhancement.

### 12.6 AI Integration

The isolated and reproducible network segments provide a foundation for AI integration — potential directions include an AI-driven attacker agent on the Kali node, a machine learning-based IDS in the DMZ, and LLM-generated attack scenarios or guided learning prompts within the GUI.

---

## 13. Troubleshooting

| Issue | Likely Cause | Resolution |
|---|---|---|
| `vagrant up` fails immediately | Vagrant or VirtualBox not installed correctly | Reinstall both. Verify with `vagrant --version` and `VBoxManage --version` |
| Windows machine shows `169.254.x.x` | APIPA race condition during boot | Run `vagrant provision client` to re-execute the IP configuration script |
| Provisioning hangs on Windows node | WinRM timeout during reboot cycle | Wait 5 minutes then run `vagrant provision` on the affected node |
| Kali `eth1` reverts to DHCP after reboot | NetworkManager override | Verify the nmcli connection with `nmcli connection show`. Re-run `vagrant provision attacker` |
| Apache not reachable on `10.0.4.2` | Netplan applied before Apache installed | Re-run `vagrant provision web-server` |
| NAT route still present after provisioning | Route removal script did not complete | SSH into the node and manually remove the `10.0.2.2` default route |
| Deployment conflict after `vagrant destroy` | VirtualBox VM folder persisted on disk | Manually delete the leftover VM folder from your VirtualBox VMs directory, then retry |
| GUI does not open | Python not installed or not in PATH | Verify with `python --version`. Reinstall Python with **Add to PATH** ticked |
| Snapshot names missing after restart | Listbox cleared on application restart | Access snapshots through VirtualBox Manager directly |
| `vagrant-reload` plugin missing | Plugin not installed before provisioning | Run `vagrant plugin install vagrant-reload` |

---

*NetbED — Francis Morris · B00386292 · BEng (Hons) Cyber Security · University of the West of Scotland · 2026*