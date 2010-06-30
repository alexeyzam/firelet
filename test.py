from lib import mailer

from lib.flcore import *

def test_compilation():
    rules = loadcsv('rules')
    hosts = loadcsv('hosts')
    hostgroups = loadcsv('hostgroups')
    services = loadcsv('services')
    networks = loadcsv('networks')
    compiled = compile(rules, hosts, hostgroups, services, networks)

    r =['-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.8.8 --dport 443 -j ACCEPT',
'-A FORWARD -s 10.0.0.2 -d 10.0.0.4 --log-level 3 --log-prefix NoSmeagol -j LOG',
'-A FORWARD -s 10.0.0.2 -d 10.0.0.4 -j DROP',
'-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.3 --dport 80 -j ACCEPT',
'-A FORWARD -p tcp -s 10.0.0.4 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG',
'-A FORWARD -p tcp -s 10.0.0.4 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT',
'-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.2 --dport 6660:6669 -j ACCEPT',
'-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG',
'-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 -j ACCEPT',
'-A FORWARD -p udp -s 10.0.0.4 -d 10.0.0.4 --dport 123 -j ACCEPT',
'-A FORWARD --log-level 1 --log-prefix default -j LOG',
'-A FORWARD -j DROP']


    assert compiled == r, "Compilation incorrect"
