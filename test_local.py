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

from lib import flssh
import shutil

from nose.tools import assert_raises, with_setup

def dd(d):
    """Debug dict"""
    from simplejson import dumps
    print dumps(d, indent=' ')

# #  Testing flssh module locally # #

def test_sshconnector_getconf():
    # {hostname: [management ip address list ], ... }
    t = {'localhost':['127.0.0.1', ]}
    sx = flssh.SSHConnector(targets=t, username='root')
    confs = sx.get_confs()
    dd(confs)

    assert 'localhost' in confs

#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs4():
#    fs = DumbFireSet(repodir='/tmp/firelet')
#    fs._get_confs()
#    fs._check_ifaces()
#    rd = fs.compile_dict(hosts=fs.hosts)
