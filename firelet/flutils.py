# Firelet - Distributed firewall management.
# Copyright (C) 2014 Federico Ceratto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from Crypto.Cipher import AES
from copy import deepcopy
from datetime import datetime
from optparse import OptionParser
from warnings import warn
import base64
import hashlib
import hmac
import json
import logging
import os

log = logging.getLogger(__name__)

def compare_digest(a, b):
    """Time-constant comparison. Less secure than hmac.compare_digest
    See http://legacy.python.org/dev/peps/pep-0466/
    """
    if len(a) != len(b):
        return False

    flag = 0
    for x, y in zip(a, b):
        flag |= ord(x) ^ ord(y)

    return flag == 0

if not hasattr(hmac, 'compare_digest'):
    warn("hmac.compare_digest is missing, using workaround.")
    hmac.compare_digest = constant_time_compare


def cli_args(args=None): # pragma: no cover
    """Parse command line arguments"""
    parser = OptionParser()
    parser.add_option("-c", "--conffile", dest="conffile",
        default='firelet.ini', help="configuration file", metavar="FILE")
    parser.add_option("-r", "--repodir", dest="repodir",
        help="configuration repository dir")
    parser.add_option("-D", "--debug",
        action="store_true", dest="debug", default=False,
        help="run in debug mode and print messages to stdout")
    parser.add_option("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help="print less messages to stdout")
    if args:
        return parser.parse_args(args=args)
    return parser.parse_args()

class Alert(Exception):
    """Custom exception used to send an alert message to the user"""


class Bunch(object):
    """A dict that exposes its values as attributes."""
    def __init__(self, **kw):
        self.__dict__ = dict(kw)

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, name):
        return self.__dict__.__getitem__(name)

    def __setitem__(self, name, value):
        return self.__dict__.__setitem__(name, value)

    def __iter__(self):
        return self.__dict__.__iter__()

    def keys(self):
        """Get the instance attributes

        :rtype: list
        """
        return self.__dict__.keys()

    def _token(self):
        """Generate a simple hash to detect changes in the bunch attributes
        """
        h = hashlib.md5()
        [h.update(k + str(v)) for k, v in sorted(self.__dict__.iteritems())]
        return h.hexdigest()[:8]

    def validate_token(self, token):
        """Check if the given token matches the instance own token to ensure
        that the instance attributes has not been modified.
        The token is a hash of the instance's attributes.

        :param token: token
        :type token: str
        :returns: True or False
        """
        assert token == self._token(), \
        "Unable to update: one or more items has been modified in the meantime."

    def attr_dict(self):
        """Provide a copy of the internal dict, with a token"""
        d = deepcopy(self.__dict__)
        d['token'] = self._token()
        return d

    def update(self, d):
        """Set/update the internal dictionary"""
        for k in self.__dict__:
            self.__dict__[k] = d[k]


def flag(s):
    """Parse string-based flags"""
    if s in (1, True, '1', 'True', 'y', 'on' ):
        return '1'
    elif s in (0, False, '0', 'False', 'n', 'off', ''):
        return '0'
    else:
        raise Exception("%r is not a valid flag value" % s)

def extract(d, keys):
    """Returns a new dict with only the chosen keys, if present"""
    return dict((k, d[k]) for k in keys if k in d)

def extract_all(d, keys):
    """Returns a new dict with only the chosen keys"""
    return dict((k, d[k]) for k in keys)

# RSS feeds generation

def append_rss_item(channel, url, level, msg, ts, items):
    """Append a new RSS item to items"""
    i = Bunch(
        title = "Firelet %s: %s" % (level, msg),
        desc = msg,
        link = url,
        build_date = '',
        pub_date = ts.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        guid = ts.isoformat()
    )
    items.append(i)

def get_rss_channels(channel, url, msg_list=[]):
    """Generate RSS feeds for different channels"""
    if channel not in ('messages', 'confsaves', 'deployments'):
        raise Exception("Inexistent RSS channel")

    utc_rfc822 = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    c = Bunch(
        title = 'Firelet %s RSS' % channel,
        desc = "%s feed" % channel,
        link = url,
        build_date = utc_rfc822,
        pub_date = utc_rfc822,
        channel = channel
    )

    items = []

    if channel == 'messages':
        for level, ts, msg in msg_list:
            append_rss_item(channel, url, level, msg, ts, items)

    elif channel == 'confsaves':
        for level, ts, msg in msg_list:
            if 'saved:' in msg:
                append_rss_item(channel, url, level, msg, ts, items)

    elif channel == 'deployments':
        for level, ts, msg in msg_list:
            if 'deployed' in msg:
                append_rss_item(channel, url, level, msg, ts, items)

    return dict(c=c, items=items)


def encrypt_cookie(key, data):
    """Generate encrypted and signed cookie content
    :returns: str
    """
    block_size = AES.block_size

    # Convert to JSON.
    # Sort keys to have a deterministic behavior for testing.
    cleartext = json.dumps(data, sort_keys=True)

    # Encrypt using AES in CFB mode with random IV
    iv = os.urandom(block_size)
    assert len(iv) == block_size
    aes = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = aes.encrypt(cleartext)
    assert len(ciphertext) == len(cleartext)

    # Sign the ciphertext with HMAC
    sig = hmac.new(key, ciphertext).digest()
    assert len(sig) == block_size

    # Concatenate IV, signature, ciphertext
    encoded = base64.b64encode(iv + sig + ciphertext)
    assert len(encoded) <= 4093, "Cookie size exceeding 4093 bytes"
    return encoded

def decrypt_cookie(key, enc):
    """Decrypt cookie content and check signature
    """
    block_size = AES.block_size

    # Split string
    enc = base64.b64decode(enc)
    iv = enc[:block_size]
    sig = enc[block_size:block_size * 2]
    ciphertext = enc[block_size * 2:]

    # Regenerate signature
    correct_sig = hmac.new(key, ciphertext).digest()

    # Compare signatures using a time-constant function
    # http://bugs.python.org/issue15061
    sig_is_valid = hmac.compare_digest(sig, correct_sig)
    if not sig_is_valid:
        raise Exception("Invalid signature")

    # Decrypt ciphertext
    aes = AES.new(key, AES.MODE_CFB, iv)
    cleartext = aes.decrypt(ciphertext)

    # Parse JSON contents
    return json.loads(cleartext)

