#!/bin/bash
set -u
set -e

echo "This command will change this host network settings. Press enter to proceed if you know what you are doing."
echo "or Ctrl-C to quit"
read

sudo cp /home/firelet/.bashrc /home/firelet/.bashrc.orig
sudo cp bashrc /home/firelet/.bashrc
sudo cp firelet_node_emulator.py /home/firelet/firelet_node_emulator.py

IF=eth1

sudo /sbin/ifconfig $IF:10 10.66.1.2/24 up
sudo /sbin/ifconfig $IF:11 10.66.2.1/24 up
sudo /sbin/ifconfig $IF:12 10.66.1.3/24 up
sudo /sbin/ifconfig $IF:13 10.66.2.2/24 up
sudo /sbin/ifconfig $IF:14 172.16.2.223/24 up
sudo /sbin/ifconfig $IF:14 10.66.1.1/24 up
sudo /sbin/ifconfig $IF:14 88.88.88.88/24 up

echo Done.


