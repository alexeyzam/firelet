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

from argparse import ArgumentParser
from .confreader import ConfReader
from getpass import getpass
import sys
import os.path

from . import __version__
from .flcore import GitFireSet, Users

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

def cli_args(mockargs=None):
    """Parse command line arguments"""
    parser = ArgumentParser(description='Firelet daemon')

    parser.add_argument("-c", "--conffile", nargs='?',
        default='/etc/firelet/firelet.ini', help="configuration file", metavar="FILE")
    parser.add_argument("-r", "--repodir", nargs='?',
        help="configuration repository dir")
    parser.add_argument("-D", "--debug",
        action="store_true", dest="debug", default=False,
        help="run in debug mode and print messages to stdout")
    parser.add_argument("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help="print less messages to stdout")

    # catch all other arguments
    parser.add_argument('commands', nargs='+',
        help='an integer for the accumulator')

    if mockargs:
        opts = parser.parse_args(mockargs)
    else:
        opts = parser.parse_args()

    # temporary hack before rewriting the entire file using argparse
    six_commands = opts.commands + [None] * (6 - len(opts.commands))
    return opts, six_commands

def give_help():    # pragma: no cover
    """Print a help page"""
    #TODO
    say("""
    Commands:

    user    - web interface user management
        list
        add  <login> <role>
        del <num>
    save    - save the current configuration
    reset   - revert the configuration to the last saved state
    version
    save_needed
    check
    deploy
    rule| host | hostgroup | service
        list
        del <id>
    rule
        add
        enable <id>
        disable <id>
    host
        add
    hostgroup
        add
    service
        add
    user
        list
        add <name> <group> <email>
        del <name>
        validatepwd <name>
    assimilate <ip_address>  - configure a new firewall
    """)

def help(s=None):
    """Print help and exit"""
    if s:
        say(s)
    give_help()
    sys.exit(1)

def to_int(s):
    """Convert string to int, exit on failure"""
    try:
        return int(s)
    except:
        if s:
            help("Unable to convert '%s' to int" % s)
        help("Missing argument")

def deletion(table):
    if not a3:
        help()
    try:
        rid = to_int(a3)
        rd.delete(table, rid)
    except:
        pass
        #TODO

def max_len(li):
    """Lenght of the longest item in a list"""
    return max(map(len, li))

def prettyprint(li):
    """Pretty-print a list of dicts a table"""
    keys = sorted(li[0].keys())
    t = [keys]
    for d in li:
        m = [d[k] for k in keys]
        m = map(str, m)
        t.append(m)

    cols = zip(*t)
    cols_sizes = map(max_len, cols) # get the widest entry in each column
    id = 'id'
    for row in t:
        s = " %2s | " % id + " | ".join((item.ljust(pad) for item, pad in zip(row, cols_sizes)))
        say(s)
        try:
            id += 1
        except TypeError:
            id = 0

def say(s):
    """Print to stdout"""
    print(s)

def open_fs(repodir):
    """Open Git FireSet"""
    return GitFireSet(repodir=repodir)

def main(mockargs=None):    # pragma: no cover
    """Firelet command line interface"""

    opts, (a1, a2, a3, a4, a5, a6) = cli_args(mockargs=mockargs)

    whisper = say
    if opts.quiet:
        whisper = lambda x: None

    whisper("Firelet %s CLI." % __version__)

    if not a1:
        help()

    # read configuration,
    fn = opts.conffile.strip()
    fn = os.path.abspath(fn)
    if not os.path.isfile(fn):
        say("File %s not found" % fn)
        sys.exit(1)

    try:
        conf = ConfReader(fn=fn)
    except Exception as e:
        say("Exception %s while reading configuration file '%s'" % (e, fn))
        sys.exit(1)

    # Repodir specified from command line has precedence over the conf. file
    if opts.repodir:
        repodir = opts.repodir.strip()
    else:
        repodir = conf.data_dir

    #TODO: open the FireSet only when needed
    fs = open_fs(repodir)

    if a1 == 'save':
        if a3 or not a2:
            help()
        fs.save(str(a2))
        say('Configuration saved. Message: "%s"' % str(a2))

    elif a1 == 'reset':
        if a2:
            help()
        fs.reset()
        say('Reset complete.')

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

    elif a1 == 'save_needed':
        if fs.save_needed():
            say('Yes')
            if __name__ == '__main__':
                sys.exit(0)
        else:
            say('No')
            if __name__ == '__main__':
                sys.exit(1)

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

    # generic listing
    elif a1 in ('rule', 'host', 'hostgroup', 'network', 'service') and a2 == 'list':
        table = "%ss" % a1
        prettyprint(fs.__dict__[table])

    # generic deletion
    elif a1 in ('rule', 'host', 'hostgroup', 'network', 'service') and a2 == 'del':
        table = "%ss" % a1
        fs.delete(table, to_int(a3))

    elif a1 == 'rule':
        if a2 == 'add':
            raise NotImplementedError   #TODO

        elif a2 == 'enable':
            i = to_int(a3)
            fs.rules.enable(i)
            say('Rule %d enabled.' %i)
        elif a2 == 'disable':
            i = to_int(a3)
            fs.rules.disable(i)
            say('Rule %d disabled.' %i)
        else:
            help('Incorrect arguments')

    elif a1 == 'hostgroup':
        if a2 == 'add':
            raise NotImplementedError
        else:
            help('Incorrect arguments')

    elif a1 == 'host':
        if a2 == 'add':
            raise NotImplementedError
        else:
            help('Incorrect arguments')

    elif a1 == 'network':
        if a2 == 'add':
            raise NotImplementedError
        else:
            help('Incorrect arguments')

    elif a1 == 'service':
        if a2 == 'add':
            raise NotImplementedError
        else:
            help('Incorrect arguments')

    elif a1 == 'user':
        users = Users(d=repodir)
        if a2 == 'list' or None:
            whisper("Name           Role            Email ")
            for name, (role, secret, email) in sorted(users._users.items()):
                say("%-14s %-15s %s" % (name, role, email))
        elif a2 == 'add':
            if not a3:
                help("Missing username.")
            if not a4:
                help("Missing role.")
            if a4 not in ('admin', 'editor', 'readonly'):
                help("Valid roles are: admin, editor, readonly")
            if not a5:
                help("Missing email.")
            pwd = getpass('Enter new password: ')
            users.create(a3, a4, pwd, email=a5)
        elif a2 == 'del':
            if not a3:
                help("Missing username.")
            users.delete(a3)
        elif a2 == 'validatepwd':
            if not a3:
                help("Missing username.")
            pwd = getpass('Enter password: ')
            users.validate(a3, pwd)
            whisper('Password is valid.')
        else:
            help('Incorrect arguments')


    elif a1 == 'assimilate' and a2 is not None:

        rsa_pub_key = fs.get_rsa_pub()
        username = conf.ssh_username
        password = fs.generate_otp()
        say("""Interactive new firewall configuration.

Please SSH to the firewall and run:
sudo adduser %s

Insert the following password: %s
Press Enter when done or Ctrl-C to terminate""" % (username, password))
        raw_input()

        fs.assimilate(a2, rsa_pub_key, 'firelet', password)

    else:
        give_help()
        sys.exit(0)

    sys.exit(0)

if __name__ == '__main__':
    main()

