from lib import mailer

from lib.flcore import *
import shutil
from lib.flssh import SSHConnector
from lib.flmap import draw_svg_map
from nose.tools import assert_raises, with_setup

import logging
log = logging.getLogger()

#TODO: migration to network objects
#TODO: parallel SSH
#TODO: SSH check and deployment

def setup_dir():
    shutil.rmtree('/tmp/firelet', True)
    shutil.copytree('test/', '/tmp/firelet')

def teardown_dir():
    shutil.rmtree('/tmp/firelet', True)



# #  Testing flssh module without network interaction # #

def setup_dummy_flssh():
    import pxssh
    setup_dir()
    def dummy_sl(self, a):
        n = self.my_hostname
        log.debug( "Sending '%s' to bogus '%s'" % (a, n))
        if 'save' in a:
            self.before = open('test/iptables-save-%s' % n).read()
        else:
            self.before = open('test/ip-addr-show-%s' % n).read()

    pxssh.login = pxssh.isalive = pxssh.prompt = pxssh.logout = lambda *x: True
    pxssh.sendline = dummy_sl
    globals()['pxssh'] = pxssh

def teardown_flssh():
    teardown_dir()


#@with_setup(setup_dummy_flssh)
#def test_get_confs_local_dummy():
#    d  = flssh.get_confs( {'localhost':['127.0.0.1']} )
#    assert d == {'localhost': [None, '127.0.0.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'teredo': (None, 'fe80::ffff:ffff:ffff/64'), 'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}]}


#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs3():
#    fs = DumbFireSet(repodir='/tmp/firelet')
#    fs._get_confs()
#    assert fs._remote_confs == {'Bilbo': [None, '10.66.2.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('10.66.1.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Fangorn': [None, '10.66.2.2', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.2.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Gandalf': [None, '10.66.1.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.1.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('172.16.2.223/24', 'fe80::3939:3939:3939:3939/64')}], 'Smeagol': [None, '10.66.1.3', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.1.3/24', 'fe80::3939:3939:3939:3939/64')}]}



#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs4():
#    fs = DumbFireSet(repodir='/tmp/firelet')
#    fs._get_confs()
#    fs._check_ifaces()
#    rd = fs.compile_dict(hosts=fs.hosts)





def test_clean():
    """Test user input cleanup"""
    s = clean(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_')
    assert s == ' !#$%&()*+,-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'


# #  User management testing  # #

@with_setup(setup_dir, teardown_flssh)
def test_user_management():
    u = Users(d='/tmp/firelet')
    u.create('Totoro', 'admin', 'rawr', 'totoro@nowhere.forest')
    assert_raises(Exception,  u.create, 'Totoro', '', '', '')
    u.validate('Totoro', 'rawr')
    assert_raises(Exception, u.validate, 'Totoro', 'booo')
    u.update('Totoro', role='user')
    assert u._users['Totoro'][0] == 'user'
    u.update('Totoro', pwd='')
    u.update('Totoro', email='')
    assert u._users['Totoro'][2] == ''
    assert_raises(Exception, u.update, 'Totoro2', 'email=""')
    u.delete('Totoro')
    assert_raises(Exception,  u.delete, 'Totoro')


# # File save/load # #

@with_setup(setup_dir, teardown_flssh)
def test_load_save_hosts():
    lines = open('/tmp/firelet/hosts.csv', 'r').readlines()
    content = [x.strip() for x in lines]
    content = filter(None, content)
    h = Hosts(d='/tmp/firelet')
    h.save()
    lines = open('/tmp/firelet/hosts.csv', 'r').readlines()
    content2 = [x.strip() for x in lines]
    content2 = filter(None, content2)
    h2 = Hosts(d='/tmp/firelet')
    assert content == content2, "load/save hosts loop failed:\n\n%s\n\n%s\n\n" \
        % (repr(content), repr(content2))
    assert repr(h) == repr(h2), "load/save hosts loop failed"

@with_setup(setup_dir, teardown_flssh)
def test_load_save_csv():
    h = loadcsv('rules', d='/tmp/firelet')
    savecsv('rules', h, d='/tmp/firelet')
    h2 = loadcsv('rules', d='/tmp/firelet')
    assert h == h2, "load/save hosts loop failed"


# #  FireSet testing # #

@with_setup(setup_dir, teardown_flssh)
def test_gitfireset_simple():
    fs = GitFireSet(repodir='/tmp/firelet')
    assert fs.save_needed() == False
    fs.save('test')
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False


@with_setup(setup_dir, teardown_flssh)
def test_gitfireset_long():
    fs = GitFireSet(repodir='/tmp/firelet')
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'networks'):
        fs.delete(t, 1)
        assert fs.save_needed() == True, "save_needed non set when deleting item 1 from %s" % t
        fs.save("%s: n.1 deleted" % t)
        assert fs.save_needed() == False
    fs.rule_moveup(2)
    assert fs.save_needed() == True
    fs.rule_movedown(1)
    fs.save('movedown1')
    fs.rule_movedown(2)
    fs.save('movedown2')
    fs.rule_movedown(3)
    fs.save('movedown3')
    vl = fs.version_list()
    log.debug('version_list: %s' % repr(vl))
    assert zip(*vl)[2] == (['movedown3'], ['movedown2'], ['networks: n.1 deleted'], ['services: n.1 deleted'],
                            ['hostgroups: n.1 deleted'], ['hosts: n.1 deleted'], ['rules: n.1 deleted'])
    fs.rollback(2)
    assert fs.save_needed() == False
    vl = fs.version_list()
    log.debug('version_list: %s' % repr(vl))
    assert zip(*vl)[2] == (['networks: n.1 deleted'], ['services: n.1 deleted'], ['hostgroups: n.1 deleted'],
                            ['hosts: n.1 deleted'], ['rules: n.1 deleted'])

