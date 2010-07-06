from lib import mailer

from lib.flcore import *
import shutil

from nose.tools import assert_raises

#TODO: migration to network objects
#TODO: parallel SSH
#TODO: SSH check and deployment

from lib import flssh

def test_get_confs():
    def dummy(*a):
        return True
    def dummy_sl(self, *a):
        self.before = ''
    flssh.pxssh.login = flssh.pxssh.isalive = flssh.pxssh.prompt = flssh.pxssh.logout = dummy
    flssh.pxssh.sendline = dummy_sl
    d  = flssh.get_confs( [('localhost','127.0.0.1'),]  )
    assert d == {'localhost': [None, '127.0.0.1', {'filter': '', 'nat': ''}, {}]}


def test_get_confs2():
    def dummy(*a):
        return True
    def dummy_sl(self, a):
        if 'save' in a:
            self.before = open('test/iptables-save-1').read()
        else:
            self.before = open('test/ip-addr-show-1').read()

    flssh.pxssh.login = flssh.pxssh.isalive = flssh.pxssh.prompt = flssh.pxssh.logout = dummy
    flssh.pxssh.sendline = dummy_sl
    d  = flssh.get_confs( [('localhost','127.0.0.1'),]  )

#    assert d == {'localhost': [None, '127.0.0.1', {
#        'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT',
#        'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'},
#        {'lo:': ('127.0.0.1/8', '::1/128'),
#            'teredo:': (None, 'fe80::ffff:ffff:ffff/64'),
#            'wlan0:': ('192.168.1.1/24', 'fe80::219:d2ff:fe26:fb8e/64'),
#            'eth0:': (None, None)
#        }]}



## User management testing

def test_user_management():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
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


## FireSet testing

def test_gitfireset():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
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



def test_dumbfireset():

    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
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




##

def test_ip_parsing():
    for x in xrange(0, 256):
        ipaddr = "%d.%d.%d.%d" % (x, x, x, x)
        assert long_to_dot(dot_to_long(ipaddr)) == ipaddr


def test_flattening():

    hg2 = HostGroup(childs=[Host('h', 'b', 'i')])
    hg3 = HostGroup(childs=[Network('n', 'b', 'c'), hg2])
    hg = HostGroup(childs=[hg2, hg3])
    assert ['h', 'h'] == [h.name for h in hg.hosts()]
    assert ['n'] == [h.name for h in hg.networks()], repr(hg.networks())

def test_contain():
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '28')
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '24')
    assert Host('h', 'eth0', '1.1.1.1') in Network('h', '1.1.1.0', '8')


def test_compilation():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = DumbFireSet(repodir='test/firewalltmp')
    compiled = fs.compile()
    print repr(compiled)
    r =['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT', '-A FORWARD --log-level 1 --log-prefix default -j LOG', '-A FORWARD -j DROP']
    assert compiled == r, "Compilation incorrect" + repr(compiled)

def test_select_rules():
    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = DumbFireSet(repodir='test/firewalltmp')

    rd = fs.compile_dict(hosts=fs.hosts)
    print repr(rd)
    assert rd == {'Bilbo': {'eth1': [[]], 'eth0': [['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']]}, 'Fangorn': {'eth1': [['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.2.2 --dport 80 -j ACCEPT']]}, 'Gandalf': {'eth1': [['-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.1 --dport 443 -j ACCEPT']], 'eth0': [['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 --log-level 2 --log-prefix ssh_mgmt -j LOG', '-A FORWARD -p tcp -s 172.16.2.223 -d 10.0.0.0/255.0.0.0 --dport 22 -j ACCEPT', '-A FORWARD -p udp -s 172.16.2.223 -d 172.16.2.223 --dport 123 -j ACCEPT']]}, 'Smeagol': {'eth0': [['-A FORWARD -s 10.66.1.3 -d 172.16.2.223 --log-level 3 --log-prefix NoSmeagol -j LOG', '-A FORWARD -s 10.66.1.3 -d 172.16.2.223 -j DROP', '-A FORWARD -p tcp -s 10.66.1.2 -d 10.66.1.3 --dport 6660:6669 -j ACCEPT', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 --log-level 2 --log-prefix imap -j LOG', '-A FORWARD -p tcp -s 10.66.1.3 -d 10.66.1.2 -m multiport --dport 143,585,993 -j ACCEPT']]}}


def test_get_confs3():
    def dummy(*a):
        return True
    def dummy_sl(self, a):
        n = self.my_hostname
        if 'save' in a:
            self.before = open('test/iptables-save-%s' % n).read()
        else:
            self.before = open('test/ip-addr-show-%s' % n).read()

    flssh.pxssh.login = flssh.pxssh.isalive = flssh.pxssh.prompt = flssh.pxssh.logout = dummy
    flssh.pxssh.sendline = dummy_sl

    shutil.rmtree('test/firewalltmp', True)
    shutil.copytree('test/', 'test/firewalltmp')
    fs = DumbFireSet(repodir='test/firewalltmp')

    fs._get_confs()
#    rd = fs.compile_dict(hosts=fs.hosts)
    print 'fsconfs', repr(fs.confs)
    assert fs.confs == {'Bilbo': [None, '10.66.2.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('10.66.1.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Fangorn': [None, '10.66.2.2', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.2.2/24', 'fe80::3939:3939:3939:3939/64')}], 'Gandalf': [None, '10.66.1.1', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth1': ('10.66.1.1/24', 'fe80::3939:3939:3939:3939/64'), 'eth0': ('172.16.2.223/24', 'fe80::3939:3939:3939:3939/64')}], 'Smeagol': [None, '10.66.1.3', {'filter': '-A INPUT -s 10.0.0.0/8 -p tcp -m tcp --dport 80 -j ACCEPT\n-A FORWARD -s 1.2.3.4/32 -d 5.6.7.8/32 -p tcp -m multiport --dports 22,80,443 -j ACCEPT\n-A OUTPUT -d 10.10.10.10/32 -p udp -m udp --dport 123 -j ACCEPT', 'nat': '-A POSTROUTING -o eth3 -j MASQUERADE'}, {'lo': ('127.0.0.1/8', '::1/128'), 'eth0': ('10.66.1.3/24', 'fe80::3939:3939:3939:3939/64')}]}


    fs._check_ifaces()
    rd = fs.compile_dict(hosts=fs.hosts)

#    assert False, 'test'



# Test JSON lib

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

if __name__ == '__main__':
    test_get_confs2()
