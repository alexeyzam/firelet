from lib import mailer

from lib.flcore import *
import shutil

from nose.tools import assert_raises, with_setup

#TODO: migration to network objects
#TODO: parallel SSH
#TODO: SSH check and deployment

def setup_dir():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')

def teardown_dir():
    shutil.rmtree('test/firewalltmp', True)



# #  Testing flssh module  # #

def setup_dummy_flssh():
    from lib import flssh
    setup_dir()
    def dummy_sl(self, a):
        n = self.my_hostname
        print "Sending '%s' to bogus '%s'" % (a, n)
        if 'save' in a:
            self.before = open('test/iptables-save-%s' % n).read()
        else:
            self.before = open('test/ip-addr-show-%s' % n).read()
    flssh.pxssh.login = flssh.pxssh.isalive = flssh.pxssh.prompt = flssh.pxssh.logout = lambda *x: True
    flssh.pxssh.sendline = dummy_sl
    flssh.isbogus = True
    globals()['flssh'] = flssh

def setup_real_flssh():  #FIXME: this stuff is not working properly - once the dummy setup is run the module stays
    print 'setup real flssh'
    from lib import flssh
    globals()['flssh'] = flssh
    setup_dir()

def teardown_flssh():
    print "flssh teardown"
#    del(globals()['flssh'])
    teardown_dir()

@with_setup(setup_real_flssh, teardown_flssh)
def test_get_confs_remote_real():
    return
    """Requires test hosts to be available"""

    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = DumbFireSet(repodir='test/firewalltmp')
    fs._get_confs()
    assert fs._remote_confs == {
        'Bilbo': [None, '10.66.2.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth1': ('10.66.2.1/24', 'fe80::a00:27ff:fe52:a8b2/64'), 'eth0': ('10.66.1.2/24', 'fe80::a00:27ff:fe81:1366/64')}],
        'Fangorn': [None, '10.66.2.2', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth0': ('10.66.2.2/24', 'fe80::a00:27ff:fe77:6d19/64')}],
        'Gandalf': [None, '10.66.1.1', {'filter': '', 'nat': '-A POSTROUTING -o eth0 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth1': ('10.66.1.1/24', 'fe80::a00:27ff:fee6:4b3e/64'), 'eth0': ('172.16.2.223/17', 'fe80::a00:27ff:fe03:d05e/64')}],
        'Smeagol': [None, '10.66.1.3', {'filter': '', 'nat': ''}, {'lo': ('127.0.0.1/8', '::1/128'), 'add': (None, None),
            'eth0': ('10.66.1.3/24', 'fe80::a00:27ff:fe75:2c75/64')}]}

    fs._check_ifaces()


@with_setup(setup_dummy_flssh)
def test_get_confs_local_dummy():
    d  = flssh.get_confs( {'localhost':['127.0.0.1']} )
    assert d == {'localhost': [None, '127.0.0.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'teredo': (None, 'fe80::ffff:ffff:ffff/64'), 'wlan0': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'), 'eth0': (None, None)}]}


@with_setup(setup_dummy_flssh, teardown_dir)
def test_get_confs3():
    fs = DumbFireSet(repodir='test/firewalltmp')
    fs._get_confs()
    print 'fsconfs', repr(fs._remote_confs)
    assert fs._remote_confs == {'Bilbo': [None, '10.66.2.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('10.66.1.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Fangorn': [None, '10.66.2.2', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Gandalf': [None, '10.66.1.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.1.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('172.16.2.223/24', 'fe80::3939:3939:3939:3939/64')}], 'Smeagol': [None, '10.66.1.3', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.1.3/24', 'fe80::3939:3939:3939:3939/64')}]}

#@with_setup(setup_dummy_flssh, teardown_dir)
#def test_get_confs4():
#    fs = DumbFireSet(repodir='test/firewalltmp')
#    fs._get_confs()
#    fs._check_ifaces()
#    rd = fs.compile_dict(hosts=fs.hosts)









# #  User management testing  # #

@with_setup(setup_dir, teardown_flssh)
def test_user_management():
    u = Users(d='test/firewalltmp')
    u.create('Totoro', 'admin', 'rawr', 'totoro@nowhere.forest')
    assert_raises(Exception,  u.create, 'Totoro', '', '', '')
    u.validate('Totoro', 'rawr')
    assert_raises(Exception, u.validate, 'Totoro', 'booo')
    u.update('Totoro', role='user')
    assert u._users['Totoro'][0] == 'user'
    u.update('Totoro', pwd='')
    u.update('Totoro', email='')
    assert u._users['Totoro'][2] == ''
    assert_raises(Exception, u.update, 'Totoro2', 'email=""')
    u.delete('Totoro')
    assert_raises(Exception,  u.delete, 'Totoro')


