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

from pytest import raises
from webtest import TestApp, AppError
import bottle
import logging
import pytest

from firelet import fireletd
from firelet.flcore import GitFireSet, DemoGitFireSet, Users
from firelet.flssh import MockSSHConnector
from firelet.mailer import Mailer
import firelet.flssh

log = logging.getLogger(__name__)

# TODO: fix skipped tests
skip = pytest.mark.skipif("True")

class Conf(object):
    public_url = 'http://localhost'
    stop_on_extra_interfaces = False

@pytest.fixture
def mailer(monkeypatch):
    mailer = Mailer(
        sender = 'bogus@sender.org',
        recipients = 'bogus@recipient.org',
        smtp_server = 'bogus-email-server',
    )
    monkeypatch.setattr(mailer, 'send_msg', lambda *a, **kw: None)
    return mailer


@pytest.fixture
def mock_ssh(monkeypatch):
    # FIXME: broken
    monkeypatch.setattr(firelet.flssh, 'SSHConnector', MockSSHConnector)

@pytest.fixture
def raw_app(repodir, mailer, mock_ssh):
    """Create app (without logging in)"""
    bottle.debug(True)
    app = TestApp(fireletd.app)
    assert not app.cookies

    fireletd.conf = Conf()
    assert fireletd.conf

    fireletd.users = Users(d=repodir)
    fireletd.mailer = mailer
    fireletd.fs = GitFireSet(repodir)

    return app

@pytest.fixture
def webapp(raw_app):
    """Create app and log in"""
    assert not raw_app.cookies
    raw_app.post('/login', {'user': 'Ada', 'pwd': 'ada'})
    assert raw_app.cookies.keys() == ['fireletd']
    return raw_app

# Unauthenticated tests

def test_bogus_page(raw_app):
    with raises(AppError):
        raw_app.get('/bogus_page')

def test_index_page_unauth(raw_app):
    out = raw_app.get('/')
    assert out.status_code == 200

@skip
def test_login_unauth(raw_app):
    out = raw_app.get('/login')
    assert out.status_code == 200

def test_login_incorrect(raw_app):
    assert not raw_app.cookies
    out = raw_app.post('/login', {'user': 'bogus', 'pwd': 'bogus'})
    assert not raw_app.cookies

def test_login_correct(raw_app):
    assert not raw_app.cookies
    raw_app.post('/login', {'user': 'Ada', 'pwd': 'ada'})
    assert raw_app.cookies.keys() == ['fireletd']

def test_logout_unauth(raw_app):
    out = raw_app.get('/logout')
    assert out.status_code == 302 # redirect

# Authenticated tests

def test_index_page(webapp):
    out = webapp.get('/')
    assert out.status_code == 200
    assert 'DOCTYPE' in out.text
    assert 'body' in out.text
    assert 'Distributed firewall management' in out
    assert '</html>' in out

def test_logout(webapp):
    assert webapp.cookies.keys() == ['fireletd']
    webapp.get('/logout')
    assert not webapp.cookies.keys()

def test_double_login(webapp):
    # log in again
    assert webapp.cookies.keys() == ['fireletd']
    webapp.post('/login', {'user': 'Ada', 'pwd': 'ada'})
    assert webapp.cookies.keys() == ['fireletd']

def test_messages(webapp):
    out = webapp.get('/messages')
    assert str(out.html) == ''

def test_ruleset(webapp):
    out = webapp.get('/ruleset')
    assert out.pyquery('table#items')
    assert 'Ssh access from the test workstation' in out.text
    rules = out.pyquery('table#items tr')
    assert len(rules) == 11 # 10 rules plus header

def test_ruleset_post_delete(webapp):
    out = webapp.post('/ruleset', dict(
        action='delete',
        rid=0,
    ))
    assert out.json == {u'ok': True}

    out = webapp.get('/ruleset')
    rules = out.pyquery('table#items tr')
    assert len(rules) == 10 # 9 rules plus header

def test_ruleset_post_moveup(webapp):
    out = webapp.post('/ruleset', dict(
        action='moveup',
        rid=1,
    ))
    assert out.json == {u'ok': True}

@skip
def test_ruleset_post_moveup_incorrect(webapp):
    out = webapp.post('/ruleset', dict(
        action='moveup',
        rid=0,
    ))
    assert out.json == {u'ok': True}

def test_ruleset_post_movedown(webapp):
    out = webapp.post('/ruleset', dict(
        action='movedown',
        rid=1,
    ))
    assert out.json == {u'ok': True}

#TODO: movedown error on last rule

def test_ruleset_post_disable(webapp):
    out = webapp.post('/ruleset', dict(
        action='disable',
        rid=1,
    ))
    assert out.json == {u'ok': True}

