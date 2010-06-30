
from lib.flcore import *

def test_compilation():
    rules = loadcsv('rules')
    hosts = loadcsv('hosts')
    hostgroups = loadcsv('hostgroups')
    services = loadcsv('services')
    networks = loadcsv('networks')
    compiled = compile(rules, hosts, hostgroups, services, networks)

    r = [
            ('10.0.0.1', ('IPv4', None), '10.0.8.8', 'TCP', 'ACCEPT', '0'),
            ('10.0.0.1', ('IPv4', None), '10.0.8.8', '443', 'ACCEPT', '0'),
            ('10.0.0.2', ('IPv4', None), '10.0.0.4', ('IPv4', None), 'DROP', '3'),
            ('10.0.0.2', ('IPv6', None), '10.0.0.4', ('IPv6', None), 'DROP', '3'),
            ('10.0.0.1', ('IPv4', None), '10.0.0.3', 'TCP', 'ACCEPT', '0'),
            ('10.0.0.1', ('IPv4', None), '10.0.0.3', '80', 'ACCEPT', '0'),
            ('10.0.0.4', ('IPv4', None), '10.0.0.0', 'TCP', 'ACCEPT', '2'),
            ('10.0.0.4', ('IPv4', None), '10.0.0.0', '22', 'ACCEPT', '2'),
            ('10.0.0.4', ('IPv4', None), '255.0.0.0', 'TCP', 'ACCEPT', '2'),
            ('10.0.0.4', ('IPv4', None), '255.0.0.0', '22', 'ACCEPT', '2'),
            (['10.0.0.4'], ('IPv4', None), ['10.0.0.4'], 'UDP', 'ACCEPT', '0'),
            (['10.0.0.4'], ('IPv4', None), ['10.0.0.4'], '123', 'ACCEPT', '0'),
            (['10.0.0.4'], ('IPv4', None), ['10.0.0.2'], 'UDP', 'ACCEPT', '0'),
            (['10.0.0.4'], ('IPv4', None), ['10.0.0.2'], '123', 'ACCEPT', '0'),
            (['10.0.0.2'], ('IPv4', None), ['10.0.0.4'], 'UDP', 'ACCEPT', '0'),
            (['10.0.0.2'], ('IPv4', None), ['10.0.0.4'], '123', 'ACCEPT', '0'),
            (['10.0.0.2'], ('IPv4', None), ['10.0.0.2'], 'UDP', 'ACCEPT', '0'),
            (['10.0.0.2'], ('IPv4', None), ['10.0.0.2'], '123', 'ACCEPT', '0')
        ]

    assert compiled == r, "Compilation incorrect"
