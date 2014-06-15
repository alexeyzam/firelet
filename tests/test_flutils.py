
import pytest
import os
from datetime import datetime

from firelet.flutils import encrypt_cookie, decrypt_cookie
from firelet.flutils import get_rss_channels

# RSS generation

@pytest.fixture
def rss_msg():
    return [
        ['success', datetime(2011,01,01,10,10,10), 'Blah'],
        ['success', datetime(2011,01,01,10,10,20), 'Configuation saved: line'],
        ['success', datetime(2011,01,01,10,10,30), 'Configuration deployed.'],
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

