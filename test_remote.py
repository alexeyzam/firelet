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

# Test network-enabled functions
#
# These tests can be performed against the local node emulator
# ( see ./node_emulator/) or against real firewalls.
# WARNING: the tests are disruptive - don't run the in production.
#


from firelet.flcore import *
from os import listdir
import shutil
from tempfile import mkdtemp

from nose.tools import assert_raises, with_setup

repodir = None

def setup_dir():
    global repodir
    if repodir:
        teardown_dir()
    repodir = mkdtemp() + '/test'
    shutil.copytree('test', repodir)
    li = listdir(repodir)
    assert len(li) > 5

def teardown_dir():
    global repodir
    if repodir:
        shutil.rmtree(repodir, True)
        repodir = None

addrmap = {
    "10.66.1.2": "Bilbo",
    "10.66.2.1": "Bilbo",
    "10.66.1.3": "Smeagol",
    "10.66.2.2": "Fangorn",
    "172.16.2.223": "Gandalf",
    "10.66.1.1": "Gandalf",
    '127.0.0.1': 'localhost'
}

# #  Testing flssh module  # #

from firelet.flssh import SSHConnector

def test_SSHConnector_get():
    pass

##TODO: test get confs
#@with_setup(setup_dir, teardown_dir)
#def test_get_confs():
#    return
#    fs = GitFireSet(repodir=repodir)
#    fs._get_confs()
#    assert fs._remote_confs == {
#        'Bilbo': [None, '10.66.2.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth1': ('10.66.2.1/24', 'fe80::a00:27ff:fe52:a8b2/64'), 'eth0': ('10.66.1.2/24', 'fe80::a00:27ff:fe81:1366/64')}],
#        'Fangorn': [None, '10.66.2.2', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth0': ('10.66.2.2/24', 'fe80::a00:27ff:fe77:6d19/64')}],
#        'Gandalf': [None, '10.66.1.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth1': ('10.66.1.1/24', 'fe80::a00:27ff:fee6:4b3e/64'), 'eth0': ('172.16.2.223/17', 'fe80::a00:27ff:fe03:d05e/64')}],
#        'Smeagol': [None, '10.66.1.3', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth0': ('10.66.1.3/24', 'fe80::a00:27ff:fe75:2c75/64')}]}
#    fs._check_ifaces()


@with_setup(setup_dir, teardown_dir)
def test_get_confs():
    """Get confs from firewalls
    Ignore the iptables confs, but check for ip addr show
    """
    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    sx = SSHConnector(d)
    confs = sx.get_confs()
    for hostname in d:
        assert hostname in confs, "%s missing from the results" % hostname

    for h, conf in confs.iteritems():
        assert repr(conf['iptables']) == "{'filter': [], 'nat': ''}", "%s %s" % (h, repr(conf['iptables']))
        assert 'lo' in conf['ip_a_s']

    assert repr(confs) == "{'Bilbo': {'iptables': {'filter': [], 'nat': ''}, 'ip_a_s': {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('10.66.1.2/24', 'fe80::3939:3939:3939:3939/64')}}, 'Fangorn': {'iptables': {'filter': [], 'nat': ''}, 'ip_a_s': {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.2.2/24', 'fe80::3939:3939:3939:3939/64')}}, 'Gandalf': {'iptables': {'filter': [], 'nat': ''}, 'ip_a_s': {'lo': ('127.0.0.1/8', '::1/128'), 'eth2': ('88.88.88.88/24', 'fe80::3939:3939:3939:3939/64'), 'eth1': ('10.66.1.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('172.16.2.223/24', 'fe80::3939:3939:3939:3939/64')}}, 'localhost': {'iptables': {'filter': [], 'nat': ''}, 'ip_a_s': {'lo': ('127.0.0.1/8', '::1/128'), 'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}}, 'Smeagol': {'iptables': {'filter': [], 'nat': ''}, 'ip_a_s': {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.1.3/24', 'fe80::3939:3939:3939:3939/64')}}}"
    #TODO: review this



@with_setup(setup_dir, teardown_dir)
def test_deliver_confs():
    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    sx = SSHConnector(d)
    confs = dict((h, []) for h in d)
    status = sx.deliver_confs(confs)
    assert status == {'Bilbo': 'ok', 'Fangorn': 'ok', 'Gandalf': 'ok', 'localhost': 'ok', 'Smeagol': 'ok'}, repr(status)


@with_setup(setup_dir, teardown_dir)
def test_deliver_apply_and_get_confs():
    """Remote conf delivery, apply and get
    """

    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    # confs =  {hostname: {iface: [rules, ] }, ... }
    confs = dict((h, ['# this is an iptables conf test','# for %s' % h] ) for h in d)

    # deliver
    sx = SSHConnector(d)
    status = sx.deliver_confs(confs)
    assert status == {'Bilbo': 'ok', 'Fangorn': 'ok', 'Gandalf': 'ok', 'localhost': 'ok', 'Smeagol': 'ok'}, repr(status)

    # apply
    print "Applying..."
    sx.apply_remote_confs()

    # get
    print "Getting confs..."
    rconfs = sx.get_confs()

    # compare
    for h, conf in confs.iteritems():
        print repr(conf)
    assert False

#        assert repr(conf['iptables']) == "{'filter': [], 'nat': ''}", "%s %s" % (h, repr(conf['iptables']))
#        for iface in conf['ip_a_s']:
#            print h, iface





#@with_setup(setup_dir, teardown_dir)
#def test_check():
#    fs = GitFireSet(repodir=repodir)
#    fs.check()
#
#
#
## # Rule deployment testing # #
#
#@with_setup(setup_dir, teardown_dir)
#def test_deployment():
#    """Test host connectivity is required"""
#    fs = GitFireSet(repodir=repodir)
#    fs.deploy()
#
#

