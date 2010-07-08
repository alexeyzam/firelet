from lib import flssh
import shutil

from nose.tools import assert_raises, with_setup

def dd(d):
    """Debug dict"""
    from simplejson import dumps
    print dumps(d, indent=' ')

# #  Testing flssh module locally # #

def test_sshconnector_getconf():
    # {hostname: [management ip address list ], ... }
    t = {'localhost':['127.0.0.1', ]}
    sx = flssh.SSHConnector(targets=t, username='root')
    confs = sx.get_confs()
    dd(confs)

    assert 'localhost' in confs
