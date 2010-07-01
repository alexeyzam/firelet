import csv
from collections import defaultdict

from netaddr import IPAddress, IPNetwork

protocols = ['IP','TCP', 'UDP', 'OSPF', 'IS-IS', 'SCTP', 'AH', 'ESP']

# Objects

class NetworkObj(object):
    """Can be a host, a network or a hostgroup"""
    pass


class Sys(NetworkObj):
    def __init__(self, name, ifaces={}):
        self.ifaces = ifaces


class Host(NetworkObj):
    def __init__(self, name, iface, addr):
        self.name = name
        self.iface = iface
        self.ip_addr = addr


class Network(NetworkObj):
    def __init__(self, name, addr, mask):
        self.name = name
        self.ip_addr = addr
        self.netmask = mask

    def __contains__(self, item):
        """Check if a host or a network falls inside this network"""
        if isinstance(item, Host):
            return IPAddress(item.ip_addr) in IPNetwork("%s/%s" % (self.ip_addr, self.netmask))




class HostGroup(NetworkObj):

    def __init__(self, childs=[]):
        self.childs = childs

    def _flatten(self, i):
        if hasattr(i, 'childs'):
            return sum(map(self._flatten, i.childs), [])
        return [i]

    def networks(self):
        """Flatten the hostgroup and return its networks"""
        return [n for n in self._flatten(self) if isinstance(n, Network)]

    def hosts(self):
        """Flatten the hostgroup and return its hosts"""
        return filter(lambda i: type(i) == Host, self._flatten(self)) # better?
        return [n for n in self._flatten(self) if isinstance(n, Host)]





# CSV files handling

def loadcsv(n, d='firewall'):
    try:
        f = open("%s/%s.csv" % (d, n))
        r = list(csv.reader(f, delimiter=' '))
        f.close()
    except IOError:
        return []
    return r

def savecsv(filename, stuff):
    f = open(filename, 'wb')
    writer = csv.writer(f,  delimiter=' ')
    writer.writerows(stuff)
    f.close()

def loadrules():
    return loadcsv('rules')

def saverules(rules):
    savecsv('firewall/rules.csv', rules)

def loadhosts():
    return loadcsv('hosts')

def savehosts(h):
    savecsv('firewall/blades.csv', h)


# Firewall ruleset processing


def _resolveitems(items, addr, net, hgs):
    """Flatten host groups tree, used in compile()"""

    def flatten1(item):
        li = addr.get(item), net.get(item), _resolveitems(hgs.get(item), addr, net, hgs)  # should we convert network to string here?
        return filter(None, li)[0]


    if not items:
        return None
    return map(flatten1, items)


def compile(rules, hosts, hostgroups, services, networks):
    """Compile firewall rules to be deployed"""

    # build dictionaries to perform resolution
    addr = dict(((name + ":" + iface),ipa) for name,iface,ipa in hosts) # host to ip_addr
    net = dict((name, (n, mask)) for name, n, mask in networks) # network name
    hgs = dict((entry[0], (entry[1:])) for entry in hostgroups) # host groups
    hg_flat = dict((hg, _resolveitems(hgs[hg], addr, net, hgs)) for hg in hgs) # flattened to hg: hosts or networks

    proto_port = dict((name, (proto, ports)) for name, proto, ports in services) # protocol
    proto_port['*'] = (None, '') # special case for "any"


    # port format: "2:4,5:10,10:33,40,50"

    def res(n):
        if n in addr:
            return (addr[n], )
        elif n in net:
            return (net[n][0] + '/' + net[n][1], )
            return ('/'.join(net[n]), )
        elif n in hg_flat:
            return hg_flat[src][0][0]
        elif n == '*':
            return [None]
        else:
            raise Exception, "Host %s is not defined." % n

    for rule in rules:
        assert rule[0] in ('y', 'n')

    from itertools import product

    compiled = []
    for ena, name, src, src_serv, dst, dst_serv, action, log_val, desc in rules:
        if ena == 'n':
            continue
        assert action in ('ACCEPT', 'DROP'),  'TODO'
        srcs = res(src)
        dsts = res(dst)
        sproto, sports = proto_port[src_serv]
        dproto, dports = proto_port[dst_serv]
        assert sproto in protocols + [None], "Unknown source protocol: %s" % sproto
        assert dproto in protocols + [None], "Unknown dest protocol: %s" % dproto

        if sproto and dproto and sproto != dproto:
            continue # mismatch
        if sproto:
            proto = " -p %s" % sproto.lower()
        elif dproto:
            proto = " -p %s" % dproto.lower()
        else:
            proto = ''

        if sports:
            ms = ' -m multiport' if ',' in sports else ''
            sports = "%s --sport %s" % (ms, sports)
        if dports:
            md = ' -m multiport' if ',' in dports else ''
            dports = "%s --dport %s" % (md, dports)

        # TODO: ensure that 'name' is a-zA-Z0-9_-

        log_val = int(log_val)  #TODO: try/except this

        for src, dst in product(srcs, dsts):
            src = " -s %s" % src if src else ''
            dst = " -d %s" % dst if dst else ''
            if log_val:
                compiled.append("-A FORWARD%s%s%s%s%s --log-level %d --log-prefix %s -j LOG" %   (proto, src, sports, dst, dports, log_val, name))
            compiled.append("-A FORWARD%s%s%s%s%s -j %s" %   (proto, src, sports, dst, dports, action))

    return compiled


def select_rules(hosts, rset):
    """Generate set of rules specific for each host"""

    # r[hostname][interface] = [rule, rule, ... ]
    rd = defaultdict(dict)

    for hostname,iface,ipa in hosts:
        myrules = [ r for r in rset if ipa in r ]
        if iface in rd[hostname]:
            rd[hostname][iface].append(myrules)
        else:
            rd[hostname][iface] = [myrules, ]

    return rd





"""
*raw
:PREROUTING ACCEPT
:OUTPUT ACCEPT
COMMIT

*mangle
:PREROUTING ACCEPT
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
COMMIT

*nat
:PREROUTING ACCEPT
:POSTROUTING ACCEPT
:OUTPUT ACCEPT
COMMIT

*filter
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
-A INPUT -s 4.4.4.4/32 -p tcp -m multiport --sports 0:65535 -m multiport --dports 2:4,5:10,10:33 -j ACCEPT
-A INPUT -s 4.4.4.4/32 -p tcp -m multiport --sports 0:65535 -m multiport --dports 2:4,5:10,10:33 -j ACCEPT
-A INPUT -s 4.4.4.4/32 -p tcp -m tcp --dport 2:4 -j ACCEPT
-A INPUT -s 3.3.3.3/32 -j ACCEPT
-A INPUT -s 3.3.3.0/30 -j ACCEPT
-A INPUT -s 3.3.3.3/32 -j ACCEPT
COMMIT
"""