@with_setup(setup_dir, teardown_flssh)
def test_gitfireset_check_ifaces():
    fs = GitFireSet(repodir='/tmp/firelet')
    d = {'Bilbo': {'filter': [], 'ip_a_s': {'eth1': ('10.66.2.1', None), 'eth0': ('10.66.1.2', None)}},
            'Fangorn': {'filter': [], 'ip_a_s': {'eth0': ('10.66.2.2', None)}},
            'Gandalf': {'filter': [], 'ip_a_s': {'eth1': ('10.66.1.1', None), 'eth0': ('172.16.2.223', None)}},
            'Smeagol': {'filter': [], 'ip_a_s': {'eth0': ('10.66.1.3', None)}} }
    fs._remote_confs = {}
    for n, v in d.iteritems():
        fs._remote_confs[n] = Bunch(filter=v['filter'], ip_a_s=v['ip_a_s'])
    fs._check_ifaces()




#@with_setup(setup_dir, teardown_flssh)
#def test_dumbfireset():
#    fs = DumbFireSet(repodir='/tmp/firelet')
#    assert fs.save_needed() == False
#    fs.save('save')
#    assert fs.save_needed() == False
#    fs.reset()
#    assert fs.save_needed() == False
#    fs.rollback(2)
#    assert fs.save_needed() == False
#    vl = fs.version_list()
#    # assert
#    for t in ('rules', 'hosts', 'hostgroups', 'services', 'networks'):
#        tmp = len(fs.__dict__[t])
#        fs.delete(t, 0)
#        assert fs.save_needed() == True, t
#        assert tmp == len(fs.__dict__[t]) + 1, t
#    fs.save('test')
#    assert fs.save_needed() == False
#    orig_rules = fs.rules[:] # copy
#    fs.rule_moveup(2)
#    assert fs.save_needed() == True
#    assert orig_rules != fs.rules
#    fs.rule_movedown(1)
#    assert orig_rules == fs.rules
#
#    fs.rule_movedown(1)
#    assert orig_rules != fs.rules
#    assert fs.save_needed() == True
#    fs.reset()
#    assert fs.save_needed() == False
#    assert orig_rules == fs.rules




# #  IP address handling  # #


def test_network_update():
    assert Network(['','255.255.255.255',8]).ip_addr == '255.0.0.0'
    assert Network(['','255.255.255.255',16]).ip_addr == '255.255.0.0'
    assert Network(['','255.255.255.255',24]).ip_addr == '255.255.255.0'
    assert Network(['','255.255.255.255',27]).ip_addr == '255.255.255.224'
    assert Network(['','255.255.255.255',28]).ip_addr == '255.255.255.240'
    assert Network(['','255.255.255.255',29]).ip_addr == '255.255.255.248'
    assert Network(['','255.255.255.255',30]).ip_addr == '255.255.255.252'


