from lib import mailer

from lib.flcore import *
import shutil

#TODO: migration to network objects
#TODO: parallel SSH
#TODO: SSH check and deployment

## FireSet testing

def test_gitfireset():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = GitFireSet(repodir='test/firewalltmp')
    return #FIXME
    assert fs.save_needed() == False
    fs.save()
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False
    fs.rollback(2)
    assert fs.save_needed() == False
    vl = version_list()
    # assert
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'network'):
        fs.delete(t, 1)
        tmp = len(fs.__dict__[t])
        assert fs.save_needed() == True
        assert tmp == len(fs.__dict__[t]) - 1
    fs.save()
    assert fs.save_needed() == False
    tmp = fs.rules
    fs.rule_moveup(2)
    assert fs.save_needed() == True
    assert tmp != fs.rules
    fs.rule_movedown(1)
    assert tmp == fs.rules



def test_dumbfireset():

    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = DumbFireSet(repodir='test/firewalltmp')
    assert fs.save_needed() == False
    fs.save()
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False
    fs.rollback(2)
    assert fs.save_needed() == False
    vl = fs.version_list()
    # assert
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'networks'):
        tmp = len(fs.__dict__[t])
        fs.delete(t, 0)
        assert fs.save_needed() == True, t
        assert tmp == len(fs.__dict__[t]) + 1, t
    fs.save()
    assert fs.save_needed() == False
    orig_rules = fs.rules[:] # copy
    fs.rule_moveup(2)
    assert fs.save_needed() == True
    assert orig_rules != fs.rules
    fs.rule_movedown(1)
    assert orig_rules == fs.rules

    fs.rule_movedown(1)
    assert orig_rules != fs.rules
    assert fs.save_needed() == True
    fs.reset()
    assert fs.save_needed() == False
    assert orig_rules == fs.rules




##

def test_ip_parsing():
    for x in xrange(0, 256):
        ipaddr = "%d.%d.%d.%d" % (x, x, x, x)
        assert long_to_dot(dot_to_long(ipaddr)) == ipaddr


def test_flattening():

    hg2 = HostGroup(childs=[Host('h', 'b', 'i')])
    hg3 = HostGroup(childs=[Network('n', 'b', 'c'), hg2])
    hg = HostGroup(childs=[hg2, hg3])
    assert ['h', 'h'] == [h.name for h in hg.hosts()]
    assert ['n'] == [h.name for h in hg.networks()], repr(hg.networks())

def test_contain():
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '28')
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '24')
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '8')


def test_compilation():
    rules = loadcsv('rules', d='test')
    hosts = loadcsv('hosts', d='test')
    hostgroups = loadcsv('hostgroups', d='test')
    services = loadcsv('services', d='test')
    networks = loadcsv('networks', d='test')
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



    assert compiled == r, "Compilation incorrect" + repr(compiled)

def test_select_rules():
    rules = loadcsv('rules', d='test')
    hosts = loadcsv('hosts', d='test')
    hostgroups = loadcsv('hostgroups', d='test')
    services = loadcsv('services', d='test')
    networks = loadcsv('networks', d='test')
    compiled = compile(rules, hosts, hostgroups, services, networks)

    rd = select_rules(hosts, compiled)
    assert rd == {'Bilbo': {'eth0': [['-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.8.8 --dport 443 -j ACCEPT', '-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.3 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.2 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 -j ACCEPT']]},
                                       'Fangorn': {'eth1': [['-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.3 --dport 80 -j ACCEPT']]}, 'Gandalf': {'eth1': [['-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.8.8 --dport 443 -j ACCEPT']], 'eth0': [['-A FORWARD -s 10.0.0.2 -d 10.0.0.4 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.0.0.2 -d 10.0.0.4 -j DROP', '-A FORWARD -p tcp -s 10.0.0.4 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 10.0.0.4 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT', '-A FORWARD -p udp -s 10.0.0.4 -d 10.0.0.4 --dport 123 -j ACCEPT']]},
                                       'Smeagol': {'eth0': [['-A FORWARD -s 10.0.0.2 -d 10.0.0.4 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.0.0.2 -d 10.0.0.4 -j DROP', '-A FORWARD -p tcp -s 10.0.0.1 -d 10.0.0.2 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.0.0.2 -d 10.0.0.1 -m multiport --dport 143,585,993 -j ACCEPT']]}}


