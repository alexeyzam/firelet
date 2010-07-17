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

#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs4():
#    fs = DumbFireSet(repodir='/tmp/firelet')
#    fs._get_confs()
#    fs._check_ifaces()
#    rd = fs.compile_dict(hosts=fs.hosts)
