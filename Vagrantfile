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
    ubuntu.vm.network "private_network", ip: "10.0.4.2", virtualbox__intnet: "intnet-dmz"
    #Runs ansible playbook
    ubuntu.vm.provision "ansible_local", playbook: "ansible/web-server.yml"
  end

#This is the config for the attacker machine.
  config.vm.define "attacker" do |kali|
    kali.vm.box = kali_box
    kali.vm.hostname = "attacker"
    kali.vm.network "private_network", ip: "10.0.3.2", virtualbox__intnet: "intnet-attacker"
  end
#This is the config for the Domain-Controller.
  config.vm.define "domain-controller" do |dc|
    dc.vm.box = "dstoliker/winserver2016-dc"
    dc.vm.hostname = "domain-controller"
    dc.vm.network "private_network", ip: "10.0.1.2"
  end
#This is the config for the Windows Client
  config.vm.define "client" do |client|
    client.vm.box = "sva-mk/Windows-10"
    client.vm.hostname = "client"
    client.vm.network "private_network", ip: "10.0.1.3"
    client.ssh.username = "vagrant"
    client.ssh.password = "vagrant" 

  client.vm.provider "virtualbox" do |v|
    v.memory = 4096
    v.cpus = 2
    v.customize ["modifyvm", :id, "--vram", "128"]
    v.customize ["modifyvm", :id, "--graphicscontroller", "vmsvga"]
  end
end
end