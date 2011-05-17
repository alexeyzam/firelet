#!/bin/bash

# Setup and run lxc virtual machines

LXCROOT=~/lxc

echo "Creating bridges..."
br=br0
	sudo brctl addbr $br
	sudo brctl setfd $br 0
	sudo ifconfig $br promisc up
	aterm +sb -bg white -fg black -title Net:$br -e sudo tcpdump -npqi $br &

#sudo ifconfig firenet 88.88.88.1/24 up

echo "Starting LXC machines..."
pushd ~
for h in BorderFW InternalFW Server001 Smeagol Firelet;
do
	aterm +sb -bg white -fg black -title Host:$h -e sudo lxc-start -n $h -f $LXCROOT/$h/config &
done

popd

echo "Setting up host routing..."

sudo sysctl net.ipv4.conf.all.forwarding=1
sudo iptables -D POSTROUTING -t nat -o wlan1 -j MASQUERADE
sudo iptables -A POSTROUTING -t nat -o wlan1 -j MASQUERADE

sudo ifconfig br0 10.66.1.5 promisc up
sudo route add -net 10.66.1.0/24 dev br0
sudo route add -net 10.66.2.0/24 dev br0
sudo route add -net 172.16.2.0/24 dev br0

echo ""
sleep 3
for i in $(sudo ip a s | awk '/vet.*BROA/ {print $2}' | tr -d ':');
do
	echo "Monitoring $i..."
	aterm +sb -bg white -fg black -title If:$i -e sudo tcpdump -npqi $i &
done


echo "Done"
