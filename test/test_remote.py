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
from nose.tools import assert_raises, with_setup
from os import listdir
import shutil
from tempfile import mkdtemp

from firelet.flcore import *

# import testing utility functions from test.py
from test import debug, string_in_list, assert_equal_line_by_line

import logging
log = logging.getLogger(__name__)

from logging import getLogger
log = logging.getLogger(__name__)
deb = log.debug

from testingutils import *
import testingutils

addrmap = {
    "10.66.1.2": "InternalFW",
    "10.66.2.1": "InternalFW",
    "10.66.1.3": "Smeagol",
    "10.66.2.2": "Server001",
    "172.16.2.223": "BorderFW",
    "10.66.1.1": "BorderFW",
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
#        'InternalFW': [None, '10.66.2.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth1': ('10.66.2.1/24', 'fe80::a00:27ff:fe52:a8b2/64'), 'eth0': ('10.66.1.2/24', 'fe80::a00:27ff:fe81:1366/64')}],
#        'Server001': [None, '10.66.2.2', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
#            'eth0': ('10.66.2.2/24', 'fe80::a00:27ff:fe77:6d19/64')}],
#        'BorderFW': [None, '10.66.1.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
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
    assert isinstance(confs, dict)
    for hostname in d:
        assert hostname in confs, "%s missing from the results" % hostname

    for h, conf in confs.iteritems():
#        assert isinstance(conf, dict), "%s's conf is not a dict: %s" \
#            % (h, repr(conf))
        assert 'iptables' in conf
        assert 'ip_a_s' in conf
        assert 'nat' in conf['iptables']
        assert 'filter' in conf['iptables']
        assert 'lo' in conf['ip_a_s']

    for h in ('InternalFW', 'Server001', 'BorderFW', 'Smeagol'):
        assert 'eth0' in confs[h]['ip_a_s'], h + " has no eth0"

    assert 'eth1' in confs['BorderFW']['ip_a_s']
    assert 'eth1' in confs['InternalFW']['ip_a_s']
    assert 'eth2' in confs['BorderFW']['ip_a_s']


@with_setup(setup_dir, teardown_dir)
def test_get_conf_BorderFW():
    d = {'BorderFW': ['172.16.2.223']}
    for x in xrange(20):
        deb(show("%d run" % x))
        sx = SSHConnector(d)
        confs = sx.get_confs()
        assert isinstance(confs, dict)
        assert 'BorderFW' in confs, "BorderFW missing from the results"
        assert 'iptables' in confs['BorderFW']
        del(sx)
        deb(show("Completed run %d" % x))

## # Rule deployment testing # #

@with_setup(setup_dir, teardown_dir)
def test_deliver_confs():
    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    sx = SSHConnector(d)
    confs = dict((h, []) for h in d)
    status = sx.deliver_confs(confs)
    assert status == {'InternalFW': 'ok', 'Server001': 'ok', 'BorderFW': 'ok', 'localhost': 'ok', 'Smeagol': 'ok'}, repr(status)


@with_setup(setup_dir, teardown_dir)
def test_deliver_apply_and_get_confs():
    """Remote conf delivery, apply and get it back
    """

    d = dict((h, [ip_addr]) for ip_addr, h in addrmap.iteritems())
    # confs =  {hostname: {iface: [rules, ] }, ... }
    confs = dict(
        (h, ['# this is an iptables conf test',
                '# for %s' % h,
                '-A INPUT -s 3.3.3.3/32 -j ACCEPT',
            ] ) for h in d
    )

    # deliver
    log.debug("Delivery...")
    sx = SSHConnector(d)
    status = sx.deliver_confs(confs)
    assert status == {'InternalFW': 'ok', 'Server001': 'ok', 'BorderFW': 'ok',
        'localhost': 'ok', 'Smeagol': 'ok'}, repr(status)

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
#        assert r['iptables']['nat'] == [], repr(r)
    #FIXME: re-enable this
    #assert r['iptables']['filter'] == ['-A INPUT -s 3.3.3.3/32 -j ACCEPT'], "Rconf: %s" % repr(r)
        assert 'lo' in r['ip_a_s']


## # End-to-end Fireset testing # #


#@with_setup(setup_dir, teardown_dir)
#def test_GitFireSet_check():
#    """Run diff between complied rules and remote confs using GitFireSet
#    Given the test files, the check should be ok and require no deployment"""
#    fs = GitFireSet(repodir=testingutils.repodir)
#    diff = fs.check()
#    #TODO: initial
#    assert diff == {}, repr(diff)

@with_setup(setup_dir, teardown_dir)
def test_GitFireSet_deployment():
    """Check, then deploy confs"""
    fs = GitFireSet(repodir=testingutils.repodir)
    diff_before = fs.check()
    fs.deploy()
    diff = fs.check()
    assert diff == {}, repr(diff)