# #  FireSet testing # #

@with_setup(setup_dir, teardown_flssh)
def test_gitfireset():
    fs = GitFireSet(repodir='test/firewalltmp')
    return #FIXME
    assert fs.save_needed() == False
    fs.save('test')
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False
    fs.rollback(2)
    assert fs.save_needed() == False
    vl = version_list()
    # assert
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'network'):
        fs.delete(t, 1)
        tmp = len(fs.__dict__[t])
        assert fs.save_needed() == True
        assert tmp == len(fs.__dict__[t]) - 1
    fs.save('test')
    assert fs.save_needed() == False
    tmp = fs.rules
    fs.rule_moveup(2)
    assert fs.save_needed() == True
    assert tmp != fs.rules
    fs.rule_movedown(1)
    assert tmp == fs.rules


@with_setup(setup_dir, teardown_flssh)
def test_dumbfireset():
    fs = DumbFireSet(repodir='test/firewalltmp')
    assert fs.save_needed() == False
    fs.save('save')
    assert fs.save_needed() == False
    fs.reset()
    assert fs.save_needed() == False
    fs.rollback(2)
    assert fs.save_needed() == False
    vl = fs.version_list()
    # assert
    for t in ('rules', 'hosts', 'hostgroups', 'services', 'networks'):
        tmp = len(fs.__dict__[t])
        fs.delete(t, 0)
        assert fs.save_needed() == True, t
        assert tmp == len(fs.__dict__[t]) + 1, t
    fs.save('test')
    assert fs.save_needed() == False
    orig_rules = fs.rules[:] # copy
    fs.rule_moveup(2)
    assert fs.save_needed() == True
    assert orig_rules != fs.rules
    fs.rule_movedown(1)
    assert orig_rules == fs.rules

    fs.rule_movedown(1)
    assert orig_rules != fs.rules
    assert fs.save_needed() == True
    fs.reset()
    assert fs.save_needed() == False
    assert orig_rules == fs.rules




# #  IP address handling  # #


def test_network_update():
    assert Network('','255.255.255.255',8).ip_addr == '255.0.0.0'
    assert Network('','255.255.255.255',16).ip_addr == '255.255.0.0'
    assert Network('','255.255.255.255',24).ip_addr == '255.255.255.0'
    assert Network('','255.255.255.255',27).ip_addr == '255.255.255.224'
    assert Network('','255.255.255.255',28).ip_addr == '255.255.255.240'
    assert Network('','255.255.255.255',29).ip_addr == '255.255.255.248'
    assert Network('','255.255.255.255',30).ip_addr == '255.255.255.252'


def test_contain_nets():
    assert Network('', '255.255.255.255', 16) in Network('', '255.255.255.255', 8)
    assert Network('', '255.255.255.255', 16) in Network('', '255.255.255.255', 16)
    assert Network('', '255.255.255.255', 8) not in Network('', '255.255.255.255', 16)
    assert Network('', '1.0.0.0', 17) in Network('', '1.0.0.0', 16)
    assert Network('', '1.0.0.0', 16) in Network('', '1.0.0.0', 16)
    assert Network('', '1.0.0.0', 15) not in Network('', '1.0.0.0', 16)
    assert Network('', '42.42.42.42', 15) not in Network('','42.42.42.42', 16)
    assert Network('', '42.42.42.42', 16) in Network('','42.42.42.42', 16)
    assert Network('', '42.42.42.42', 17) in Network('','42.42.42.42', 16)

def test_contain_hosts():
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', 28)
    assert Host('h', 'eth0', '1.1.1.15') in Network('h', '1.1.1.0', 28)
    assert Host('h', 'eth0', '1.1.1.16') not in Network('h', '1.1.1.0', 28)
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', 24)
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', 8)
    assert Host('h', 'eth0', '1.1.1.1') not in Network('h', '1.1.2.0', 24)
    assert Host('h', 'eth0', '1.1.1.1') not in Network('h', '10.1.1.0', 8)

def test_compare():
    from netaddr import IPNetwork
    for x in xrange(0, 32):
        n=IPNetwork('255.1.1.1/%d' % x)
        ok = n.network
        mine = Network('','255.1.1.1', x).ip_addr
        print 'ok', ok, 'mine', mine, 'len', x
        assert str(mine) == str(ok)


