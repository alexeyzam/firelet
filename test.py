# Firelet - Distributed firewall management.
# Copyright (C) 2010 Federico Ceratto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from firelet import mailer

from firelet.flcore import *
import shutil
from firelet.flssh import MockSSHConnector
from firelet.flmap import draw_svg_map
from firelet.flutils import flag, Bunch
from nose.tools import assert_raises, with_setup
from pprint import pformat

from firelet import cli
from firelet.cli import main as cli_main

import logging
log = logging.getLogger()

#TODO: migration to network objects
#TODO: parallel SSH
#TODO: SSH check and deployment

def setup_dir():
    shutil.rmtree('/tmp/firelet_test', True)
    shutil.copytree('test/', '/tmp/firelet_test')


def teardown_dir():
    shutil.rmtree('/tmp/firelet_test', True)



# #  Testing flssh module without network interaction # #

#def setup_dummy_flssh():
#    """Patch the pxssh module to use files instead of performing network interaction"""
#    import pxssh
#    setup_dir()
#    def dummy_sl(self, a):
#        n = self.my_hostname
#        log.debug( "Sending '%s' to bogus '%s'" % (a, n))
#        if 'save' in a:
#            self.before = open('test/iptables-save-%s' % n).read()
#        else:
#            self.before = open('test/ip-addr-show-%s' % n).read()
#
#    pxssh.login = pxssh.isalive = pxssh.prompt = pxssh.logout = lambda *x: True
#    pxssh.sendline = dummy_sl
#    globals()['pxssh'] = pxssh
#
#def teardown_flssh():
#    teardown_dir()
#
#
#@with_setup(setup_dummy_flssh)
#def test_get_confs_local_dummy():
#    from firelet.flssh import SSHConnector, MockSSHConnector
#
#    sshconn = SSHConnector(targets={'localhost':['127.0.0.1']} )
#    d  = sshconn.get_confs( )
#    assert 'localhost' in d
#    assert d['localhost']
#    assert d == {'localhost': [None, '127.0.0.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'teredo': (None, 'fe80::ffff:ffff:ffff/64'), 'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}]}




#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs3():
#    fs = DumbFireSet(repodir='/tmp/firelet_test')
#    fs._get_confs()
#    assert fs._remote_confs == {'Bilbo': [None, '10.66.2.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('10.66.1.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Fangorn': [None, '10.66.2.2', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.2.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Gandalf': [None, '10.66.1.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.1.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('172.16.2.223/24', 'fe80::3939:3939:3939:3939/64')}], 'Smeagol': [None, '10.66.1.3', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.1.3/24', 'fe80::3939:3939:3939:3939/64')}]}



#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs4():
#    fs = DumbFireSet(repodir='/tmp/firelet_test')
#    fs._get_confs()
#    fs._check_ifaces()
#    rd = fs.compile_dict(hosts=fs.hosts)





def test_clean():
    """Test user input cleanup"""
    s = clean(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_')
    assert s == ' !#$%&()*+,-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'


# #  User management testing  # #

@with_setup(setup_dir, teardown_dir)
def test_user_management():
    u = Users(d='/tmp/firelet_test')
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

@with_setup(setup_dir, teardown_dir)
def test_load_save_hosts():
    lines = open('/tmp/firelet_test/hosts.csv', 'r').readlines()
    content = [x.strip() for x in lines]
    content = filter(None, content)
    h = Hosts(d='/tmp/firelet_test')
    h.save()
    lines = open('/tmp/firelet_test/hosts.csv', 'r').readlines()
    content2 = [x.strip() for x in lines]
    content2 = filter(None, content2)
    h2 = Hosts(d='/tmp/firelet_test')
    assert content == content2, "load/save hosts loop failed:\n\n%s\n\n%s\n\n" \
        % (repr(content), repr(content2))
    assert repr(h) == repr(h2), "load/save hosts loop failed"

@with_setup(setup_dir, teardown_dir)
def test_load_save_csv():
    h = loadcsv('rules', d='/tmp/firelet_test')
    savecsv('rules', h, d='/tmp/firelet_test')
    h2 = loadcsv('rules', d='/tmp/firelet_test')
    assert h == h2, "load/save hosts loop failed"


# #  FireSet testing # #

@with_setup(setup_dir, teardown_dir)
def test_gitfireset_simple():
    fs = GitFireSet(repodir='/tmp/firelet_test')
    assert fs.save_needed() == False
    fs.save('test')
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False


@with_setup(setup_dir, teardown_dir)
def test_gitfireset_long():
    fs = GitFireSet(repodir='/tmp/firelet_test')
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'networks'):
        fs.delete(t, 1)
