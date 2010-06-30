from lib import mailer

from lib.flcore import *

def test_compilation():
    rules = loadcsv('rules')
    hosts = loadcsv('hosts')
    hostgroups = loadcsv('hostgroups')
    services = loadcsv('services')
    networks = loadcsv('networks')
    compiled = compile(rules, hosts, hostgroups, services, networks)


    r = ['-A x -p tcp -s 10.0.0.1  -d 10.0.8.8 -m multiport --sport 443 -j ACCEPT',
             '-A x  -s 10.0.0.2  -d 10.0.0.4  -j LOG-3',
             '-A x  -s 10.0.0.2  -d 10.0.0.4  -j DROP',
             '-A x -p tcp -s 10.0.0.1  -d 10.0.0.3 -m multiport --sport 80 -j ACCEPT',
             '-A x -p tcp -s 10.0.0.4  -d 10.0.0.0 -m multiport --sport 22 -j LOG-2',
             '-A x -p tcp -s 10.0.0.4  -d 255.0.0.0 -m multiport --sport 22 -j LOG-2',
             '-A x -p tcp -s 10.0.0.4  -d 10.0.0.0 -m multiport --sport 22 -j ACCEPT',
             '-A x -p tcp -s 10.0.0.4  -d 255.0.0.0 -m multiport --sport 22 -j ACCEPT',
             "-A x -p udp -s ['10.0.0.4']  -d ['10.0.0.4'] -m multiport --sport 123 -j ACCEPT",
             "-A x -p udp -s ['10.0.0.4']  -d ['10.0.0.2'] -m multiport --sport 123 -j ACCEPT",
             "-A x -p udp -s ['10.0.0.2']  -d ['10.0.0.4'] -m multiport --sport 123 -j ACCEPT",
             "-A x -p udp -s ['10.0.0.2']  -d ['10.0.0.2'] -m multiport --sport 123 -j ACCEPT"]



    assert compiled == r, "Compilation incorrect"
