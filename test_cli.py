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

import glob
from os import listdir
from json import dumps
import shutil

from nose.tools import assert_raises, with_setup
from pprint import pformat
from tempfile import mkdtemp

from firelet.flcore import DemoGitFireSet

from firelet import cli
from firelet.cli import main as cli_main

from logging import getLogger
from testingutils import show
from firelet import cli
from firelet.cli import main as cli_main

repodir = None

log = getLogger(__name__)
deb = log.debug

# setup and teardown

def setup_test_dir():
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
    deb("temp dir %s created" % repodir)


def teardown_dir():
    global repodir
    if repodir:
        shutil.rmtree(repodir)
        repodir = None

# utility functions

def string_in_list(s, li):
    """Count how many times a string is contained in a list of strings
    No exact match is required
    >>> strings_in_list('p', ['apple'])
    1
    """
    return sum((1 for x in li if s in str(x)))

def test_string_in_list():
    li = ['apple', 'p', '', None, 123, '   ']
    assert string_in_list('p', li) == 2

def assert_equal_line_by_line(li1, li2):
    for x, y in zip(li1, li2):
        assert x == y, "'%s' differs from '%s' in:\n%s\n%s\n" % (repr(li1), repr(li2))



# #  CLI testing # #

class MockSay():
    """Mock the say() method in cli.py to store what is being printed"""
    def __init__(self):
        deb("Mocking say()...")
        self.li = []
    def __call__(self, s):
        self.li.append(s)
    def hist(self):
        return '\n-----\n' + '\n'.join(self.li) + '\n-----\n'
    def flush(self):
        self.li = []

def mock_open_fs(_repodir):
    "Testing is performed against the Demo FireSet"
    deb(show("Using %s as repodir" % repodir))
    return DemoGitFireSet(repodir=repodir)

def mock_getpass(s=None):
    """Mock getpass() to unit-test user creation"""
    return "12345"




def cli_setup():
    cli.say = MockSay()
    cli.getpass = mock_getpass
    cli.open_fs = mock_open_fs
    setup_test_dir()

def cli_run(*args):
    """Wrap CLI invocation to prevent os.exit() from breaking unit testing"""
    deb(show('started'))
    deb(show("running cli with arguments: %s" % repr(args)))
    oldrepodir = repodir
    a = list(args)
    hist_len = len(cli.say.li)
    deb(show('cli.main started'))
    assert_raises(SystemExit, cli.main, a), "Exited without 0 or 1" + cli.say.hist()
    out = cli.say.li[hist_len:]
    deb(show("Output: %s\n" % out))
#    repodir = oldrepodir
    if oldrepodir != repodir:
        deb(show("XXXXXXXXXXXXXXXXXXX"))
    return out
    return cli.say.li[hist_len:]

@with_setup(cli_setup)
def test_cli_rule_list():
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'rule', 'list')
    assert len(cli.say.li) > 5, cli.say.hist()

@with_setup(cli_setup)
def test_cli_help():
    assert_raises(SystemExit, cli.main), "Exit 1, print help"

@with_setup(cli_setup)
def test_cli_list():
    for x in ('rule', 'host', 'hostgroup', 'service', 'network'):
        print "Running cli %s list" % x
        out = cli_run(x, 'list', '')
        assert len(out) > 3, \
            "Short or no output from cli %s list: %s" % (x, repr(out))

@with_setup(cli_setup)
def test_cli_versioning():
    """Versioning functional testing"""
    deb(show('started'))
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir,
        '-r '+repodir, 'save_needed', '-q')
    assert out == ['No'], "No save needed here" + cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
        'list', '-q') # no versions
    assert out == [], "No versions expected" + cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'rule',
    'disable', '2', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'save',
    'test1', '-q') # save 1
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
                   'list', '-q')
    assert cli.say.li[:3] == ['No', 'Rule 2 disabled.',
    'Configuration saved. Message: "test1"'], "Incorrect behavior"
    assert out, cli.say.hist()
    assert out[-1].endswith('| test1 |'), cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'rule',
    'enable', '2', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'save',
    'test2', '-q') # save 2
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
    'list', '-q')
    assert out[-2].endswith('| test2 |'), cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'rule',
    'disable', '2', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'save',
    'test3', '-q') # save 1
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
    'list', '-q')
    assert out[-3].endswith('| test3 |'), cli.say.hist()
    # rollback by number
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version', 'rollback', '1', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
    'list', '-q')
    assert out[0].endswith('| test2 |') and \
        out[1].endswith('| test1 |'), "Incorrect rollback" + cli.say.hist()
    # rollback by ID
    commit_id = out[1].split()[0]
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version', 'rollback', commit_id, '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'version',
                   'list', '-q')
    assert out[0].endswith('| test1 |'),  "Incorrect rollback" + cli.say.hist()
    # reset
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'rule',
                   'enable', '2', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'save_needed',
                   '-q')
    assert out[-1] == 'Yes', "Save needed here" + cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'reset', '-q')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, 'save_needed',
                   '-q')
    assert out[-1] == 'No', "No save needed here" + cli.say.hist()

# TODO: add check, compile and deploy tests

# CLI user management

@with_setup(cli_setup)
def test_cli_user_management():
    deb(show('started'))
    out1 = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'user',
                    'list')
    assert out1 == [
        u'Rob            readonly        None',
        u'Eddy           editor          None',
        u'Ada            admin           None'], \
        "Incorrect user list: %s" % repr(out1) + cli.say.hist()
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'user',
                   'add', 'Totoro',
        'admin', 'totoro@nowhere.forest')
    out2 = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'user',
    'list')
    assert out2 == [
        u'Rob            readonly        None',
        u'Ada            admin           None',
        u'Eddy           editor          None',
        u'Totoro         admin           totoro@nowhere.forest'], \
        "Incorrect user list" + cli.say.hist()
    cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'user',
             'validatepwd', 'Totoro')
    cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'user',
    'del', 'Totoro')
    out3 = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
    'user', 'list')
    assert out3 == out1, "User not deleted" + cli.say.hist()

    #TODO: add user editing to the CLI and test it ?

# CLI rule management

@with_setup(cli_setup)
def test_cli_rule_list():
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
    'rule', 'list')
    for line in out[1:]:
        li = line.split('|')
        li = map(str.strip, li)
        assert li[1] in ('ACCEPT','DROP'), li
        assert li[5] in ('0','1'), li #en/dis-abled

@with_setup(cli_setup)
def test_cli_rule_enable_disable():
    out1 = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
    'rule', 'list')
    assert out1[2].split('|')[5].strip() == '1',  "First rule should be enabled"
    cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'rule',
    'disable', '1')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
    'rule', 'list')
    assert out[2].split('|')[5].strip() == '0',  "First rule should be disabled"
    cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', 'rule',
    'enable', '1')
    out = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
    'rule', 'list')
    assert out == out1, "Rule enable/disable not idempotent"

@with_setup(cli_setup)
def test_cli_multiple_list_and_deletion():
    for name in ('rule', 'host', 'hostgroup', 'network', 'service'):
        before = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
                         name, 'list')
        cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q', name,
        'del', '2')
        after = cli_run('-c test/firelet_test.ini',  "-r %s" % repodir, '-q',
                        name, 'list')
        assert len(after) == len(before) - 1, "%s not deleted %s" % \
            (name, cli.say.hist())