#        assert fs.save_needed() == True, "save_needed non set when deleting item 1 from %s" % t
        fs.save("%s: n.1 deleted" % t)
        assert fs.save_needed() == False
    fs.rules.moveup(2)
#    assert fs.save_needed() == True
    fs.rules.movedown(1)
    fs.save('movedown1')
    fs.rules.movedown(2)
    fs.save('movedown2')
    fs.rules.movedown(3)
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

@with_setup(setup_dir, teardown_dir)
def test_gitfireset_check_ifaces():
    fs = GitFireSet(repodir='/tmp/firelet_test')
    d = {'Bilbo': {'filter': [], 'ip_a_s': {'eth1': ('10.66.2.1', None), 'eth0': ('10.66.1.2', None)}},
            'Fangorn': {'filter': [], 'ip_a_s': {'eth0': ('10.66.2.2', None)}},
            'Gandalf': {'filter': [], 'ip_a_s': {'eth1': ('10.66.1.1', None), 'eth0': ('172.16.2.223', None)}},
            'Smeagol': {'filter': [], 'ip_a_s': {'eth0': ('10.66.1.3', None)}} }
    fs._remote_confs = {}
    for n, v in d.iteritems():
        fs._remote_confs[n] = Bunch(filter=v['filter'], ip_a_s=v['ip_a_s'])
    fs._check_ifaces()


@with_setup(setup_dir, teardown_dir)
def test_gitfireset_sibling_names():
    fs = GitFireSet(repodir='/tmp/firelet_test')
    names = ['AllSystems', 'Bilbo:eth0', 'Bilbo:eth1', 'Clients', 'Fangorn:eth0', 'Gandalf:eth0', \
    'Gandalf:eth1', 'SSHnodes', 'Servers', 'Smeagol:eth0', 'WebServers']
    assert fs.list_sibling_names() == names, "list_sibling_names generating incorrect output"


#@with_setup(setup_dir, teardown_dir)
#def test_dumbfireset():
#    fs = DumbFireSet(repodir='/tmp/firelet_test')
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
#    fs.rules.moveup(2)
#    assert fs.save_needed() == True
#    assert orig_rules != fs.rules
#    fs.rules.movedown(1)
#    assert orig_rules == fs.rules
#
#    fs.rules.movedown(1)
#    assert orig_rules != fs.rules
#    assert fs.save_needed() == True
#    fs.reset()
#    assert fs.save_needed() == False
#    assert orig_rules == fs.rules



