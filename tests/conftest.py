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

import pytest
import glob
import shutil
import py
#@pytest.fixture(scope="module")
@pytest.fixture
def repodir(tmpdir):
    """Create and populate test repository directory"""

    # copy the needed files
    globs = ['tests/iptables-save*', 'tests/ip-addr-show*','tests/*.csv', 'tests/*.json']
    for g in globs:
        for f in glob.glob(g):
            f = py.path.local(f)
            f.copy(tmpdir)

    py.path.local('tests/firelet_test.ini').copy(tmpdir)

    li = tmpdir.listdir()
    assert len(li) > 5, "Not enough file copied: %r" % li

    return tmpdir.strpath

