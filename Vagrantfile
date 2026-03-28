#Find the architecture, ARM or x86.
architecture = RbConfig::CONFIG['host_cpu'].downcase

#Variable names for boxes.
if architecture.include?('arm') || architecture.include?('aarch64')
  #Run boxes for ARM architecture.
  puts "ARM architecture detected. Using ARM-Compataible boxes."
  ubuntu_box = "bento/ubuntu-22.04"
  kali_box = "kali-arm/kali-me"
else
  #Run boxes for x86 architecture
  puts "x86 architecure detected. Using standard boxes"
  ubuntu_box = "ubuntu/jammy64"
  kali_box = "kalilinux/rolling"
end

#Define vagrant boxes to configure virtual machines.
Vagrant.configure("2") do |config|
#This is the config for the web server.  
  config.vm.define "web-server" do |ubuntu|
    ubuntu.vm.box = ubuntu_box
    ubuntu.vm.hostname = "web-server"
    #Sets the static ip for web servers
    ubuntu.vm.network "private_network", ip: "10.0.4.2", virtualbox__intnet: "intnet-dmz", gateway: "10.0.4.1"
    #Runs ansible playbook
    ubuntu.vm.provision "ansible_local", playbook: "ansible/web-server.yml"
    ubuntu.vm.provider "virtualbox" do |v|
      v.name = "Web Server"
      v.memory = 1024
      v.cpus = 1
  end 
end

#This is the config for the attacker machine.
  config.vm.define "attacker" do |kali|
    kali.vm.box = kali_box
    kali.vm.hostname = "attacker"
    kali.vm.network "private_network", ip: "10.0.3.2", virtualbox__intnet: "intnet-attacker"

    kali.vm.provision "ansible_local", playbook: "ansible/attacker.yml" 
    kali.vm.provider "virtualbox" do |v|
      v.name = "Attacker"
      v.memory = 2048
      v.cpus = 2
  end
end


#This is the config for the Domain-Controller.
  config.vm.define "domain-controller" do |dc|
    dc.vm.box = "dstoliker/winserver2016-dc"
    dc.vm.communicator ="winrm"
    dc.vm.guest = :windows
    dc.vm.network "private_network", ip: "10.0.1.2", virtualbox__intnet: "intnet-lan"

    dc.vm.provision "shell", path: "scripts/dc_ipconfig.ps1"
    dc.vm.provider "virtualbox" do |v|
      v.memory = 2048
      v.cpus = 2
      v.name = "Domain Controller"
  end
end


########################################################################################################################################################################################################
#This is the config for the Windows Client
  config.vm.define "client" do |client|
    client.vm.box = "sva-mk/Windows-10"
    client.vm.communicator = "winrm"
    client.vm.guest = :windows
    client.winrm.retry_limit = 30
    client.winrm.retry_delay = 10
    client.vm.boot_timeout = 600
    client.vm.network "private_network", ip: "10.0.1.3", auto_config: false, virtualbox__intnet: "intnet-lan"
    client.ssh.username = "vagrant"
    client.ssh.password = "vagrant"
    
    #sets hostname of machine
    client.vm.provision "shell", path: "scripts/hostname.ps1"
    
    #reloads machine to confirm the hostname change.
    client.vm.provision "reload"
    
    #Runs shellscript to configure static IP
    client.vm.provision "shell", path: "scripts/ipconfig.ps1"
  
  

    client.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.cpus = 2
      v.customize ["modifyvm", :id, "--vram", "128"]
      v.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
      v.name = "Client"
      
 end
end
##################################################################################################################################################################################################

#This is the config for the pfsense firewall
config.vm.define "pfsense" do |pf|
  pf.vm.box ="nandillonmax/Pfsense-max"
  pf.vm.synced_folder ".", "/vagrant", disabled: true

  pf.vm.guest = :openbsd

  pf.vm.network "private_network", ip: "10.0.1.1", virtualbox__intnet: "intnet-lan", auto_config: false
  pf.vm.network "private_network", ip: "10.0.3.1", virtualbox__intnet: "intnet-attacker", auto_config: false
  pf.vm.network "private_network", ip: "10.0.4.1", virtualbox__intnet: "intnet-dmz", auto_config: false
  pf.vm.allow_hosts_modification = false

  pf.ssh.shell = "/bin/sh"
  
  pf.vm.provider "virtualbox" do |v|
    v.name = "pfsense"
    v.memory = 512
    v.cpus = 1
 end

  pf.ssh.insert_key = false
  pf.ssh.username = "root"
  pf.ssh.password = "pfsense"
  pf.ssh.shell = "/bin/sh"
  



  pf.vm.provision "file", source: "pfsense_config.xml", destination: "/tmp/pfsense_config.xml"
  pf.vm.provision "shell", 
    privileged: false,
    inline: "cp /tmp/pfsense_config.xml /conf/config.xml && rm -f /tmp/config.cache && (daemon -f sh -c 'sleep 5 && pkill -9 sshd && pfctl -e') && (daemon -f /usr/local/bin/php -f /etc/rc.reload_all) && echo 'SUCCESS: Deployment complete. Firewall will engage in 5 seconds.'"
end
end