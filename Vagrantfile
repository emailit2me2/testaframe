# -*- mode: ruby -*-
# vi: set ft=ruby :

# To bring up a test VM follow the instructions below
# comments with a single # are to run on the host machine
## comments with two ## are for running inside the VM
# `vagrant up`
# `vagrant ssh`
## `nosetests run_user.py -m test_in_order`
## The test should succeed

# If you'd like to do GUI/browser testing inside a VM GUI do the following.
# You could set the DISPLAY to display back onto your host instead.
## `sudo apt-get install -y lxde`
## exit vagant
# uncomment the `v.gui = true`
# `vagrant reload`
# gui desktop should come up.
## login to the gui `vagrant:vagrant`
# `vagrant ssh`
## run `chromium-browser` and it should show up in the GUI window
## close the browser
## `nosetests run_user.py -m test_wikipedia`
## the test should run in the gui

# This file is configured for browser testing inside the VM.
# For displaying a full GUI:
# uncomment the `v.gui = true`
# then `vagrant reload`
## To configure autologin of the vagrant user run
## `sudo sed -i 's/^.*autologin=.*$/autologin=vagrant/' /etc/lxdm/default.conf`

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.hostname = "testall"
  config.vm.network :forwarded_port, guest: 22, host: 5678

  # Firefox 49.x doesn't currently work with selenium 2.53.1. So you might need to install an older version.
  # http://security.ubuntu.com/ubuntu/pool/main/f/firefox/firefox_48.0+build2-0ubuntu1_amd64.deb
  # sudo dpkg -i firefox_48.0+build2-0ubuntu1_amd64.deb

  config.ssh.forward_agent = true
  config.ssh.forward_x11 = true

# Install desktop and virtualbox additions
  config.vm.provision "shell", inline: "sudo apt-get update"
  config.vm.provision "shell", inline: "sudo apt-get install -y virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11 \
                                             dkms linux-headers-generic \
                                             build-essential python-dev python-pip openntpd graphviz git \
                                             firefox chromium-browser chromium-chromedriver libgconf-2-4 eog \
                                             "
                                             # Can't install lxde here for some reason :-(
#  config.vm.provision "shell", inline: "sudo sed -i 's/^.*autologin=.*$/autologin=vagrant/' /etc/lxdm/default.conf"


  # the chromium-chromedriver package doesn't put itself into the PATH.
  config.vm.provision "shell", inline: "sudo printf '#!/bin/bash
# This file is created by a vagrant up or provision, so make personalizations in ~vagrant/.bashrc
if [ -f ~/.bashrc ]; then
   source ~/.bashrc
fi
export PATH=$PATH:/usr/lib/chromium-browser/
echo Default DISPLAY value was: $DISPLAY
export DISPLAY=:0
cd /vagrant
' > /home/vagrant/.bash_profile"

  config.vm.provision "shell", inline: "pushd /vagrant  && sudo pip install -r pip_requirements.txt && popd"

  config.vm.provider "virtualbox" do |v|
    v.customize ["guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold", 10000]
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.gui = true
    v.memory = 1024
    v.cpus = 2
  end
end
