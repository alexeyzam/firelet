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

import logging
import inspect

import glob
from os import listdir
from json import dumps
import shutil
from tempfile import mkdtemp


repodir = None

# setup and teardown

def setup_dir():
    global repodir
    if repodir:
        teardown_dir()
    repodir = mkdtemp(prefix='tmp_fltest')

    # copy the needed files
    globs = ['test/iptables-save*', 'test/ip-addr-show*','test/*.csv', 'test/*.json']
    for g in globs:
        for f in glob.glob(g):
            shutil.copy(f, repodir)

    li = listdir(repodir)
    assert len(li) > 5, "Not enough file copied"
#    log.debug("temp dir %s created" % repodir)

def teardown_dir():
    global repodir
    if repodir:
        shutil.rmtree(repodir)
        repodir = None

def show(s, o=None):
    """Log an object representation"""

    stack = [x[3] for x in inspect.stack()]
    if 'runTest' in stack:
        rt = stack.index('runTest')
        stack = stack[1:rt]
    else:
        stack = stack[1:3]
    stack = "->".join(reversed(stack))

    try:
        d = dumps(o, indent=2)
    except:
        d = repr(o)
    li = d.split('\n')

    if len(li) < 3:
        if o:
            return "%s %s: %s" % (stack, s, repr(o))
        else:
            return "%s %s" % (stack, s)
    else:
        indented = "\n    ".join(li)
        return "\n-------- [%s] ---------\n    %s\n----- [end of %s] -----\n" % (s, indented, s)