@with_setup(setup_dir, teardown_dir)
def test_MockSSHConnector_get_confs():
    sshconn = MockSSHConnector(targets={'localhost':['127.0.0.1']})
    sshconn.repodir = '/tmp/firelet_test'
    d  = sshconn.get_confs( )
    assert 'iptables' in d['localhost'] and 'ip_a_s' in d['localhost']
    assert d['localhost'].iptables != None
    assert d['localhost'].ip_a_s != None
    ok = {'localhost': {'iptables': ['# Generated by iptables-save v1.4.8 on Sun Jul  4 09:28:19 2010', '*nat', ':PREROUTING ACCEPT [8:3712]', ':POSTROUTING ACCEPT [32:3081]', ':OUTPUT ACCEPT [32:3081]', '-A POSTROUTING -o eth3 -j MASQUERADE', 'COMMIT', '# Completed on Sun Jul  4 09:28:19 2010', '# Generated by iptables-save v1.4.8 on Sun Jul  4 09:28:19 2010', '*filter', ':INPUT ACCEPT [4304:2534591]', ':FORWARD ACCEPT [0:0]', ':OUTPUT ACCEPT [4589:2195434]', '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT', '-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT', '-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'COMMIT', '# Completed on Sun Jul  4 09:28:19 2010'], 'ip_a_s': {'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}}}
    for x in d:
        for y in d[x]:
            assert d[x][y] == ok[x][y], "%s incorrect" % d[x][y]
    assert_raises(NotImplementedError,  sshconn._interact, '', 'echo hi')


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_get_confs():
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs._get_confs(keep_sessions=False)
    for hostname, v in fs._remote_confs.iteritems():
        assert isinstance(v, Bunch)
    for h in fs.hosts:
        assert h.hostname in fs._remote_confs, "Missing host %s" % h.hostname

# # Rule compliation and deployment testing # #


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_compile_rules_basic():
    """Compile rules and perform basic testing"""
    return #FIXME
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    rset = fs.compile_rules()
    for hn, d in rset.iteritems():
        for chain,  rules in d.iteritems():
            assert ' -j DROP' in rules or '-j DROP' in rules,  rules


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_compile_rules_full():
    return #FIXME
    fs = GitFireSet(repodir='/tmp/firelet_test')
    rd = fs.compile_rules()

    ok = {'Bilbo': {'FORWARD': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                       ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
                       ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
                       ' -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j LOG --log-level 0 --log-prefix irc',
                       ' -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
                       ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
                       ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
                       ' -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
                       ' -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
                       ' -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
                       ' -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
                       ' -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP',
                       ' -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP'],
           'INPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                     '-i lo -j ACCEPT',
                     '-i eth1  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
                     ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
                     '-i eth0  -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j LOG --log-level 2 --log-prefix imap',
                     ' -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT',
                     '-i eth0  -j LOG --log-level 1 --log-prefix default',
                     ' -j DROP',
                     '-i eth1  -j LOG --log-level 1 --log-prefix default',
                     ' -j DROP'],
           'OUTPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                      '-o lo -j ACCEPT',
                      ' -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT',
                      ' -p tcp -s 10.66.2.1 -d 10.66.2.2 --dport 80 -j ACCEPT',
                      ' -j LOG --log-level 1 --log-prefix default',
                      ' -j DROP',
                      ' -j LOG --log-level 1 --log-prefix default',
                      ' -j DROP']},
 'Fangorn': {'FORWARD': ['-j DROP'],
             'INPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                       '-i lo -j ACCEPT',
                       ' -p tcp -s 10.66.2.1 -d 10.66.2.2 --dport 80 -j ACCEPT',
                       '-i eth0  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
                       ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
                       '-i eth0  -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP'],
             'OUTPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                        '-o lo -j ACCEPT',
                        ' -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
                        ' -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
                        ' -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
                        ' -j LOG --log-level 1 --log-prefix default',
                        ' -j DROP']},
 'Gandalf': {'FORWARD': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                         ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
                         ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
                         ' -j LOG --log-level 1 --log-prefix default',
                         ' -j DROP',
                         ' -j LOG --log-level 1 --log-prefix default',
                         ' -j DROP'],
             'INPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                       '-i lo -j ACCEPT',
                       ' -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT',
                       '-i eth1  -s 10.66.1.3 -d 10.66.1.1 -j LOG --log-level 3 --log-prefix NoSmeagol',
                       ' -s 10.66.1.3 -d 10.66.1.1 -j DROP',
                       ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
                       ' -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
                       '-i eth0  -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP',
                       '-i eth1  -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP'],
             'OUTPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                        '-o lo -j ACCEPT',
                        ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
                        ' -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
                        ' -p udp -s 172.16.2.223 -d 10.66.1.3 --dport 123 -j ACCEPT',
                        ' -j LOG --log-level 1 --log-prefix default',
                        ' -j DROP',
                        ' -j LOG --log-level 1 --log-prefix default',
                        ' -j DROP']},
 'Smeagol': {'FORWARD': ['-j DROP'],
             'INPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                       '-i lo -j ACCEPT',
                       ' -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
                       ' -p udp -s 172.16.2.223 -d 10.66.1.3 --dport 123 -j ACCEPT',
                       ' -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
                       '-i eth0  -j LOG --log-level 1 --log-prefix default',
                       ' -j DROP'],
             'OUTPUT': ['-m state --state RELATED,ESTABLISHED -j ACCEPT',
                        '-o lo -j ACCEPT',
                        ' -s 10.66.1.3 -d 10.66.1.1 -j LOG --log-level 3 --log-prefix NoSmeagol',
                        ' -s 10.66.1.3 -d 10.66.1.1 -j DROP',
                        ' -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j LOG --log-level 2 --log-prefix imap',
                        ' -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT',
                        ' -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
                        ' -j LOG --log-level 1 --log-prefix default',
                        ' -j DROP']}}

    for hostname in ok:
        for chain in ok[hostname]:
            for n, my_line in enumerate(rd[hostname][chain]):
                ok_line = ok[hostname][chain][n]
                assert my_line == ok_line, "Incorrect rules in %s chain %s:\ngot [%s]\nexpected [%s]" % (hostname, chain, my_line,  ok_line )


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_build_ipt_restore():
    """Run diff between compiled rules and empty remote confs"""
    return #FIXME
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    rset = fs.compile_rules()
    m = map(fs._build_ipt_restore, rset.iteritems())
    m = dict(m)
    ok = {'Bilbo': ['# Created by Firelet for host Bilbo',
           '*filter',
           '-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
           '-A INPUT -i lo -j ACCEPT',
           '-A INPUT -i eth1  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
           '-A INPUT  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
           '-A INPUT -i eth0  -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j LOG --log-level 2 --log-prefix imap',
           '-A INPUT  -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT',
           '-A INPUT -i eth0  -j LOG --log-level 1 --log-prefix default',
           '-A INPUT  -j DROP',
           '-A INPUT -i eth1  -j LOG --log-level 1 --log-prefix default',
           '-A INPUT  -j DROP',
           '-A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT',
           '-A FORWARD  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
           '-A FORWARD  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
           '-A FORWARD  -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j LOG --log-level 0 --log-prefix irc',
           '-A FORWARD  -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
           '-A FORWARD  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
           '-A FORWARD  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
           '-A FORWARD  -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
           '-A FORWARD  -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
           '-A FORWARD  -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
           '-A FORWARD  -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
           '-A FORWARD  -j LOG --log-level 1 --log-prefix default',
           '-A FORWARD  -j DROP',
           '-A FORWARD  -j LOG --log-level 1 --log-prefix default',
           '-A FORWARD  -j DROP',
           '-A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
           '-A OUTPUT -o lo -j ACCEPT',
           '-A OUTPUT  -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT',
           '-A OUTPUT  -p tcp -s 10.66.2.1 -d 10.66.2.2 --dport 80 -j ACCEPT',
           '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
           '-A OUTPUT  -j DROP',
           '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
           '-A OUTPUT  -j DROP',
           'COMMIT'],
 'Fangorn': ['# Created by Firelet for host Fangorn',
             '*filter',
             '-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A INPUT -i lo -j ACCEPT',
             '-A INPUT  -p tcp -s 10.66.2.1 -d 10.66.2.2 --dport 80 -j ACCEPT',
             '-A INPUT -i eth0  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
             '-A INPUT  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
             '-A INPUT -i eth0  -j LOG --log-level 1 --log-prefix default',
             '-A INPUT  -j DROP',
             '-A FORWARD -j DROP',
             '-A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A OUTPUT -o lo -j ACCEPT',
             '-A OUTPUT  -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
             '-A OUTPUT  -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
             '-A OUTPUT  -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
             '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
             '-A OUTPUT  -j DROP',
             'COMMIT'],
 'Gandalf': ['# Created by Firelet for host Gandalf',
             '*filter',
             '-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A INPUT -i lo -j ACCEPT',
             '-A INPUT  -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT',
             '-A INPUT -i eth1  -s 10.66.1.3 -d 10.66.1.1 -j LOG --log-level 3 --log-prefix NoSmeagol',
             '-A INPUT  -s 10.66.1.3 -d 10.66.1.1 -j DROP',
             '-A INPUT  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
             '-A INPUT  -p udp -s 10.66.2.2 -d 172.16.2.223 --dport 123 -j ACCEPT',
             '-A INPUT -i eth0  -j LOG --log-level 1 --log-prefix default',
             '-A INPUT  -j DROP',
             '-A INPUT -i eth1  -j LOG --log-level 1 --log-prefix default',
             '-A INPUT  -j DROP',
             '-A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A FORWARD  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j LOG --log-level 0 --log-prefix ntp',
             '-A FORWARD  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
             '-A FORWARD  -j LOG --log-level 1 --log-prefix default',
             '-A FORWARD  -j DROP',
             '-A FORWARD  -j LOG --log-level 1 --log-prefix default',
             '-A FORWARD  -j DROP',
             '-A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A OUTPUT -o lo -j ACCEPT',
             '-A OUTPUT  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j LOG --log-level 2 --log-prefix ssh_mgmt',
             '-A OUTPUT  -p tcp -s 10.66.1.1 -d 10.66.2.0/24 --dport 22 -j ACCEPT',
             '-A OUTPUT  -p udp -s 172.16.2.223 -d 10.66.1.3 --dport 123 -j ACCEPT',
             '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
             '-A OUTPUT  -j DROP',
             '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
             '-A OUTPUT  -j DROP',
             'COMMIT'],
 'Smeagol': ['# Created by Firelet for host Smeagol',
             '*filter',
             '-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A INPUT -i lo -j ACCEPT',
             '-A INPUT  -p tcp -s 10.66.2.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT',
             '-A INPUT  -p udp -s 172.16.2.223 -d 10.66.1.3 --dport 123 -j ACCEPT',
             '-A INPUT  -p udp -s 10.66.2.2 -d 10.66.1.3 --dport 123 -j ACCEPT',
             '-A INPUT -i eth0  -j LOG --log-level 1 --log-prefix default',
             '-A INPUT  -j DROP',
             '-A FORWARD -j DROP',
             '-A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT',
             '-A OUTPUT -o lo -j ACCEPT',
             '-A OUTPUT  -s 10.66.1.3 -d 10.66.1.1 -j LOG --log-level 3 --log-prefix NoSmeagol',
             '-A OUTPUT  -s 10.66.1.3 -d 10.66.1.1 -j DROP',
             '-A OUTPUT  -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j LOG --log-level 2 --log-prefix imap',
             '-A OUTPUT  -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT',
             '-A OUTPUT  -p udp -s 10.66.1.3 -d 172.16.2.223 --dport 123 -j ACCEPT',
             '-A OUTPUT  -j LOG --log-level 1 --log-prefix default',
             '-A OUTPUT  -j DROP',
             'COMMIT']}

    for hostname in m:
        for ok_line, my_line in zip(ok[hostname], m[hostname]):
            assert my_line == ok_line, "Incorrect rule built for %s:\ngot [%s]\nexpected [%s]" % (hostname, my_line,  ok_line )