def test_contain_nets():
    assert Network(['', '255.255.255.255', 16]) in Network(['', '255.255.255.255', 8])
    assert Network(['', '255.255.255.255', 16]) in Network(['', '255.255.255.255', 16])
    assert Network(['', '255.255.255.255', 8]) not in Network(['', '255.255.255.255', 16])
    assert Network(['', '1.0.0.0', 17]) in Network(['', '1.0.0.0', 16])
    assert Network(['', '1.0.0.0', 16]) in Network(['', '1.0.0.0', 16])
    assert Network(['', '1.0.0.0', 15]) not in Network(['', '1.0.0.0', 16])
    assert Network(['', '42.42.42.42', 15]) not in Network(['','42.42.42.42', 16])
    assert Network(['', '42.42.42.42', 16]) in Network(['','42.42.42.42', 16])
    assert Network(['', '42.42.42.42', 17]) in Network(['','42.42.42.42', 16])

def test_contain_hosts():
    assert Host(['h', 'eth0', '1.1.1.1', 24, '1', '1', '1', [] ]) in Network(['h', '1.1.1.0', 28])
    assert Host(['h', 'eth0', '1.1.1.15',24, '1', '1', '1', [] ]) in Network(['h', '1.1.1.0', 28])
    assert Host(['h', 'eth0', '1.1.1.16',24, '1', '1', '1', [] ]) not in Network(['h', '1.1.1.0', 28])
    assert Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ]) in Network(['h', '1.1.1.0', 24])
    assert Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ]) in Network(['h', '1.1.1.0', 8])
    assert Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ]) not in Network(['h', '1.1.2.0', 24])
    assert Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ]) not in Network(['h', '10.1.1.0', 8])

def test_compare():
    from netaddr import IPNetwork
    for x in xrange(0, 32):
        n=IPNetwork('255.1.1.1/%d' % x)
        ok = n.network
        mine = Network(['','255.1.1.1', x]).ip_addr
        log.debug( 'ok: %s mine: %s len: %d' % (ok,  mine, x))
        assert str(mine) == str(ok)


def test_flattening():
    hg2 = HostGroup(childs=[Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ])])
    hg3 = HostGroup(childs=[Network(['n', '2.2.2.0', 24]), hg2])
    hg = HostGroup(childs=[hg2, hg3])
    assert ['h', 'h'] == [h.name for h in hg.hosts()]
    assert ['n'] == [h.name for h in hg.networks()], repr(hg.networks())


# # Rule compliation and deployment testing # #

@with_setup(setup_dir, teardown_flssh)
def test_compilation():
    fs = GitFireSet(repodir='/tmp/firelet')
    compiled = fs.compile()

    r = ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT', '-A FORWARD --log-level 1 --log-prefix default -j LOG', '-A FORWARD -j DROP']

    assert compiled == r, "Compilation incorrect" + repr(compiled)

