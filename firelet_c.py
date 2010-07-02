#!/usr/bin/env python

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
    print 'help'
    exit(0)

if len(argv) == 1:
    help()

if a1 == 'save':
    if a3: help()
    if a2:
        raise NotImplementedError
    help()

elif a1 == 'reset':
    raise NotImplementedError

elif a1 == 'version':
    if a2 == 'list' or None:
        pass # list
    elif argv[2] == 'rollback':
        pass # rollback to argv[3]
    else:
        help()

elif a1 == 'check':
    if a2: help()
    raise NotImplementedError

elif a1 == 'deploy':
    if a2: help()
    raise NotImplementedError

elif a1 == 'rule':
    if a2 == 'list' or None:
        raise NotImplementedError
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        raise NotImplementedError

elif a1 == 'hostgroup':
    if a2 == 'list' or None:
        raise NotImplementedError
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        raise NotImplementedError

elif a1 == 'host':
    if a2 == 'list' or None:
        raise NotImplementedError
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        raise NotImplementedError

elif a1 == 'service':
    if a2 == 'list' or None:
        raise NotImplementedError
    elif a2 == 'add':
        raise NotImplementedError
    elif a2 == 'del':
        raise NotImplementedError