def test_ruleset_post_enable(webapp):
    out = webapp.post('/ruleset', dict(
        action='enable',
        rid=1,
    ))
    assert out.json == {u'ok': True}

@skip
def test_ruleset_post_save(webapp):
    out = webapp.post('/ruleset', dict(
        action='save',
        rid=1,
        name='newrule',
        src='a',
        src_serv='SSH',
        dst='b',
        dst_serv='SSH',
        desc='New rule',
    ))
    assert 0, out
    assert out.json == {u'ok': True}

def test_ruleset_post_newabove(webapp):
    out = webapp.get('/ruleset')
    rules = out.pyquery('table#items tr')
    assert len(rules) == 11 # 10 rules plus header
    out = webapp.post('/ruleset', dict(
        action='newabove',
        rid=1,
    ))
    #TODO: return an ack
    out = webapp.get('/ruleset')
    rules = out.pyquery('table#items tr')
    assert len(rules) == 12

def test_ruleset_post_newbelow(webapp):
    out = webapp.get('/ruleset')
    rules = out.pyquery('table#items tr')
    assert len(rules) == 11 # 10 rules plus header
    out = webapp.post('/ruleset', dict(
        action='newbelow',
        rid=1,
    ))
    #TODO: return an ack
    out = webapp.get('/ruleset')
    rules = out.pyquery('table#items tr')
    assert len(rules) == 12

def test_ruleset_post_unknown_action(webapp):
    with raises(Exception):
        webapp.post('/ruleset', dict(action='bogus', rid=1))


def test_sib_names(webapp):
    out = webapp.post('/sib_names')
    out.json == {u'sib_names': [u'AllSystems', u'BorderFW:eth0', u'BorderFW:eth1', u'BorderFW:eth2', u'Clients', u'InternalFW:eth0', u'InternalFW:eth1', u'SSHnodes', u'Server001:eth0', u'Servers', u'Smeagol:eth0', u'Tester:eth1', u'WebServers']}


def test_hostgroups(webapp):
    out = webapp.get('/hostgroups')
    assert 'SSHnodes' in out
    assert len(out.pyquery('table#items tr')) == 6

def test_hostgroups_post_save_new_hg(webapp):
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 6
    out = webapp.post('/hostgroups', dict(
        action = 'save',
        childs = 'Border, Localhost',
        rid = '',
    ))
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 7

def test_hostgroups_post_save_update(webapp):
    # update existing hg
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 6
    out = webapp.post('/hostgroups', dict(
        action = 'save',
        childs = 'Border, Localhost',
        rid = '2',
    ))
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 6

def test_hostgroups_post_delete(webapp):
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 6
    out = webapp.post('/hostgroups', dict(
        action='delete',
        rid=1,
    ))
    out = webapp.get('/hostgroups')
    assert len(out.pyquery('table#items tr')) == 5

def test_hostgroups_post_fetch(webapp):
    out = webapp.post('/hostgroups', dict(
        action='fetch',
        rid=1,
    ))
    assert out.json == {u'token': u'ec0194a392e9c8a', u'childs': [u'Smeagol:eth0'], u'name': u'SSHnodes'}

def test_hostgroups_post_unknown_action(webapp):
    with raises(Exception):
        webapp.post('/hostgroups', dict(action='bogus', rid=''))


def test_hosts(webapp):
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 9

def test_hosts_post_delete(webapp):
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 9
    out = webapp.post('/hosts', dict(
        action='delete',
        rid=1,
    ))
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 8

