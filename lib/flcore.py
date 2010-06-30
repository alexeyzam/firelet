import csv


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
        a, n, l = addr.get(item), net.get(item), _resolveitems(hgs.get(item), addr, net, hgs)
        return filter(lambda i:i, (a, n, l))[0] # ugly

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
    proto_port['*'] = (('IPv4', None), ('IPv6', None))

    def res(n):
        if n in addr:
            return (addr[n], )
        elif n in net:
            return net[n]
        elif n in hg_flat:
            return hg_flat[src][0]
        else:
            raise Exception, "Host %s is not defined." % n

    for rule in rules:
        assert rule[0] in ('y', 'n')

    from itertools import product

    compiled = []
    for ena, name, src, src_serv, dst, dst_serv, action, log_val, desc in rules:
        srcs = res(src)
        dsts = res(dst)
        dst_servs = proto_port[dst_serv]

        src_servs = proto_port[src_serv]
        dst_servs = proto_port[dst_serv]

        for src, src_serv, dst, dst_serv in product(srcs, src_servs, dsts, dst_servs):
            if ena == 'n':
                continue
            if src_serv[0].endswith('6') ^ dst_serv[0].endswith('6'): # xor
                continue
            compiled.append((src, src_serv, dst, dst_serv, action, log_val))
    return compiled



