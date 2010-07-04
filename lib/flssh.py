
from pxssh import pxssh, ExceptionPxssh
from itertools import dropwhile, takewhile, groupby

def get_confs(li, timeout=10, keep_sessions=False, username='firelet'):
    """Connects to the firewall, get the configuration and return:
        { host: [session, ip_addr, iptables-save, interfaces], ... }
    """
    d = {}
    try:
        for hostname, ip_addr in li:
            p = pxssh()
            p.login(ip_addr, username)
            assert p.isalive()
            d[hostname] = [p, ip_addr]
    except Exception:
        for p, ip_addr in d.values():
            try:
                p.logout()  # logout from the existing connections
            except:
                pass
        raise Exception

    for hostname, (p, ip_addr) in d.iteritems():
        p.sendline('sudo /sbin/iptables-save')
        p.prompt()
        ret = p.before
        ret = [r.rstrip() for r in ret.split('\n')]
        d[hostname].append(ret)
        p.sendline('/bin/ip addr show')
        p.prompt()
        ret = p.before
        ret = [r.rstrip() for r in ret.split('\n')]
        d[hostname].append(ret)

    for name, (p, ip_addr, iptables, y) in d.iteritems():
        ipt = parse_iptables_save(iptables)
        d[name][2] = ipt



    if keep_sessions:
        return d

    for p, ip_addr, x, y in d.values():
        try:
            p.logout()  # logout from the existing connections
        except:
            pass

    return d


def parse_iptables_save(s):

    def chain(m):
        return [m.split()[1]]

    s = (q for q in s)

    block = takewhile(lambda x:x != 'COMMIT',
                       dropwhile(lambda x: x != '*nat', s))
    rules = dropwhile(lambda x: x[0] in ('*', ':'), block)
    r2 = groupby(rules, chain)

    block = takewhile(lambda x:x != 'COMMIT',
                       dropwhile(lambda x: x != '*filter', s))
    rules = dropwhile(lambda x: x[0] in ('*', ':'), block)
    r2 = groupby(rules, chain)

    i = {'nat':{'PREROUTING': [], 'POSTROUTING': [], 'OUTPUT': []},
         'filter':{'INPUT': [], 'FORWARD': [], 'OUTPUT': []} }

    for chain, rules in r2:
        i['filter'][chain[0]] = [r for r in rules]

    return i



def parse_conf(iptables, interfaces):
    pass

d  = get_confs( [('loc','127.0.0.1'),]  )
print repr(d)