#@with_setup(setup_dir, teardown_dir)
#def test_DemoGitFireSet_diff_table_simple():
#    """Run diff between compiled rules and empty remote confs"""
#    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
#    new_confs = fs.compile_rules()
#    remote_confs = {}
#    dt = fs._diff(remote_confs, new_confs)
#    assert dt == '<p>The firewalls are up to date. No deployment needed.</p>'
    #FIXME:  deployment IS needed


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_extract_iptables_rules():
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs._get_confs(keep_sessions=False)
    rules_d = fs._extract_ipt_filter_rules(fs._remote_confs)
    for hn, rules in rules_d.iteritems():
        assert len(rules) > 12,  rules
        assert len(rules) < 34,  rules
        for rule in rules:
            assert rule not in ('COMMIT', '*filter', '*nat')

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_diff_table_generation_1():
    """Test diff with no changes"""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    diff_dict = fs._diff({}, {})
    assert diff_dict == {}

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_diff_table_generation_2():
    """Test diff with no changes"""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    diff_dict = fs._diff({'Bilbo':['']}, {'Bilbo':['']})
    assert diff_dict == {}

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_diff_table_generation_3():
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    diff_dict = fs._diff({'Bilbo':['old item', 'static item', 'old item2']},
                                   {'Bilbo':['static item', 'new item', 'new item2']})
    assert diff_dict == {'Bilbo': (['new item', 'new item2'], ['old item', 'old item2'])}

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_diff_table_generation_all_fw_removed():
    """Test diff where all the firewalls has been removed.
    An empty diff should be generated."""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs._get_confs(keep_sessions=False)
    existing_rules = fs._extract_ipt_filter_rules(fs._remote_confs)
    diff_dict = fs._diff(existing_rules,   {})
    assert diff_dict == {}, "An empty diff should be generated."

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_diff_table_generation_all_fw_added():
    """Test diff right after all the firewalls has been added.
    An empty diff should be generated."""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs.save('test') #FIXME: shouldn't be required
    comp_rules = fs.compile_rules()
    new_rules = {}
    for hn, b in comp_rules.iteritems():
        li = fs._build_ipt_restore_blocks((hn, b))
        new_rules[hn] = li
    diff_dict = fs._diff({}, new_rules)
    assert diff_dict == {}, "An empty diff should be generated."


