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

from confreader import ConfReader
from flcore import GitFireSet, DemoGitFireSet
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

def help():
    #TODO
    say("""
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
    """)
    exit(0)


def deletion(table):
    if not a3:
        help()
    try:
        rid = int(a3)
        rd.delete(table, rid)
    except:
        pass
        #TODO

def prettyprint(li):
    """Pretty-print as a table"""
    keys = sorted(li[0].keys())
    t = [keys]
    for d in li:
        m =[d[k] for k in keys]
        m = map(str, m)
        t.append(m)

    cols = zip(*t)
    cols_sizes = [(max(map(len, i))) for i in cols] # get the widest entry in each column

    for m in t:
        s = " | ".join((item.ljust(pad) for item, pad in zip(m, cols_sizes)))
        say(s)

#        def j((n, li)):
#            return "%d  " % n + "  ".join((item.ljust(pad) for item, pad in zip(li, cols_sizes) ))
#        return '\n'.join(map(j, enumerate(self)))

def say(s):
    print s

def main(a1, a2, a3):
    if not a1:
        help()

    # read configuration,
    try:
        conf = ConfReader(fn='firelet.ini')
    except Exception, e:
        log.error("Exception %s while reading configuration file '%s'" % (e, fn))
        exit(1)

    if conf.demo_mode == 'False':
        fs = GitFireSet()
        say( "Firelet CLI.")
    elif conf.demo_mode == 'True':
        fs = DemoGitFireSet()
        say( "Firelet CLI - demo mode.")

    if a1 == 'save':
        if a3 or not a2:
            help()
        fs.save(str(a2))

    elif a1 == 'reset':
        if a2:
            help()
        fs.reset()

    elif a1 == 'version':
        if a2 == 'list' or None:
            for user, date, msg, commit_id in fs.version_list():
                s = '%s | %s | %s | %s |' % (commit_id, date, user, msg[0])
                say(s)
        elif a2 == 'rollback':
            if not a3:
                help()
            try:
                n = int(a3)
                fs.rollback(n=n)
            except ValueError:
                fs.rollback(commit_id=a3)
        else:
            help()

    elif a1 == 'check':
        if a2: help()
        raise NotImplementedError

    elif a1 == 'compile':
        if a2: help()
        c = fs.compile()
        for li in c:
            say(li)

    elif a1 == 'deploy':
        if a2: help()
        fs.deploy()

    elif a1 == 'rule':
        if a2 == 'list' or None:
            prettyprint(fs.rules)
        elif a2 == 'add':
            raise NotImplementedError
        elif a2 == 'del':
            deletion('rules')

    elif a1 == 'hostgroup':
        if a2 == 'list' or None:
            prettyprint(fs.hostgroups)
        elif a2 == 'add':
            raise NotImplementedError
        elif a2 == 'del':
            deletion('hostgroups')

    elif a1 == 'host':
        if a2 == 'list' or None:
            prettyprint(fs.hosts)
        elif a2 == 'add':
            raise NotImplementedError
        elif a2 == 'del':
            deletion('hosts')

    elif a1 == 'network':
        if a2 == 'list' or None:
            prettyprint(fs.networks)
        elif a2 == 'add':
            raise NotImplementedError
        elif a2 == 'del':
            deletion('networks')

    elif a1 == 'service':
        if a2 == 'list' or None:
            prettyprint(fs.services)
        elif a2 == 'add':
            raise NotImplementedError
        elif a2 == 'del':
            deletion('services')

    else:
        help()

if __name__ == '__main__':
    _, a1, a2, a3 = argv + [None] * (4 - len(argv))
    main(a1, a2, a3)

