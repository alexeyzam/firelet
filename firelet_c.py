#!/usr/bin/env python

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

# Firelet Command Line Interface

from lib.confreader import ConfReader
from lib.flcore import *

from sys import argv, exit

#   commands
#
#   save <desc>
#   reset
#   version
#       list
#       rollback <version>
#   check
#   deploy
#   user
#       add <....>
#       del <num>
#       list
#   rule
#       add <....>
#       del <num>
#       list
#   hostgroup
#       add <...>
#       del <num>
#       list
#   network
#       add <...>
#       del <num>
#       list
#

_, a1, a2, a3 = argv + [None] * (4 - len(argv))

def help():
    #TODO
    print """
    Firelet CLI

    Commands:

    user    - web interface user management
        list
        add  <login> <role>
        del <num>
    save    - save the current configuration
    reset   - revert the configuration to the last saved state
    version
    check
    deploy
    rule
        list
        add
        del
    host
        list
        add
        del
    hostgroup
        ...
    """
    exit(0)

def deletion(table):
    if not a3: help()
    try:
        rid = int(a3)
        rd.delete(table, rid)
    except:
        pass #TODO


if len(argv) == 1:
    help()

fs = DumbFireSet()

if a1 == 'save':
    if a3 or not a2: help()
    fs.save(str(a2))

elif a1 == 'reset':
    if a2: help()
    fs.reset()

elif a1 == 'version':
    if a2 == 'list' or None:
        print fs.version_list()
    elif a2 == 'rollback':
        fs.rollback()
    else:
        help()

elif a1 == 'check':
    if a2: help()
    raise NotImplementedError

elif a1 == 'compile':
    if a2: help()
    c = fs.compile()
    for li in c:
        print li

elif a1 == 'deploy':
    if a2: help()
    fs.deploy()

elif a1 == 'rule':
    if a2 == 'list' or None:
        print fs.rules

    if a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        deletion('rules')

elif a1 == 'hostgroup':
    if a2 == 'list' or None:
        print fs.hostgroups
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        deletion('hostgroups')

elif a1 == 'host':
    if a2 == 'list' or None:
        print fs.hosts
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        deletion('hosts')

elif a1 == 'service':
    if a2 == 'list' or None:
        print fs.services
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        deletion('services')





