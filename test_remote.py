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

from lib.flcore import *
import shutil

from nose.tools import assert_raises, with_setup

def setup_dir():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')

def teardown_dir():
    shutil.rmtree('test/firewalltmp', True)


# #  Testing flssh module  # #

@with_setup(setup_dir, teardown_dir)
def test_deployment():
    fs = DumbFireSet(repodir='test/firewalltmp')
    fs.deploy()


@with_setup(setup_dir, teardown_dir)
def test_get_confs_remote_real():
    return
    fs = DumbFireSet(repodir='test/firewalltmp')
    fs._get_confs()
    assert fs._remote_confs == {
        'Bilbo': [None, '10.66.2.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth1': ('10.66.2.1/24', 'fe80::a00:27ff:fe52:a8b2/64'), 'eth0': ('10.66.1.2/24', 'fe80::a00:27ff:fe81:1366/64')}],
        'Fangorn': [None, '10.66.2.2', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth0': ('10.66.2.2/24', 'fe80::a00:27ff:fe77:6d19/64')}],
        'Gandalf': [None, '10.66.1.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth1': ('10.66.1.1/24', 'fe80::a00:27ff:fee6:4b3e/64'), 'eth0': ('172.16.2.223/17', 'fe80::a00:27ff:fe03:d05e/64')}],
        'Smeagol': [None, '10.66.1.3', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth0': ('10.66.1.3/24', 'fe80::a00:27ff:fe75:2c75/64')}]}
    fs._check_ifaces()





# # Rule deployment testing # #

@with_setup(setup_dir, teardown_dir)
def test_deployment():
    """Test host connectivity is required"""
    fs = DumbFireSet(repodir='test/firewalltmp')
    fs.deploy()