def test_flattening():
    hg2 = HostGroup(childs=[Host('h', 'b', 'i')])
    hg3 = HostGroup(childs=[Network('n', '2.2.2.0', 24), hg2])
    hg = HostGroup(childs=[hg2, hg3])
    assert ['h', 'h'] == [h.name for h in hg.hosts()]
    assert ['n'] == [h.name for h in hg.networks()], repr(hg.networks())


# # Rule compliation and deployment testing # #

@with_setup(setup_dir, teardown_flssh)
def test_compilation():
    fs = DumbFireSet(repodir='test/firewalltmp')
    compiled = fs.compile()
    print repr(compiled)
    r =['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT', '-A FORWARD --log-level 1 --log-prefix default -j LOG', '-A FORWARD -j DROP']
    assert compiled == r, "Compilation incorrect" + repr(compiled)

@with_setup(setup_dir, teardown_flssh)
def test_select_rules():
    fs = DumbFireSet(repodir='test/firewalltmp')
    rd = fs.compile_dict()
    print repr(rd)
    assert rd == {'Bilbo': {'eth1': [], 'eth0': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']}, 'Fangorn': {'eth0': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT']}, 'Gandalf': {'eth1': ['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT'], 'eth0': ['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT']}, 'Smeagol': {'eth0': ['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']}}



# #  Test JSON lib  # #

def json_loop(obj):
    return json.loads(json.dumps(obj, sort_keys=True))

def test_json1():
    d = {'string':'string', 's2':6, 's3':7.7, 's4':True, 's5':False}
    assert d == json_loop(d)

def test_json2():
    d = {'string':'string', 's2':6, 's3':7.7, 's4':True, 's5':False}
    assert d == json_loop(d)
    #TODO: should I feel confident about that floating point number?
    assert json.dumps(d) == '{"s3": 7.7000000000000002, "s2": 6, "string": "string", "s5": false, "s4": true}'

def test_json3():
    d = {'d1':{'d2':{'d3':{'d4':{'d5':{'this is getting':'boring'}}}}}}
    assert d == json_loop(d)
    assert json.dumps(d) == '{"d1": {"d2": {"d3": {"d4": {"d5": {"this is getting": "boring"}}}}}}'

def test_json4():
    d = [x for x in xrange(42)]
    assert d == json_loop(d)

def test_json5():
    """Keys are casted to strings, integers are not preserved"""
    d = {1:1, 2:2, 3:3}
    assert d != json_loop(d)

def test_json_files():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    d = {'d1':{'d2':{'d3':{'d4':{'d5':{'this is getting':'boring'}}}}}}
    savejson('jfile', d, d='test/firewalltmp')
    nd = loadjson('jfile', d='test/firewalltmp')
    assert d == nd

# #  Test cartesian product  # #

def test_product_2_6():
    from itertools import product

    assert tuple(product([1,2,3,4,5,'O HI'],['a','b','c','d',42])) == (
        (1, 'a'), (1, 'b'), (1, 'c'), (1, 'd'), (1, 42), (2, 'a'), (2, 'b'), (2, 'c'), (2, 'd'), (2, 42),
        (3, 'a'), (3, 'b'), (3, 'c'), (3, 'd'), (3, 42), (4, 'a'), (4, 'b'), (4, 'c'), (4, 'd'), (4, 42),
        (5, 'a'), (5, 'b'), (5, 'c'), (5, 'd'), (5, 42), ('O HI', 'a'), ('O HI', 'b'), ('O HI', 'c'),
        ('O HI', 'd'), ('O HI', 42))


def test_product_2_5():

    def product(*args, **kwds):
        """List cartesian product - not available in Python 2.5"""
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    assert tuple(product([1,2,3,4,5,'O HI'],['a','b','c','d',42])) == (
        (1, 'a'), (1, 'b'), (1, 'c'), (1, 'd'), (1, 42), (2, 'a'), (2, 'b'), (2, 'c'), (2, 'd'), (2, 42),
        (3, 'a'), (3, 'b'), (3, 'c'), (3, 'd'), (3, 42), (4, 'a'), (4, 'b'), (4, 'c'), (4, 'd'), (4, 42),
        (5, 'a'), (5, 'b'), (5, 'c'), (5, 'd'), (5, 42), ('O HI', 'a'), ('O HI', 'b'), ('O HI', 'c'),
        ('O HI', 'd'), ('O HI', 42))