# Used during development with test/rebuild.sh #
# to generate new sets of  test files #
#
#@with_setup(setup_dir, teardown_dir)
#def test_DemoGitFireSet_rebuild():
#    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
#    comp_rules = fs.compile_rules()
#    for hn, b in comp_rules.iteritems():
#        li = fs._build_ipt_restore((hn, b))[1]
#        open("test/new-iptables-save-%s" % hn, 'w').write('\n'.join(li)+'\n')


@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_check():
    """Run diff between complied rules and remote confs.
    Given the test files, the check should be ok and require no deployment"""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs.save('test') #FIXME: shouldn't be required
    diff_dict = fs.check()
    assert diff_dict == {},  repr(diff_dict)[:300]

@with_setup(setup_dir, teardown_dir)
def test_DemoGitFireSet_deploy():
    """Run diff between complied rules and remote confs.
    Given the test files, the check should be ok and require no deployment"""
    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
    fs.deploy()
    for h in fs.hosts:
        ok = open('test/iptables-save-%s' % h.hostname).readlines()
        r = open('/tmp/iptables-save-%s-x' % h.hostname).readlines()
        assert len(ok) == len(r) + 4,  len(r)
#        for a, b in zip(ok, r):
#            assert a == b




#@with_setup(setup_dir, teardown_dir)
#def test_DemoGitFireSet_deploy():
#    fs = DemoGitFireSet(repodir='/tmp/firelet_test')
#    dt = fs.deploy()
#    for h in fs.hosts:
#        r = map(str.rstrip, open('/tmp/firelet_test/iptables-save-%s' % h.hostname))
#        ok = map(str.rstrip, open('/tmp/firelet_test/iptables-save-%s-correct' % h.hostname))
#        for a, b in zip(r, ok):
#            assert a == b, "%s differs from %s in iptables-save-%s" % (a, b, h.hostname)
#
#

