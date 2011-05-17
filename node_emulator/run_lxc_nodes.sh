#!/bin/bash

# Setup and run lxc virtual machines

LXCROOT=~/lxc

echo "Creating bridges..."
for br in firenet rivendell production_net shire;
do
	sudo brctl addbr $br
	sudo brctl setfd $br 0
	sudo ifconfig $br promisc up
	aterm +sb -bg white -fg black -title Net:$br -e sudo tcpdump -npqi $br &
done

sudo ifconfig firenet 88.88.88.1/24 promisc up

echo "Starting LXC machines..."
pushd ~
for h in BorderFW InternalFW Server001 Smeagol;
do
	aterm +sb -bg white -fg black -title Host:$h -e sudo lxc-start -n $h -f $LXCROOT/$h/config &  
done

popd

echo "Setting up host routing..."
sudo route add -net 10.66.1.0/24 gw 88.88.88.88
sudo route add -net 10.66.2.0/24 gw 88.88.88.88
sudo route add -net 172.16.2.0/24 dev firenet
sudo sysctl net.ipv4.conf.all.forwarding=1
sudo iptables -D POSTROUTING -t nat -o wlan1 -j MASQUERADE
sudo iptables -A POSTROUTING -t nat -o wlan1 -j MASQUERADE

echo

sleep 3
for i in $(sudo ip a s | awk '/vet.*BROA/ {print $2}' | tr -d ':');
do
	echo "Monitoring $i..."
	aterm +sb -bg white -fg black -title If:$i -e sudo tcpdump -npqi $i &
done


echo "Done"
