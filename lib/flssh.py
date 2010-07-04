
from pxssh import pxssh, ExceptionPxssh

def get_confs(li, timeout=10, keep_sessions=False, username='firelet'):
    """Connects to the firewall, get the configuration and return:
        { host: [session, ip_addr, iptables-save, interfaces], ... }
    """
    d = {}
    try:
        for hostname, ip_addr in li:
            p = pxssh()
            p.my_hostname = hostname # used for testing - urgh
            p.login(ip_addr, username)
            assert p.isalive(), "Host %s not responding to SSH after login." % hostname
            d[hostname] = [p, ip_addr]
    except Exception, e:
        for p, ip_addr in d.values():
            try:
                p.logout()  # logout from the existing connections
            except:
                pass
#        raise Exception, str(e) + 'Unable to login on %s' % actual

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

    for name, (p, ip_addr, iptables, ip_a_s) in d.iteritems():
        d[name][2] = parse_iptables_save(iptables)
        d[name][3] = parse_ip_addr_show(ip_a_s)

    if keep_sessions:
        return d

    for name, (p, ip_addr, iptables, y) in d.iteritems():
        try:
            p.logout()  # logout from the existing connections
            d[name][0] = None
        except:
            pass

    return d


def parse_iptables_save(s):

    def start(li, tag):
        for n, item in enumerate(li):
            if item == tag:
                return li[n:]
        return []

    def get_block(li, tag):
        li = start(li, tag)
        for n, item in enumerate(li):
            if item == 'COMMIT':
                return li[:n]
        return []

    def good(x):
        return x.startswith(('-A PREROUTING', '-A POSTROUTING', '-A OUTPUT', '-A INPUT', '-A FORWARD'))

    i = {'nat':{}, 'filter':{} }

    block = get_block(s, '*nat')
    b = filter(good, block)
    i['nat'] = '\n'.join(b)
#    for q in ('PREROUTING', 'POSTROUTING', 'OUTPUT'):
#        i['nat'][q] = '\n'.join(x for x in block if x.startswith('-A %s' % q))

    block = get_block(s, '*filter')
    b = filter(good, block)
    i['filter'] = '\n'.join(b)

#    for q in ('INPUT', 'OUTPUT', 'FORWARD'):
#        i['filter'][q] = '\n'.join(x for x in block if x.startswith('-A %s' % q))

    return i


def parse_ip_addr_show(s):
    """Parse the output of 'ip addr show' and returns a dict:
    {'iface': (ip_addr_v4, ip_addr_v6)} """
    iface = ip_addr_v4 = ip_addr_v6 = None
    d = {}
    for q in s:
        if q and not q.startswith('  '):   # new interface definition
            if iface:
                d[iface] = (ip_addr_v4, ip_addr_v6)
            iface = q.split()[1][:-1]  # second field, without trailing column
            ip_addr_v4 = ip_addr_v6 = None
        elif q.startswith('    inet '):
            ip_addr_v4 = q.split()[1]
        elif q.startswith('    inet6 '):
            ip_addr_v6 = q.split()[1]
    if iface:
        d[iface] = (ip_addr_v4, ip_addr_v6)

    return d





