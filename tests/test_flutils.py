
from datetime import datetime
from pytest import raises
import os
import pytest

from firelet.flutils import Bunch
from firelet.flutils import encrypt_cookie, decrypt_cookie
from firelet.flutils import flag
from firelet.flutils import get_rss_channels

# Basic Bunch class

def test_bunch_set_get():
    b = Bunch( c=42, a=3, b='44', _a=0)
    assert b.c == 42
    assert b['c'] == 42
    b.c = 17
    assert b.c == 17
    b['c'] = 18
    assert b.c == 18
    assert 'c' in b

def test_bunch_token():
    b = Bunch(c=42, a=3, b='44', _a=0)
    tok = b._token()
    b.validate_token(tok)
    assert tok == 'e4f4206e'
    with raises(Exception):
        b.validate_token('123456')

def test_bunch_update():
    b = Bunch(c=42, a=3, b='44', _a=0)
    d = dict(_a=1, a=2, b=3, c=4, extra=5)
    b.update(d)
    assert b.a == 2 and b.c == 4


# flag

def test_flag_true():
    for x in (1, True, '1', 'True', 'y', 'on' ):
        assert flag(x) == '1'

def test_flag_false():
    for x in (0, False, '0', 'False', 'n', 'off', ''):
        assert flag(x) == '0'

def test_flag_raise():
    for x in ('true', 'false'):
        with raises(Exception):
            flag(x)

# RSS generation

@pytest.fixture
def rss_msg():
    return [
        ['success', datetime(2011,1,1,10,10,10), 'Blah'],
        ['success', datetime(2011,1,1,10,10,20), 'Configuation saved: line'],
        ['success', datetime(2011,1,1,10,10,30), 'Configuration deployed.'],
    ]

def test_get_rss_messages(rss_msg):
    d = get_rss_channels('messages', 'url', msg_list=rss_msg)
    assert 'items' in d
    items = d['items']
    assert len(items) == 3

def test_get_rss_confsaves(rss_msg):
    d = get_rss_channels('confsaves', 'url', msg_list=rss_msg)
    assert 'items' in d
    items = d['items']
    assert len(items) == 1

def test_get_rss_deployments(rss_msg):
    d = get_rss_channels('deployments', 'url', msg_list=rss_msg)
    assert 'items' in d
    items = d['items']
    assert len(items)
    assert 'title' in items[-1]
    assert 'Firelet success: Configuration deployed.' in items[-1]['title']


# Crypto functions

@pytest.fixture
def mocked_os_urandom(monkeypatch):
    monkeypatch.setattr(os, 'urandom', lambda l: '9' * l)

def test_encrypt_cookie(mocked_os_urandom):
    key = 'MEOW' * 4
    enc = encrypt_cookie(key, dict(a=1, b='two', c='\0'))
    assert enc == 'OTk5OTk5OTk5OTk5OTk5OTWHb/EqDVqXyarPPnnDGhHF50T9tgJtokRp6NN2ZzQmcc6irwJwapko6mv+OLYq8LMlLTzlIy3y8hq2ygTeC2M='

def test_decrypt_cookie(mocked_os_urandom):
    key = 'MEOW' * 4
    enc = 'OTk5OTk5OTk5OTk5OTk5OTWHb/EqDVqXyarPPnnDGhHF50T9tgJtokRp6NN2ZzQmcc6irwJwapko6mv+OLYq8LMlLTzlIy3y8hq2ygTeC2M='
    d = decrypt_cookie(key, enc)
    assert d == dict(a=1, b='two', c='\0')

def test_encrypt_then_decrypt(mocked_os_urandom):
    key = 'MEOW' * 4
    d = dict(longvalue="longstring" * 333)

    enc = encrypt_cookie(key, d)
    dec = decrypt_cookie(key, enc)
    assert d == dec