@with_setup(setup_dir, teardown_flssh)
def test_select_rules():
    fs = GitFireSet(repodir='/tmp/firelet')
    rd = fs.compile_dict()
    r = {'Bilbo': {'eth1': [], 'eth0': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']}, 'Fangorn': {'eth0': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT']}, 'Gandalf': {'eth1': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT'], 'eth0': ['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT']}, 'Smeagol': {'eth0': ['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']}}
    assert rd == r,  "select_rules generates:\n%s" % repr(rd)

@with_setup(setup_dir, teardown_flssh)
def test_compile_rules():
    fs = GitFireSet(repodir='/tmp/firelet')
    rd = fs.compile_rules()
    r = {'Bilbo': ['-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 --log-level 0 --log-prefix BG_https -j LOG', '-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 --log-level 0 --log-prefix http_ok -j LOG', '-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A INPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A INPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 -j ACCEPT', '-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 --log-level 0 --log-prefix irc -j LOG', '-A OUTPUT -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A INPUT -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A INPUT -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP'], 'Gandalf': ['-A INPUT -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 --log-level 0 --log-prefix BG_https -j LOG', '-A INPUT -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A INPUT -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A INPUT -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A OUTPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A OUTPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 -j ACCEPT', '-A INPUT -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 --log-level 0 --log-prefix ntp -j LOG', '-A INPUT -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT', '-A OUTPUT -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 --log-level 0 --log-prefix ntp -j LOG', '-A OUTPUT -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP'], 'Fangorn': ['-A INPUT -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 --log-level 0 --log-prefix http_ok -j LOG', '-A INPUT -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A INPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A INPUT -p tcp -s 172.16.2.223 -d 10.66.2.0/255.255.255.0 --dport 22 -j ACCEPT', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP'], 'Smeagol': ['-A OUTPUT -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A OUTPUT -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A INPUT -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 --log-level 0 --log-prefix irc -j LOG', '-A INPUT -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A OUTPUT -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A OUTPUT -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP', '-A INPUT --log-level 1 --log-prefix default -j LOG', '-A INPUT -j DROP']}

    assert rd == r,  "compile_rules generates:\n%s" % repr(rd)
    assert isinstance(rd, dict)    #FIXME: enable testing


#@with_setup(setup_dir, teardown_flssh)
#def test_deployment():
#    """Test host connectivity is required"""
#    fs = GitFireSet(repodir='/tmp/firelet')
#    fs.deploy()

@with_setup(setup_dir, teardown_flssh)
def test_svg_map():
    fs = GitFireSet(repodir='/tmp/firelet')
    svg = draw_svg_map(fs)
    assert 'DOCTYPE svg PUBLIC' in svg, "No SVG output?"
    assert 'rivendell' in svg, "No rivendell in the map"

# #  Test JSON lib  # #

def json_loop(obj):
    return json.loads(json.dumps(obj, sort_keys=True))

def test_json1():
    d = {'string':'string', 's2':6, 's3':7.7, 's4':True, 's5':False}
    assert d == json_loop(d)

def test_json2():
    d = {'string':'string', 's2':6, 's3':7, 's4':True, 's5':False}
    assert d == json_loop(d)
    assert json.dumps(d) == '{"s3": 7, "s2": 6, "string": "string", "s5": false, "s4": true}'

def test_json3():
    d = {'d1':{'d2':{'d3':{'d4':{'d5':{'this is getting':'boring'}}}}}}
    assert d == json_loop(d)
    assert json.dumps(d) == '{"d1": {"d2": {"d3": {"d4": {"d5": {"this is getting": "boring"}}}}}}'

def test_json4():
    d = [x for x in xrange(42)]
    assert d == json_loop(d)

def test_json5():
    """Keys are casted to strings, integers are not preserved"""
    d = {1:1, 2:2, 3:3}
    assert d != json_loop(d)

def test_json_files():
    shutil.rmtree('/tmp/firelet', True)
    shutil.copytree('test/', '/tmp/firelet')
    d = {'d1':{'d2':{'d3':{'d4':{'d5':{'this is getting':'boring'}}}}}}
    savejson('jfile', d, d='/tmp/firelet')
    nd = loadjson('jfile', d='/tmp/firelet')
    assert d == nd

# #  Test cartesian product  # #

def test_product_2_6():
    from itertools import product

    assert tuple(product([1,2,3,4,5,'O HI'],['a','b','c','d',42])) == (
        (1, 'a'), (1, 'b'), (1, 'c'), (1, 'd'), (1, 42), (2, 'a'), (2, 'b'), (2, 'c'), (2, 'd'), (2, 42),
        (3, 'a'), (3, 'b'), (3, 'c'), (3, 'd'), (3, 42), (4, 'a'), (4, 'b'), (4, 'c'), (4, 'd'), (4, 42),
        (5, 'a'), (5, 'b'), (5, 'c'), (5, 'd'), (5, 42), ('O HI', 'a'), ('O HI', 'b'), ('O HI', 'c'),
        ('O HI', 'd'), ('O HI', 42))


def test_product_2_5():

    def product(*args, **kwds):
        """List cartesian product - not available in Python 2.5"""
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    assert tuple(product([1,2,3,4,5,'O HI'],['a','b','c','d',42])) == (
        (1, 'a'), (1, 'b'), (1, 'c'), (1, 'd'), (1, 42), (2, 'a'), (2, 'b'), (2, 'c'), (2, 'd'), (2, 42),
        (3, 'a'), (3, 'b'), (3, 'c'), (3, 'd'), (3, 42), (4, 'a'), (4, 'b'), (4, 'c'), (4, 'd'), (4, 42),
        (5, 'a'), (5, 'b'), (5, 'c'), (5, 'd'), (5, 42), ('O HI', 'a'), ('O HI', 'b'), ('O HI', 'c'),
        ('O HI', 'd'), ('O HI', 42))

def test_bunch():
    from lib.flutils import Bunch
    b = Bunch( c=42, a=3, b='44', _a=0)
    b2 = Bunch(a='3', b='44', _a='0')
    assert repr(b) == "{'a': 3, 'c': 42, 'b': '44', '_a': 0}", "Bunch repr is incorrect: %s" % repr(b)
    assert b.c == 42



