!#/bin/bash
for f in new-iptables-save-*;
do
 echo $f
 sudo iptables -Z
 sudo iptables-restore $f
 sudo iptables-save > processed-$f
done
sudo iptables -F
sudo iptables -Z


