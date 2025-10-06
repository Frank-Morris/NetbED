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
    ubuntu.vm.network "private_network", ip: "192.168.20.10"
    #Runs ansible playbook
    ubuntu.vm.provision "ansible_local", playbook: "playbook.yml"
  end

#This is the config for the attacker machine.
  config.vm.define "attacker" do |kali|
    kali.vm.box = kali_box
    kali.vm.hostname = "attacker"
    kali.vm.network "private_network", ip: "192.168.20.11"
  end
#Put configs here for additional virtual machines.
end