#@with_setup(setup_dummy_flssh)
#def test_get_confs_local_dummy():
#    from firelet.flssh import SSHConnector, MockSSHConnector
#
#    sshconn = SSHConnector(targets={'localhost':['127.0.0.1']} )
#    d  = sshconn.get_confs( )
#    assert 'localhost' in d
#    assert d['localhost']
#    assert d == {'localhost': [None, '127.0.0.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'teredo': (None, 'fe80::ffff:ffff:ffff/64'), 'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}]}





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


#def test_flattening():
#    hg2 = HostGroup(['name', [Host(['h', 'eth0', '1.1.1.1',24, '1', '1', '1', [] ])], ])
#    hg3 = HostGroup(['name2', [Network(['n', '2.2.2.0', 24]), hg2]])
#    hg = HostGroup(childs=[hg2, hg3])
#    assert ['h', 'h'] == [h.hostname for h in hg.hosts()]
#    assert ['n'] == [h.name for h in hg.networks()], repr(hg.networks())





@with_setup(setup_dir, teardown_dir)
def test_svg_map():
    fs = GitFireSet(repodir='/tmp/firelet_test')
    svg = draw_svg_map(fs)
    assert 'DOCTYPE svg PUBLIC' in svg, "No SVG output?"
    assert 'rivendell' in svg, "No rivendell in the map"


# #  CLI testing # #


class MockSay():
    def __init__(self):
        self.li = []
    def __call__(self, s):
        self.li.append(s)
    def hist(self):
        return '\n-----\n' + '\n'.join(self.li) + '\n-----\n'
    def flush(self):
        self.li = []

def mock_open_fs():
    return DemoGitFireSet()

def cli_setup():
    cli.say = MockSay()
    shutil.rmtree('/tmp/firelet_test', True)
    shutil.copytree('test/', '/tmp/firelet_test')

def cli_run(*args):
    """Wrap CLI invocation"""
    a = list(args)
    assert_raises(SystemExit, cli.main, a)

@with_setup(cli_setup)
def test_cli_rule_list():
    cli_run('-c test/firelet_test.ini', 'rule', 'list')
    assert len(cli.say.li) > 5, cli.say.hist()

@with_setup(cli_setup)
def test_cli_help():
    assert_raises(SystemExit, cli.main), "Exit 1, print help"

@with_setup(cli_setup)
def test_cli_list():
    old = 0
    for x in ('rule', 'host', 'hostgroup', 'service', 'network'):
        print "Running cli %s list" % x
        cli_run(x, 'list', '')
        assert len(cli.say.li) > old + 3, \
            "Short or no output from cli %s list: %s" % (x, repr(cli.say.li[old:]))
        old = len(cli.say.li)