def test_hosts_post_save_new_host(webapp):
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 9
    out = webapp.post('/hosts', dict(
        action = 'save',
        hostname = 'foo',
        iface = 'eth0',
        ip_addr = '1.2.3.4',
        local_fw = '1',
        masklen = '24',
        mng = '1',
        network_fw = '0',
        rid = '',
        routed = 'Internet',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 10

def test_hosts_post_save_update_host(webapp):
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 9
    out = webapp.post('/hosts', dict(
        action = 'save',
        hostname = 'foo',
        iface = 'eth0',
        ip_addr = '1.2.3.4',
        local_fw = '1',
        masklen = '24',
        mng = '1',
        network_fw = '0',
        rid = '2',
        routed = 'Internet',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/hosts')
    assert len(out.pyquery('table#items tr')) == 9

def test_hosts_post_fetch(webapp):
    out = webapp.post('/hosts', dict(
        action='fetch',
        rid=1,
    ))
    assert out.json == {u'masklen': u'24', u'iface': u'eth1', u'ip_addr': u'10.66.2.1', u'hostname': u'InternalFW', u'routed': [], u'local_fw': 1, u'token': u'3085af0c32f194b2', u'network_fw': 1, u'mng': 1}

def test_hosts_post_unknown_action(webapp):
    with raises(Exception):
        webapp.post('/hosts', dict(action='bogus', rid=''))


def test_net_names(webapp):
    out = webapp.post('/net_names')
    assert out.json == {u'net_names': [u'Internet', u'production_net', u'rivendell', u'shire']}


def test_networks(webapp):
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 5

def test_networks_post_save_new_network(webapp):
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 5
    out = webapp.post('/networks', dict(
        action = 'save',
        name = 'foo',
        ip_addr = '1.2.3.4',
        masklen = '24',
        rid = '',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 6

    out = webapp.post('/networks', dict(
        action='fetch',
        rid=4,
    ))
    assert out.json['name'] == 'foo'

def test_networks_post_save_update_network(webapp):
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 5
    out = webapp.post('/networks', dict(
        action = 'save',
        name = 'foo',
        ip_addr = '1.2.3.4',
        masklen = '24',
        rid = '2',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 5

def test_networks_post_delete(webapp):
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 5
    out = webapp.post('/networks', dict(
        action='delete',
        rid=1,
    ))
    out = webapp.get('/networks')
    assert len(out.pyquery('table#items tr')) == 4

def test_networks_post_fetch(webapp):
    out = webapp.post('/networks', dict(
        action='fetch',
        rid=1,
    ))
    assert out.json == {u'masklen': 24, u'ip_addr': u'10.66.2.0', u'name': u'production_net', u'token': u'5b60bae3fb2b9766'}

def test_networks_post_unknown_action(webapp):
    with raises(Exception):
        webapp.post('/networks', dict(action='bogus', rid=''))


def test_services(webapp):
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 8

def test_services_post_save_new_network_tcp(webapp):
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 8
    out = webapp.post('/services', dict(
        action = 'save',
        name = 'foo',
        protocol = 'TCP',
        ports = '80',
        rid = '',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 9

    out = webapp.post('/services', dict(
        action='fetch',
        rid=7,
    ))
    assert out.json['name'] == 'foo'

def test_services_post_save_new_network_icmp(webapp):
    out = webapp.post('/services', dict(
        action = 'save',
        name = 'foo',
        protocol = 'ICMP',
        icmp_type = '8',
        rid = '',
    ))
    assert out.json['ok'] == True
    out = webapp.post('/services', dict(
        action='fetch',
        rid=7,
    ))
    assert out.json['name'] == 'foo'
    assert out.json['protocol'] == 'ICMP'
    assert out.json['ports'] == '8'

def test_services_post_save_new_network_other_protocol(webapp):
    out = webapp.post('/services', dict(
        action = 'save',
        name = 'foo',
        protocol = 'AH',
        rid = '',
    ))
    assert out.json['ok'] == True
    out = webapp.post('/services', dict(
        action='fetch',
        rid=7,
    ))
    assert out.json['name'] == 'foo'
    assert out.json['protocol'] == 'AH'

def test_services_post_save_update_network(webapp):
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 8
    out = webapp.post('/services', dict(
        action = 'save',
        name = 'foo',
        protocol = 'TCP',
        ports = '80',
        rid = '2',
    ))
    assert out.json['ok'] == True
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 8

def test_services_post_delete(webapp):
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 8
    out = webapp.post('/services', dict(
        action='delete',
        rid=1,
    ))
    out = webapp.get('/services')
    assert len(out.pyquery('table#items tr')) == 7

def test_services_post_fetch(webapp):
    out = webapp.post('/services', dict(
        action='fetch',
        rid=1,
    ))
    assert out.json == {u'token': u'3de877cfe8d38aaa', u'protocol': u'TCP', u'ports': u'80', u'name': u'HTTP'}

def test_services_post_unknown_action(webapp):
    with raises(Exception):
        webapp.post('/services', dict(action='bogus', rid=''))


def test_manage(webapp):
    out = webapp.get('/manage')
    assert len(out.pyquery('button')) == 3

def test_save_needed(webapp):
    out = webapp.get('/save_needed')
    assert out.json['sn'] == False

def test_save_post(webapp):
    out = webapp.post('/save', dict(
        msg='test',
    ))
    assert out.json['ok'] == True

def test_reset_post(webapp):
    out = webapp.post('/reset')
    assert out.json['ok'] == True

@skip
def test_check_post(webapp):
    out = webapp.post('/api/1/check')
    assert out.json['ok'] == True


def test_rss(webapp):
    out = webapp.get('/rss')
    assert 'rss/deployments' in out

def test_rss_channel(webapp):
    out = webapp.get('/rss/deployments')
    assert 'http://localhost/rss/deployments' in out
    assert 'rss' in out





