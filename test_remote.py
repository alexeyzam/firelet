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

from json import dumps
import logging as log
from nose.tools import assert_raises, with_setup
from os import listdir
import shutil
from tempfile import mkdtemp

from firelet.flcore import *

repodir = None

def debug(s, o):
    try:
        logging.debug("%s: %s" % (s, dumps(o, indent=2)))
    except:
        logging.debug("%s: %s" % (s, repr(o)))

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
    Check for ip addr show
    Ignore the iptables confs: the current state on the hosts (or emulator) is not known
    """
    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    sx = SSHConnector(d)
    confs = sx.get_confs()
    for hostname in d:
        assert hostname in confs, "%s missing from the results" % hostname

    for h, conf in confs.iteritems():
        assert 'iptables' in conf
        assert 'ip_a_s' in conf
        assert 'nat' in conf['iptables']
        assert 'filter' in conf['iptables']
        assert 'lo' in conf['ip_a_s']

    for h in ('Bilbo', 'Fangorn', 'Gandalf', 'Smeagol'):
        assert 'eth0' in confs[h]['ip_a_s'], h + " has no eth0"

    assert 'eth1' in confs['Gandalf']['ip_a_s']
    assert 'eth1' in confs['Bilbo']['ip_a_s']
    assert 'eth2' in confs['Gandalf']['ip_a_s']


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
    confs = dict((h, ['# this is an iptables conf test',
                                '# for %s' % h,
                                '-A INPUT -s 3.3.3.3/32 -j ACCEPT',
                            ] ) for h in d)

    # deliver
    log.debug("Delivery...")
    sx = SSHConnector(d)
    status = sx.deliver_confs(confs)
    assert status == {'Bilbo': 'ok', 'Fangorn': 'ok', 'Gandalf': 'ok', 'localhost': 'ok', 'Smeagol': 'ok'}, repr(status)

    # apply
    log.debug("Applying...")
    sx.apply_remote_confs()

    # get and compare
    log.debug("Getting confs...")
    rconfs = sx.get_confs()

    for h, conf in confs.iteritems():
        assert h in rconfs, "%s missing from received confs" % h
        r = rconfs[h]
        assert 'iptables' in r
        assert 'ip_a_s' in r
        assert 'nat' in r['iptables']
        assert 'filter' in r['iptables']
        assert r['iptables']['nat'] == []
        assert r['iptables']['filter'] == ['-A INPUT -s 3.3.3.3/32 -j ACCEPT'], "Rconf: %s" % repr(r)
        assert 'lo' in r['ip_a_s']




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