@with_setup(cli_setup)
def test_versioning():
    """Versioning functional testing"""
    cli_run('-c test/firelet_test.ini', 'save_needed', '-q')
    assert cli.say.li == ['No'], "No save needed here" + cli.say.hist()
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q') # no versions
    assert cli.say.li == ['No'], "No versions expected" + cli.say.hist()
    cli_run('-c test/firelet_test.ini', 'rule', 'disable', '2', '-q')
    cli_run('-c test/firelet_test.ini', 'save', 'test1', '-q') # save 1
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q')
    assert cli.say.li[:3] == ['No', 'Rule 2 disabled.',
    'Configuration saved. Message: "test1"'], "Incorrect behavior"
    assert cli.say.li[-1].endswith('| test1 |'), cli.say.hist()
    cli_run('-c test/firelet_test.ini', 'rule', 'enable', '2', '-q')
    cli_run('-c test/firelet_test.ini', 'save', 'test2', '-q') # save 2
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q')
    assert cli.say.li[-2].endswith('| test2 |'), cli.say.hist()
    cli_run('-c test/firelet_test.ini', 'rule', 'disable', '2', '-q')
    cli_run('-c test/firelet_test.ini', 'save', 'test3', '-q') # save 1
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q')
    assert cli.say.li[-3].endswith('| test3 |'), cli.say.hist()
    # rollback by number
    cli.say.flush()
    cli_run('-c test/firelet_test.ini', 'version', 'rollback', '1', '-q')
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q')
    assert cli.say.li[0].endswith('| test2 |') and \
        cli.say.li[1].endswith('| test1 |'), "Incorrect rollback" + cli.say.hist()
    # rollback by ID
    commit_id = cli.say.li[1].split()[0]
    cli.say.flush()
    cli_run('-c test/firelet_test.ini', 'version', 'rollback', commit_id, '-q')
    cli_run('-c test/firelet_test.ini', 'version', 'list', '-q')
    assert cli.say.li[0].endswith('| test1 |'),  "Incorrect rollback" + cli.say.hist()
    # reset
    cli_run('-c test/firelet_test.ini', 'rule', 'enable', '2', '-q')
    cli_run('-c test/firelet_test.ini', 'save_needed', '-q')
    assert cli.say.li[-1] == 'Yes', "Save needed here" + cli.say.hist()
    cli_run('-c test/firelet_test.ini', 'reset', '-q')
    cli_run('-c test/firelet_test.ini', 'save_needed', '-q')
    assert cli.say.li[-1] == 'No', "No save needed here" + cli.say.hist()



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
    shutil.rmtree('/tmp/firelet_test', True)
    shutil.copytree('test/', '/tmp/firelet_test')
    d = {'d1':{'d2':{'d3':{'d4':{'d5':{'this is getting':'boring'}}}}}}
    savejson('jfile', d, d='/tmp/firelet_test')
    nd = loadjson('jfile', d='/tmp/firelet_test')
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

def test_bunch_repr():
    b = Bunch( c=42, a=3, b='44', _a=0)
    assert repr(b) == "{'a': 3, 'c': 42, 'b': '44', '_a': 0}", "Bunch repr is incorrect: %s" % repr(b)

def test_bunch_set_get():
    b = Bunch( c=42, a=3, b='44', _a=0)
    assert b.c == 42
    assert b['c'] == 42
    b.c = 17
    assert b.c == 17
    b['c'] = 18
    assert b.c == 18
    assert 'c' in b

def test_bunch_token():
    b = Bunch( c=42, a=3, b='44', _a=0)
    tok = b._token()
    b.validate_token(tok)
    assert_raises(Exception,  b.validate_token, '123456')

def test_bunch_update():
    b = Bunch( c=42, a=3, b='44', _a=0)
    d = dict(_a=1, a=2, b=3, c=4, extra=5)
    b.update(d)
    assert b.a == 2 and b.c == 4

def test_flag_true():
    for x in (1, True, '1', 'True', 'y', 'on' ):
        assert flag(x) == '1'

def test_flag_false():
    for x in (0, False, '0', 'False', 'n', 'off', ''):
        assert flag(x) == '0'

def test_flag_raise():
    for x in ('true', 'false'):
        assert_raises(Exception, flag, x)


