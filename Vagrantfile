# -*- mode: ruby -*-
# vi: set ft=ruby :

# spins up the servers needed 
# to test this project in development

logger_ip  = "192.168.33.10"
rpi_ips    = ["192.168.33.15", "192.168.33.16"]

proxy = ENV['HTTP_PROXY']
puts proxy

if proxy
	unless Vagrant.has_plugin?("vagrant-proxyconf")
  	system "vagrant plugin install vagrant-proxyconf" 
	end
end

Vagrant.configure("2") do |config|
	config.vm.provider :virtualbox do |v|
    v.check_guest_additions = false
    v.functional_vboxsf     = false
  end
  if Vagrant.has_plugin?("vagrant-vbguest") then
    config.vbguest.auto_update = false
  end

  config.ssh.insert_key = false

	config.vm.define "logger" do |node|
    handle_proxies node, proxy
    node.vm.box = "bento/centos-7.2"
    node.vm.network "private_network", ip: logger_ip
    node.vm.hostname = "logger"
    update_box node
	end

  rpi_ips.each_with_index do |ip, index|
    config.vm.define "rpi#{index}" do |node|
      handle_proxies node, proxy
      node.vm.box = "bento/centos-7.2"
      node.vm.network "private_network", ip: ip
      node.vm.hostname = "rpi0"
      update_box node
    end
  end
end

def handle_proxies vm, proxy
  if proxy
    vm.proxy.http     = "http://proxy.intra.bt.com:8080"
    vm.proxy.https    = "http://proxy.intra.bt.com:8080"
    vm.proxy.no_proxy = \
      "localhost,127.0.0.1,*.intra.bt.com,*.nat.bt.com"
  end
end

def update_box box
  box.vm.provision :shell, :inline => <<-SH
    yum update -y
  SH
end
