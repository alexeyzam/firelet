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

from logging import getLogger
from nose.tools import assert_raises
import os.path

from firelet import cli
from firelet.flcore import DemoGitFireSet
from testingutils import BaseFunctionalTesting
from testingutils import show
import testingutils

log = getLogger(__name__)
deb = log.debug


class MockSay():
    """Mock the say() method in cli.py to store what is being printed"""
    def __init__(self):
        deb("Mocking say()...")
        self.reset_history()

    def __call__(self, s):
        """Append one or more lines to the history"""
        self._output_history.extend(s.split('\n'))

    def hist(self):
        return '\n-----\n' + '\n'.join(self._output_history) + '\n-----\n'

    def flush(self):
        self._output_history = []

    @property
    def output_history(self):
        return self._output_history

    @property
    def last(self):
        return self._output_history[-1]

    def reset_history(self):
        self._output_history = []


def mock_open_fs(repodir):
    "Testing is performed against the Demo FireSet"
    deb(show("Using %s as repodir" % repodir))
    return DemoGitFireSet(repodir=repodir)

def mock_getpass(s=None):
    """Mock getpass() to unit-test user creation"""
    return "12345"


class TestCLI(BaseFunctionalTesting):
    def setUp(self):
        self._setup_repodir()
        cli.say = MockSay()
        cli.getpass = mock_getpass
        cli.open_fs = mock_open_fs

    def tearDown(self):
        self._teardown_repodir()

    def run(self, *args):
        """Wrap CLI invocation to prevent os.exit() from breaking unit testing"""
        conf_fname = os.path.join(self._repodir, 'firelet_test.ini')
        cli_args = ["-c %s" % conf_fname,  "-r %s" % self._repodir]
        cli_args.extend(args)

        deb("running cli with arguments: %r", cli_args)
        oldrepodir = self._repodir
        cli.say.reset_history()
        deb(show('cli.main started'))
        assert_raises(SystemExit, cli.main, cli_args), "Exited without 0 or 1"
        deb("Output: %r", cli.say.hist())
        assert oldrepodir == self._repodir
        return cli.say.output_history

    def test_basic(self):
        assert os.path.isfile(os.path.join(self._repodir, 'firelet_test.ini')), \
            os.listdir(self._repodir)
        out = self.run('')
        assert len(out) > 5
        assert out[0].startswith('Firelet')

    def test_rule_list(self):
        out = self.run('rule', 'list')
        assert len(cli.say.output_history) > 5, cli.say.hist()

    def test_list(self):
        for x in ('rule', 'host', 'hostgroup', 'service', 'network'):
            print "Running cli %s list" % x
            out = self.run(x, 'list', '')
            assert len(out) > 3, \
                "Short or no output from cli %s list: %s" % (x, repr(out))

    def test_versioning(self):
        deb(show('started'))
        self.run('save_needed', '-q')
        assert cli.say.output_history == ['No'], "No save needed here" + cli.say.hist()

        self.run('version', 'list', '-q') # no versions
        assert cli.say.output_history == [], "No versions expected" + cli.say.hist()

        self.run('rule', 'disable', '2', '-q')
        assert cli.say.output_history == ['Rule 2 disabled.']

        self.run('save_needed', '-q')
        assert cli.say.last == 'Yes', "Save needed"

        self.run('save', 'test1', '-q') # save 1
        assert cli.say.output_history == ['Configuration saved. Message: "test1"']

        self.run('version', 'list', '-q')
        assert cli.say.last.endswith('| test1 |'), cli.say.hist()

        self.run('rule', 'enable', '2', '-q')
        assert cli.say.last == 'Rule 2 enabled.'

        self.run('save', 'test2', '-q') # save 2
        assert cli.say.last == 'Configuration saved. Message: "test2"'

        self.run('version', 'list', '-q')
        assert len(cli.say.output_history) == 2
        assert cli.say.output_history[0].endswith('| test2 |'), cli.say.hist()
        assert cli.say.output_history[1].endswith('| test1 |'), cli.say.hist()

        self.run('rule', 'disable', '2', '-q')
        assert cli.say.last == 'Rule 2 disabled.'

        self.run('save', 'test3', '-q') # save 1
        assert cli.say.last == 'Configuration saved. Message: "test3"'

        self.run('version', 'list', '-q')
        assert len(cli.say.output_history) == 3
        assert cli.say.output_history[0].endswith('| test3 |'), cli.say.hist()

        # rollback by number
        self.run('version', 'rollback', '1', '-q')

        self.run('version', 'list', '-q')
        assert len(cli.say.output_history) == 2
        assert cli.say.output_history[0].endswith('| test2 |'), cli.say.hist()
        assert cli.say.output_history[1].endswith('| test1 |'), cli.say.hist()

        # rollback by ID - to a version where rule 2 was disabled
        commit_id = cli.say.output_history[1].split()[0]
        self.run('version', 'rollback', commit_id, '-q')

        self.run('version', 'list', '-q')
        assert cli.say.last.endswith('| test1 |'),  "Incorrect rollback" + cli.say.hist()

        # reset
        self.run('rule', 'enable', '2', '-q')
        assert cli.say.last == 'Rule 2 enabled.'

        self.run('save_needed', '-q')
        assert cli.say.last == 'Yes', "Save needed"

        self.run('reset', '-q')

        self.run('save_needed', '-q')
        assert cli.say.last == 'No', "Save not needed"


    # user management

    def test_user_management(self):
        deb(show('started'))
        out1 = self.run('-q', 'user', 'list')
        assert out1 == [
            u'Rob            readonly        None',
            u'Eddy           editor          None',
            u'Ada            admin           None'], \
            "Incorrect user list: %s" % repr(out1) + cli.say.hist()
        out = self.run('-q', 'user', 'add', 'Totoro',
            'admin', 'totoro@nowhere.forest')
        out2 = self.run('-q', 'user', 'list')
        assert out2 == [
            u'Rob            readonly        None',
            u'Ada            admin           None',
            u'Eddy           editor          None',
            u'Totoro         admin           totoro@nowhere.forest'], \
            "Incorrect user list" + cli.say.hist()
        self.run('-q', 'user', 'validatepwd', 'Totoro')
        self.run('-q', 'user', 'del', 'Totoro')
        out3 = self.run('-q', 'user', 'list')
        assert out3 == out1, "User not deleted" + cli.say.hist()


    # rule management

    def test_rule_list(self):
        out = self.run('-q', 'rule', 'list')
        for line in out[1:]:
            li = line.split('|')
            li = map(str.strip, li)
            assert li[1] in ('ACCEPT','DROP'), li
            assert li[5] in ('0','1'), li #en/dis-abled

    def test_rule_enable_disable(self):
        out1 = self.run('-q', 'rule', 'list')
        assert out1[2].split('|')[5].strip() == '1',  "First rule should be enabled"
        self.run('-q', 'rule', 'disable', '1')
        out = self.run('-q', 'rule', 'list')
        assert out[2].split('|')[5].strip() == '0',  "First rule should be disabled"
        self.run('-q', 'rule', 'enable', '1')
        out = self.run('-q', 'rule', 'list')
        assert out == out1, "Rule enable/disable not idempotent"

    def test_multiple_list_and_deletion(self):
        for name in ('rule', 'host', 'hostgroup', 'network', 'service'):
            before = self.run('-q', name, 'list')
            self.run('-q', name, 'del', '2')
            after = self.run('-q', name, 'list')
            assert len(after) == len(before) - 1, "%s not deleted %s" % \
                (name, cli.say.hist())
