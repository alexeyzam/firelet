#!/bin/bash



for h in BorderFW InternalFW Server001 Smeagol;
do
	sudo lxc-stop --name $h
done

for br in firenet rivendell production_net shire;
do
    sudo ifconfig $br down
    sudo brctl delbr $br
done



