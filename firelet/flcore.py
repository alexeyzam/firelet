# Firelet - Distributed firewall management.
# Copyright (C) 2010 Federico Ceratto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

from copy import deepcopy
import csv
from collections import defaultdict
from hashlib import sha512
import logging
from netaddr import IPAddress, IPNetwork
from os import fsync, rename, unlink, getenv
from random import choice
from socket import inet_ntoa, inet_aton
from struct import pack, unpack
from time import time

from flssh import SSHConnector, MockSSHConnector
from flutils import Alert, Bunch, flag, extract_all

__version__ = '0.4.5a2'

from logging import getLogger
log = getLogger(__name__)

# Logging levels:
#
# critical - application failing - red mark on webapp logging pane
# error - anything that prevents ruleset deployment - red mark
# warning - non-blocking errors - orange mark
# info - default messages - displayed on webapp
# debug - usually not logged and not displayed on webapp


try:
    import json
except ImportError: # pragma: no cover
    import simplejson as json

try:
    from itertools import product
except ImportError: # pragma: no cover
    from flutils import product

protocols = ['AH', 'ESP', 'ICMP', 'IP', 'TCP', 'UDP']
# protocols unsupported by iptables: 'IGMP','','OSPF', 'EIGRP','IPIP','VRRP',
#  'IS-IS', 'SCTP', 'AH', 'ESP'

icmp_types = {
    '': 'all',
    0: 'echo-reply',
    3: 'destination-unreachable',
    4: 'source-quench',
    5: 'redirect',
    8: 'echo-request',
    9: 'router-advertisement',
    10: 'router-solicitation',
    11: 'ttl-exceeded',
    12: 'parameter-problem',
    13: 'timestamp-request',
    14: 'timestamp-reply',
    17: 'address-mask-request',
    18: 'address-mask-reply'}

def timeit(method):
    """Log function call and execution time
    Used for debugging
    """
    def timed(*args, **kw):
        t = time()
        log.setLevel(logging.WARN)
        result = method(*args, **kw)
        log.setLevel(logging.DEBUG)
        log.debug("%4.0fms %s %s %s" %
            (
                (time() - t) * 1000,
                method.__name__,
                repr(args)[:200],
                repr(kw)[:200],
            )
        )
        return result
    timed.__doc__ = method.__doc__
    return timed

#input validation

def validc(c):
    """Validate a character in rule name
    
    :arg c: character
    :return: True/False
    :rtype: bool
    """
    n = ord(c)
    if 31 < n < 127 and n not in (34, 39, 60, 62, 96):
        return True
    return False

def clean(s):
    """Remove dangerous characters.
    >>> clean(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_')
    ' !#$%&()*+,-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'
    
    :arg s: string
    :type s: str
    :rtype: str
    """
    return filter(validc, s)

# Network objects

class Rule(Bunch):

    def enable(self):
        self.enabled = '1'

    def disable(self):
        self.enabled = '0'


class Host(Bunch):
    def __init__(self, r):
        """Creates a Host object

        :arg r: Host attributes
        :type r: list
        """
        self.hostname=r[0]
        self.iface=r[1]
        self.ip_addr=r[2]
        self.masklen=r[3]
        self.local_fw=r[4]
        self.network_fw=r[5]
        self.mng=r[6]
        self.routed=r[7]

    def ipt(self):
        """String representation for iptables"""
        return "%s/32" % self.ip_addr

    def __contains__(self, other):
        """A host is "contained" in another host only when they have the same
        address
        """
        if isinstance(other, Host):
            return other.ip_addr == self.ip_addr
        
        raise Exception, "__contains__ called as: %s in Host" % type(other)

    def mynetwork(self):
        """Creates an unnamed network directly connected to the host

        :returns: A :class:`Network` instance
        """
        return Network(['', self.ip_addr, self.masklen])


class Network(Bunch):
    def __init__(self, r):
        """Creates a Host object

        Args:
            r (list): Network attributes
        """
        self.name = r[0]
        self.update({'ip_addr': r[1], 'masklen': r[2]})

    def ipt(self):
        """String representation for iptables"""
        return "%s/%s" % (self.ip_addr, self.masklen)

    def update(self, d):
        """Get the correct network address and update attributes"""
        addr = d['ip_addr']
        masklen = d['masklen']


        masklen = int(masklen)
        real_addr = net_addr(addr, masklen)
        self.ip_addr = real_addr
        self.masklen = masklen
        return real_addr, masklen, real_addr == addr

    def __contains__(self, other):
        """Check if a host or a network falls inside this network.
        Special case: the "Internet" network contains no hosts """

        if self.name == 'Internet':
            return False

        if isinstance(other, Host):
            return net_addr(other.ip_addr, self.masklen) == self.ip_addr

        elif isinstance(other, Network):
            addr_ok = net_addr(other.ip_addr, self.masklen) == self.ip_addr
            net_ok = other.masklen >= self.masklen
            return addr_ok and net_ok


class HostGroup(Bunch):
    """A Host Group contains hosts, networks, and other host groups"""

    def __init__(self, li):
        """Creates a HostGroup object

        :arg li: attributes
        :type li: list
        """
        self.name = li[0]
        if len(li) == 1:
            childs = []
        else:
            childs = li[1:]
        self.childs = childs

    def _flatten(self, i):
        """Flatten the host groups hierarchy
       
        :return: list of strings
        """
        if hasattr(i, 'childs'):  # "i" is a hostgroup _object_!
            childs = i.childs
            leaves = sum(map(self._flatten, childs), [])
            for x in leaves:
                assert isinstance(x, str)
            return leaves
        if i in self._hbn:  # if "i" is a host group, fetch its childs:
            childs = self._hbn[i]
            leaves = sum(map(self._flatten, childs), [])
            for x in leaves:
                assert isinstance(x, str)
            return leaves
        else: # it's a host or a network name (string)
            return [i]

    def flat(self, host_by_name, net_by_name, hg_by_name):
        """Flatten the host groups hierarchy

        :arg host_by_name: hostname -> host
        :type host_by_name: dict
        :arg net_by_name: netname -> net
        :type net_by_name: dict
        :arg hg_by_name: hgname -> hg
        :type hg_by_name: dict
        :returns: :class:`Host` or :class:`Network` instances
        """
        self._hbn = hg_by_name
        li = self._flatten(self)
        del(self._hbn)
        def res(o):
            assert isinstance(o, str), repr(o)
            if o in host_by_name:
                return host_by_name[o]
            elif o in net_by_name:
                return net_by_name[o]
            else:
                raise Exception,  "%s is not in %s or %s" % \
                    (o, repr(host_by_name), repr(net_by_name))

        return map(res, li)

#    def networks(self):
#        """Flatten the hostgroup and return its networks"""
#        return [n for n in self._flatten(self) if isinstance(n, Network)]
#
#    def hosts(self):
#        """Flatten the hostgroup and return its hosts"""
#        return filter(lambda i: type(i) == Host, self._flatten(self)) # better?
#        return [n for n in self._flatten(self) if isinstance(n, Host)]

class Service(Bunch):
    """A network service using one protocol and one, many or no ports"""
    def update(self, d):
        """Validate, then set/update the internal dictionary"""
        ports = d['ports']
        if d['protocol'] in ('TCP', 'UDP') and ports:
            for block in ports.split(','):
                try:
                    int_li = [int(i) for i in block.split(':')]
                except ValueError:
                    raise Alert, "Incorrect syntax in port definition '%s'" \
                        % block
                assert len(int_li) < 3, "Too many items in port range '%s'" \
                    % block
                for i in int_li:
                    assert i >= 0, "Negative port number '%s'" % i
                    assert i < 65536, "Port number too high '%s'" % i
                if len(int_li) == 2:
                    assert int_li[0] <= int_li[1], \
                        "Reversed port range '%s'" % block
        elif d['protocol'] == 'ICMP' and ports:
            try:
                icmp_type = int(ports)
            except ValueError:
                raise Alert,  "Invalid ICMP Type '%s'" % ports
            assert icmp_type in icmp_types, "Invalid ICMP Type '%s'" % icmp_type
        elif d['protocol'] in protocols:
            # Supported protocol that has no ports
            d['ports'] = ''
        else:
            raise Alert, "Unsupported protocol: '%s'" % d['protocol']
        super(Service, self).update(d)


class NetworkObjTable(object):
    """Contains a set of hosts or networks or hostgroups.
    They are stored as self._objdict where the key is the object name
    """
    def __init__(self):
        raise NotImplementedError

    def __str__(self):
        """Pretty-print as a table"""
        cols = zip(*self)
        # get the widest entry for each column
        cols_sizes = [(max(map(len, i))) for i in cols]

    def len(self):
        return len(self._objdict())

    def get(self, id=None, name=None):
        if name:
            return self._objdict[name]
        if id:
            return self._objdict.values()[id]



#files handling

class Table(list):
    """A list with pretty-print methods"""
    def __str__(self):
        cols = zip(*self)
        cols_sizes = [(max(map(len, i))) for i in cols] # get the widest entry for each column

    def len(self):
        return len(self)

class SmartTable(object):
    """A list of Bunch instances. Each subclass is responsible to load and save files."""
    def __init__(self, d):
        self._dir = d

    def __repr__(self):
        return repr(self._list)

    def __iter__(self):
        return self._list.__iter__()

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list.__getitem__(i)

    def pop(self, i):
        x = self._list[i]
        del self._list[i]
        return x

    def update(self, d, rid=None, token=None):
        """Update internal dictionary based on d

        :param d: Fields
        :type d: dict.
        :param rid: row ID (optional)
        :type rid: int.
        :param token: token (optional)
        :type token: str.
        """
        assert rid != None, "Malformed input row ID is missing."
        try:
            item = self.__getitem__(int(rid))
        except IndexError:
            raise Alert, "Item to be updated not found: one or more "\
                "items has been modified in the meantime."
        if token:
            assert token == item._token(), "Unable to update: one " \
                "or more items has been modified in the meantime."
        item.update(d)
        self.save()


class Rules(SmartTable):
    """A list of Bunch instances"""
    def __init__(self, d):
        """Creates a Rules object

        Args:
            d (string): data directory
        """
        self._dir = d
        self.reload()

    def reload(self):
        """Load ruleset from file
        """
        li = readcsv('rules', self._dir)
        self._list = [Rule(enabled=r[0], name=r[1], src=r[2], src_serv=r[3],
            dst=r[4], dst_serv=r[5], action=r[6], log_level=r[7], desc=r[8])
            for r in li]

    def save(self):
        """Save the ruleset"""
        li = [[x.enabled, x.name, x.src, x.src_serv, x.dst, x.dst_serv,
                    x.action, x.log_level, x.desc] for x in self._list]
        savecsv('rules', li, self._dir)

    def moveup(self, rid):
        """Move a rule up"""
        try:
            rules = self._list
            rules[rid], rules[rid - 1] = rules[rid - 1], rules[rid]
            self._list = rules
            self.save()
        except Exception, e:
            log.debug("Error in rules.moveup: %s" % e)
            raise Alert
            #            say("Cannot move rule %d up." % rid)

    def movedown(self, rid):
        """Move a rule down"""
        try:
            rules = self._list
            rules[rid], rules[rid + 1] = rules[rid + 1], rules[rid]
            self._list = rules[:]
            self.save()
        except Exception, e:
            #            say("Cannot move rule %d down." % rid)
            raise Alert

    def disable(self, rid):
        """Disable a rule

        :param rid: Rule ID
        :type rid: int.
        """
        self._list[rid].disable()
        self.save()

    def enable(self, rid):
        """Enable a rule

        :param rid: Rule ID
        :type rid: int.
        """
        self._list[rid].enable()
        self.save()

    def enabled(self, rid):
        """Check if a rule is enabled

        :param rid: Rule ID
        :type rid: int.
        :returns: bool
        """
        return self._list[rid].enabled == '1'

    def update(self, d, rid=None, token=None):
        """Update internal dictionary based on d"""
        assert rid != None, "Malformed input row ID is missing."
        try:
            rule = self.__getitem__(int(rid))
        except IndexError:
            raise Alert, "Rule to be updated not found: one or more items has been modified in the meantime."
        if token:
            self.validate_token(token)
        rule.update(d)
        self.save()

    def add(self, d, rid=0): #TODO: unit testing
        """Add a new item based on a dict of fields"""
        assert isinstance(rid, int)
        assert isinstance(d, dict)
        if d == {}:
            d = dict(enabled='0', name='new', src='*', src_serv='*',
                dst='*', dst_serv='*', action='ACCEPT', log_level=0, desc='')
        if d['name'] in (rule.name for rule in self._list):
            raise Alert, "Another rule with the same name '%s' exists." % d['name']
        self._list.insert(rid, Rule(**d))
        self.save()


class Hosts(SmartTable):
    """A list of Bunch instances"""
    def __init__(self, d):
        self._dir = d
        self.reload()

    def reload(self):
        """Load hosts from file
        """
        li = readcsv('hosts', self._dir)
        self._list = []
        for r in li:
            q = r[0:7] + [r[7:]]
            b = Host(q)
            self._list.append(b)

    def save(self):
        """Flatten the routed network list and save"""
        li = [[x.hostname, x.iface, x.ip_addr, x.masklen, x.local_fw, x.network_fw, x.mng] + x.routed for x in self._list]
        savecsv('hosts', li, self._dir)

    def add(self, f): #TODO: unit testing
        """Add a new item based on a dict of fields"""
        names = ["%s:%s" % (x.hostname, x.iface) for x in self._list]
        me = "%s:%s" % (f['hostname'], f['iface'])
        assert me not in names, "Host '%s' already defined" % me
        li = [f[x] for x in ('hostname', 'iface', 'ip_addr', 'masklen', 'local_fw', 'network_fw', 'mng', 'routed')]
        self._list.append(Host(li))
        self.save()

#        self.hostname=r[0]
#        self.iface=r[1]
#        self.ip_addr=r[2]
#        self.masklen=r[3]
#        self.local_fw=r[4]
#        self.network_fw=r[5]
#        self.mng=r[6]
#        self.routed=r[7]


class HostGroups(SmartTable):
    """A list of Bunch instances"""
    def __init__(self, d):
        """
        .. automethod:: _simpleflatten
        """
        self._dir = d
        self.reload()

    def reload(self):
        """Load hostgroups from file
        """
        li = readcsv('hostgroups', self._dir)
        self._list = [HostGroup(r) for r in li]

    def save(self):
        li = [[x.name] + x.childs for x in self._list]
        savecsv('hostgroups', li, self._dir)

    def add(self, f): #TODO: unit testing
        """Add a new hostgroup based and saves to disk.

        :param f: New hg's fields
        :type f: dict.
        """
        assert 'name' in f, '"name" field missing'
        assert 'childs' in f,  '"childs" field missing'
        names = [x.name for x in self._list]
        assert f['name'] not in names, "Hostgroup '%s' already defined" % f['name']
        li = [f['name']] + f['childs']
        self._list.append(HostGroup(li))
        self.save()

    def _simpleflatten(self, node):
        """Flatten a tree of hostgroups starting from a node

        :param node: node to start from
        :type node:  str.

        """
        for root_hg in self._list:
            if node == root_hg.name:
                m = map(self._simpleflatten, root_hg.childs)
                return sum(m, [])
        return [node]


    def update(self, d, rid=None, token=None):
        """Perform loop checking before running the original "update" method.
        A loop happens when a HostGroup contains itself in one of its
        siblings (once flattened)

        :param d: Fields
        :type d: dict.
        :param rid: row ID (optional)
        :type rid: int.
        :param token: token (optional)
        :type token: str.

        """
        assert rid != None, "Malformed input row ID is missing."
        try:
            item = self.__getitem__(int(rid))
        except IndexError:
            raise Alert, "Item to be updated not found: one or more " \
                "items has been modified in the meantime."
        if token:
            assert token == item._token(), "Unable to update: one " \
                "or more items has been modified in the meantime."
        for child in d['childs']:
            flat = self._simpleflatten(child)
            assert item.name not in flat, "Loop "

        item.update(d)
        self.save()

#        super(HostGroups, self).update(d, rid, token)


class Networks(SmartTable):
    """A list of Bunch instances"""
    def __init__(self, d):
        self._dir = d
        self.reload()

    def reload(self):
        """Load networks from file
        """
        li = readcsv('networks', self._dir)
        self._list = [Network(r) for r in li]

    def save(self):
        li = [[x.name, x.ip_addr, x.masklen] for x in self._list]
        savecsv('networks', li, self._dir)

    def add(self, f): #TODO: unit testing
        """Add a new item based on a dict of fields"""
        names = [x.name for x in self._list]
        assert f['name'] not in names, "Network '%s' already defined" % f['name']
        li = [f[x] for x in ('name', 'ip_addr', 'masklen')]
        self._list.append(Network(li))
        self.save()


class Services(SmartTable):
    """A list of Bunch instances"""
    def __init__(self, d):
        self._dir = d
        self.reload()

    def reload(self):
        """Load service from file
        """
        li = readcsv('services', self._dir)
        self._list = [ Service(name=r[0], protocol=r[1], ports=r[2]) for r in li ]

    def save(self):
        li = [[x.name, x.protocol, x.ports] for x in self._list]
        savecsv('services', li, self._dir)

    def add(self, f): #TODO: unit testing
        """Add a new item based on a dict of fields"""
        d = extract_all(f, ('name', 'protocol', 'ports'))
        names = [x.name for x in self._list]
        assert d['name'] not in names, "Service '%s' already defined" % d['name']
        self._list.append(Service(**d))
        self.save()

# CSV files

def readcsv(n, d):
    """Read CSV file, ignore comments
    :param n: filename (path and .csv)
    :type n: str
    :param d: directory name (without slashes)
    :type d: str
    :returns: list
    """
    with open("%s/%s.csv" % (d, n)) as f:
        lines = map(str.rstrip, f)
    if lines[0] != '# Format 0.1 - Do not edit this line':
        raise Exception, "Data format not supported in %s/%s.csv" \
            % (d, fname)
    li = [x for x in lines if not x.startswith('#') and x]
    return csv.reader(li, delimiter=' ')


def loadcsv_unused(fname, d):
    """Load a CSV file

    Args:
        n (string): filename, without .csv
        d (string): directory

    Returns:
        a Table instance
    """
    f = open("%s/%s.csv" % (d, fname))
    lines = map(str.rstrip, f)
    f.close()
    if lines[0] != '# Format 0.1 - Do not edit this line':
        raise Exception, "Data format not supported in %s/%s.csv" \
            % (d, fname)
    li = [x for x in lines if not x.startswith('#') and x != '\n']
    r = Table(csv.reader(li, delimiter=' '))
    return r

def savecsv(n, stuff, d):
    """Save CSV file safely, preserving comments"""
    fullname = "%s/%s.csv" % (d, n)
    log.debug('Saving "%s" in "%s"...' % (n, d))
    try:
        f = open(fullname)
        comments = [x for x in f if x.startswith('#')]
        f.close()
    except IOError:
        log.debug("%s not existing" % fullname)
        comments = []
    f = open(fullname +".tmp", 'wb')
    f.writelines(comments)
    writer = csv.writer(f,  delimiter=' ', lineterminator='\n')
    writer.writerows(stuff)
    f.flush()
    fsync(f.fileno())
    f.close()
    rename(fullname + ".tmp", fullname)

def loadjson(n, d):
    try:
        f = open("%s/%s.json" % (d, n))
        s = f.read()
        f.close()
    except Exception, e:
        raise Alert, "Unable read json file: %s" % e
    try:
        return json.loads(s)
    except Exception, e:
        raise Alert, "Unable to load users from '%s/%s.json': %s" % (d, n, e)



def savejson(n, obj, d):
    s = json.dumps(obj)
    f = open("%s/%s.json" % (d, n), 'wb')
    f.write(s)
    f.close()


# IP address parsing

def net_addr(a, n):
    q = IPNetwork('%s/%d' % (a, n)).network
    return str(q)

    addr = map(int, a.split('.'))
    x =unpack('!L', inet_aton(a))[0] & 2L**(n + 1) - 1
    return inet_ntoa(pack('L', x))



class FireSet(object):
    """A container for the network objects.
    Upon instancing the objects are loaded.
    """
    def __init__(self):
        """Initialize FireSet"""
        self.SSHConnector = SSHConnector
        self._table_names = ('rules', 'hosts', 'hostgroups', 'services', 'networks')

    # FireSet management methods
    # They are redefined in each FireSet subclass

    def save_needed(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def reload(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def rollback(self, n):
        raise NotImplementedError

    def version_list(self):
        raise NotImplementedError

    # editing methods

    def fetch(self, table, rid):
        """Get item from table
        """
        assert table in self._table_names, "Incorrect table name."
        try:
            return self.__dict__[table][rid]
        except Exception, e:
            Alert,  "Unable to fetch item %d in table %s: %s" % (rid, table, e)


    def delete(self, table, rid):
        """Delete item from table
        """
        assert table in self._table_names, "Incorrect table name."
        try:
            self.__dict__[table].pop(rid)
        except Exception, e:
            Alert,  "Unable to delete item %d in table %s: %s" % (rid, table, e)


    def list_sibling_names(self):
        """Return a list of all the possible siblings for a hostgroup
        being created or edited.
        """
        items = set()
        for hg in self.hostgroups:
            items.add(hg.name)
            for c in hg.childs:
                items.add(c)
        for h in self.hosts:
            items.add("%s:%s" % (h.hostname, h.iface))
        return sorted(items)



    # deployment-related methods #

    # 1) The hostgroups are flattened, then the firewall rules are compiled into a big list of iptables commands.
    # 2) Firelet connects to the firewalls and fetch the iptables status and the existing interfaces (name, ip_addr, netmask)
    # 3) Based on this, the list is split in many sets - one for each firewall.

    #TODO: save the new configuration for each host and provide versioning.

    # Before deployment, compare the old (versioned), current (on the host) and new configuration for each firewall.
    # If current != versioned warn the user: someone made local changes.
    # Provide a diff of current VS new to the user before deploying.

    def _flattenhg(self, items, addr, net, hgs):
        """Flatten host groups tree, used in compiling)"""
        def flatten1(item):
            li = addr.get(item), net.get(item), self._flattenhg(hgs.get(item), addr, net, hgs)
            return filter(None, li)[0]
        if not items: return None
        return map(flatten1, items)

    def _get_firewalls(self):
        """Returns only the hosts that can be managed by Firelet
        """
        # List host names that have *at least one* management interface
        firewall_names = set(h.hostname for h in self.hosts if int(h.mng))
        return [h for h in self.hosts if h.hostname in firewall_names]

    def _get_confs(self, keep_sessions=False, username='firelet',
            ssh_key_autoadd=True):
        """Connect to the firewalls and fetch the existing configuration
        Return the SSHConnector instance if keep_sessions is True
        """
        self._remote_confs = None
        d = defaultdict(list) # {hostname: [management ip address list ], ... }
        for h in self._get_firewalls():
            d[h.hostname].append(h.ip_addr)
        sx = self.SSHConnector(
            targets=d,
            username=username,
            ssh_key_autoadd=ssh_key_autoadd
        )
        log.debug("Running SSH.")
        self._remote_confs = sx.get_confs()
        if keep_sessions:
            return sx
        sx._disconnect()
        del(sx)

    def _check_ifaces(self, stop_on_extra_interfaces=False):
        """Ensure that the interfaces configured on the hosts match
            the contents of the host table"""
        log.debug("Checking interfaces...")
        confs = self._remote_confs
        assert isinstance(confs, dict), "_remote_confs not populated " \
            "before calling _check_ifaces"
        for q in confs.itervalues():
            assert isinstance(q, Bunch), "Incorrect type in %s" % repr(confs)
            assert len(q) == 2, "%s must have 2 items" % repr(q)

        # hostname -> interfaces_list
        ifaces = defaultdict(set)

        for h in self._get_firewalls():
            if not h.hostname in confs:
                raise Alert, "Host %s not available." % h.hostname
            ifaces[h.hostname].add(h.iface)
            ip_a_s = confs[h.hostname].ip_a_s
            if not h.iface in ip_a_s:
                raise Alert, "Interface %s missing on host %s" \
                    % (h.iface, h.hostname)
            ip_addr_v4, ip_addr_v6 = ip_a_s[h.iface]
            assert '/' in ip_addr_v4, "The IPv4 address extracted from " \
                "running 'ip addr show' on %s has no '/' in it" % h.hostname
            if not ip_addr_v4 or len(ip_addr_v4.split('/')) != 2:
                raise Alert, "Unable to parse IPv4 addr from '%s' on '%s'" % \
                    (ip_a_s, h.hostname)
            if h.ip_addr not in (ip_addr_v6,  ip_addr_v4.split('/')[0] ):
                raise Alert,"Wrong address on %s on interface %s: \
            %s and %s (should be %s)" % (h.hostname, iface, ip_addr_v4,
                        ip_addr_v6, h.ip_addr)

        # Check if extra interfaces (unknown to Firelet) are present
        # on the hosts
        fw_having_extra_if = {}
        if stop_on_extra_interfaces:
            for hostname, flet_ifaces in ifaces.iteritems():
                fw_ifaces = set(confs[h.hostname].ip_a_s)
                extra = fw_ifaces - flet_ifaces
                if extra:
                    fw_having_extra_if[hostname] = extra

            if fw_having_extra_if:
                li = ["%s: %s" % (hn, ','.join(i))
                        for hn, i in fw_having_extra_if.iteritems()]
                s = "One or more firewalls have extra interfaces: %s" \
                            % ' '.join(li)
                log.warn(s)
                raise Alert, s

        log.debug("self._check_ifaces successful")

    def _oo_forwarded(self, src, dst, me, routed_nets, other_ifaces):
        """Tell if a src network or ipaddr has to be routed through the local host.
        All params are Host or Network instances"""
        if not src: return True
        if me.ip_addr == src.ip_addr: # this is input or output traffic, not to be forwarded
            return False
        if src in me.mynetwork(): # src is in a directly conn. network
            if dst in me.mynetwork(): # but dst is in the same network
                return False
            return True
        for rnet in routed_nets:
            if src in rnet and dst not in rnet:
                return True
        return False

    def compile_rules(self):
        """Compile iptables rules to be deployed in a dict:
        { 'firewall_name': {'INPUT',[rules...]},{'OUTPUT',[rules...]},{'FORWARD',[rules...]}, ... }

        During the compilation many checks are performed."""
        assert not self.save_needed(), "Configuration must be saved before deployment."

        for rule in self.rules:
            assert rule.enabled in ('1', '0'), 'First field must be "1" or "0" in %s' % repr(rule)
        log.debug('Building dictionaries...')
        # build dictionaries to perform resolution
        addr = dict(((h.hostname + ":" + h.iface), h.ip_addr) for h in self.hosts) # host to ip_addr
        net = dict((n.name, (n.ip_addr, n.masklen)) for n in self.networks) # network name to addressing

        for h in self.hosts:
            for routed_net in h.routed:
                assert routed_net in net, "Unknown network '%s' routed by %s" \
                    % (routed_net, h.hostname)

        proto_port = dict((sr.name, (sr.protocol, sr.ports)) for sr in self.services) # protocol
        proto_port['*'] = (None, '') # special case for "any"      # port format: "2:4,5:10,10:33,40,50"

        host_by_name_col_iface = dict((h.hostname + ":" + h.iface, h) for h in self.hosts)
        host_by_name = dict((h.hostname, h) for h in self.hosts)
        net_by_name = dict((n.name, n) for n in self.networks)

        hg_by_name = dict((hg.name, hg.childs) for hg in self.hostgroups)  # hg name  to its child names

        flat_hg = dict((hg.name, hg.flat(host_by_name_col_iface, net_by_name, hg_by_name)) for hg in self.hostgroups)

        def res(n):
            """Resolve flattened hostgroups, hosts and networks by name
                and provides None for '*' """
            if n in host_by_name_col_iface:
                return [host_by_name_col_iface[n]]
            elif n in net_by_name:
                return [net_by_name[n]]
            elif n in flat_hg:
                return flat_hg[n]
            elif n == '*':
                return [None]
            else:
                raise Alert, "Item %s is not defined." % n + repr(host_by_name_col_iface)

        log.debug('Compiling ruleset...')
        # for each rule, for each (src,dst) tuple, compiles a list
        #[ (protocol, src, sports, dst, dports, log_val, rule_name, action), ... ]
        compiled = []
        for rule in self.rules:  # for each rule
            if rule.enabled == '0':
                continue
            assert rule.action in ('ACCEPT', 'DROP'), """The Action field must
                be "ACCEPT" or "DROP" in rule "%s"" """ % rule.name
            srcs = res(rule.src)
            dsts = res(rule.dst)    # list of Host and Network instances

            sproto, sports = proto_port[rule.src_serv]
            dproto, dports = proto_port[rule.dst_serv]
            assert sproto in protocols + [None], """Unknown source
                protocol: %s""" % sproto
            assert dproto in protocols + [None], """Unknown dest
                protocol: %s""" % dproto


            if sproto:
                if dproto and sproto != dproto:
                    raise Alert, """Source and destination protocol
                        must be the same in rule "%s".""" % rule.name
                proto = sproto.lower()
            elif dproto:
                proto = dproto.lower()
            else:
                proto = ''

            if ',' in sports or ',' in dports:
                multiport = True
            else:
                multiport = False

            if multiport:
                modules = ' -m multiport'
                if sports:
                    sports = " --sports %s" % sports
                if dports:
                    dports = " --dports %s" % dports
            elif proto in ('udp', 'tcp', 'icmp'):
                modules = ' -m %s ' % proto
                if sports:
                    sports = " --sport %s" % sports
                if dports:
                    dports = " --dport %s" % dports
            else:
                assert not sports
                assert not dports
                modules = ''

            if proto:
                proto = " -p %s " % proto
            #FIXME: handle other protocols


            for x in rule.name:
                assert validc(x), "Invalid character in '%s': x" % (repr(rule.name), repr(x))

            try:
                log_val = int(rule.log_level)
            except ValueError:
                raise Alert, """The logging field in rule '%s' is '%s'
                    and must be an integer.""" % (rule.name, rule.log_level)

            for src, dst in product(srcs, dsts):
                assert isinstance(src, Host) or isinstance(src, Network) or src == None, repr(src)
                assert isinstance(dst, Host) or isinstance(dst, Network) or dst == None, repr(dst)
                compiled.append((proto, modules, src, sports, dst, dports, log_val,  rule.name, rule.action))

        log.debug('Splicing ruleset...')

        # Creating iptables-compatible rules, using the following format:
        #
        # -A <chain> -s <ipa/mask> -d <ipa/mask> -i <iface> -p <proto>
        #        -m <module> --sport <nn> --dport <nn> -j ACCEPT
        #
        # r[hostname] = [rule, rule, ... ]
        rd = {}
        for proto, modules, src, sports, dst, dports, log_val, name, action in compiled: # for each compiled rule
            _src = "-s %s" % src.ipt() if src else ''
            if '0.0.0.0' in _src:
                _src = ''
            _dst = " -d %s" % dst.ipt() if dst else ''
            for h in self.hosts:   # for each host (interface)
                # Insert first rules
                if h.hostname not in rd:
                    rd[h.hostname] = {}
                    rd[h.hostname]['INPUT'] = ["-m state --state " \
                        "RELATED,ESTABLISHED -j ACCEPT", "-i lo -j ACCEPT"]
                    rd[h.hostname]['OUTPUT'] = ["-m state --state " \
                        "RELATED,ESTABLISHED -j ACCEPT", "-o lo -j ACCEPT"]
                    if h.network_fw == '1':
                        rd[h.hostname]['FORWARD'] = ["-m state --state " \
                            "RELATED,ESTABLISHED -j ACCEPT"]
                    else:
                        rd[h.hostname]['FORWARD'] = ["-j DROP"]
                if src and dst and src.ipt() == dst.ipt():
                    continue

                # Build INPUT rules: where the host is in the destination
                if dst and h in dst or not dst:
                    if log_val:
                        rd[h.hostname]['INPUT'].append(
                            '%s%s -i %s %s%s%s%s -j LOG --log-prefix "i_%s" --log-level %d' %
                                (_src, _dst, h.iface, proto, modules, sports,
                                dports, name, log_val))
                    rd[h.hostname]['INPUT'].append(
                            "%s%s -i %s %s%s%s%s -j %s"
                            % (_src, _dst, h.iface, proto, modules, sports,
                              dports, action))

                # Build OUTPUT rules: where the host is in the source
                if src and h in src or not src:
                    if log_val:
                        rd[h.hostname]['OUTPUT'].append(
                            '%s%s -o %s %s%s%s%s -j LOG --log-prefix "o_%s" --log-level %d' %
                            (_src, _dst, h.iface, proto, modules, sports,
                            dports, name, log_val))

                    rd[h.hostname]['OUTPUT'].append("%s%s -o %s %s%s%s%s -j %s"
                            % (_src, _dst, h.iface, proto, modules, sports,
                               dports, action))

                # Build FORWARD rules: where the source and destination are
                #  both in directly connected or routed networks
                if h.network_fw in ('0', 0, False):
                    continue
                # resolved routed nets [[addr, masklen], [addr, masklen], ... ]
                resolved_routed = [net[r] for r in h.routed]
                nets = [IPNetwork("%s/%s" %(y, w)) for y, w in resolved_routed]

                other_ifaces = [k for k in self.hosts
                    if k.hostname == h.hostname and k.iface != h.iface]

                forw = self._oo_forwarded(src, dst, h, resolved_routed,
                                          other_ifaces)

                if forw:
                    rd[h.hostname]['FORWARD'].append(
                        '%s%s%s%s%s%s -j LOG  --log-prefix "f_%s" --log-level %d' %
                        (_src, _dst, proto,  modules, sports, dports, name,
                         log_val))
                    rd[h.hostname]['FORWARD'].append("%s%s%s%s%s%s -j %s"
                        %  (_src, _dst, proto, modules, sports, dports, action))

            # "for every host"
        # "for every rule"

        #FIXME: this should not be required
        for hostname, rules in rd.iteritems():
            if hostname == 'BorderFW' or hostname == 'InternalFW':
                rules['INPUT'] = ['-j ACCEPT'] + rules['INPUT']
                rules['FORWARD'] = ['-j ACCEPT'] + rules['FORWARD']

#        log.debug("rd first 900 bytes: %s" % repr(rd)[:900])
        return rd       # complile_rules()

    def _remove_dup_spaces(self, s):
        return ' '.join(s.split())

    def _build_ipt_restore_blocks(self, (hostname, b)):
        """Build a list of strings for each chain compatible with iptables-restore"""
        li = []
        for chain in ('INPUT', 'FORWARD', 'OUTPUT'):
            for rule in b[chain]:
                li.append("-A %s %s"% (chain, rule))
        return li

    def _build_ipt_restore(self, (hostname, b)):
        """Build a list of strings compatible with iptables-restore"""
        li = ['# Created by Firelet for host %s' % hostname, '*filter']
        li.extend(self._build_ipt_restore_blocks((hostname, b)))
        li.append('COMMIT')
        return (hostname, li)

    #TODO: improve UT
    @timeit
    def _extract_ipt_filter_rules(self, remote_confs):
        """Extract the relevant iptables rules from the output of iptables-save,
        delimited by '*filter' and 'COMMIT' """
        #remote_confs = dict(
        #        hostname=Bunch(
        #            iptables=dict(
        #               'filter' = [rule, rule, ...]
        #               'nat' = []
        #            ),
        #            ip_a_s=ip_a_s_p
        #        )
        #    )
        return dict(
            (hn, remote_confs[hn]['iptables']['filter'])
            for hn in remote_confs
        )


    @timeit
    def _diff(self, remote_confs, new_confs):
        """Generate a dict containing the changes between the existing and
        the compiled iptables ruleset on every host"""
        # TODO: this is a hack - rewrite it using two-step comparison:
        # existing VS old (stored locally), existing VS new
        # d = {hostname: ( [ added item, ... ], [ removed item, ... ] ), ... }
        d = {}
        for hostname, ex_iptables in remote_confs.iteritems():
            # looping through existing iptables ruleset and ip_a_s
            if hostname in new_confs:
                new = new_confs[hostname]
                new = map(self._remove_dup_spaces, new)
                ex_iptables = map(self._remove_dup_spaces, ex_iptables)
                added_li = [x for x in new if x not in ex_iptables]
                removed_li = [x for x in ex_iptables if x not in new]

                log.debug("Rules for %-15s old: %d new: %d added: %d removed: %d"
                    % (hostname, len(ex_iptables), len(new), len(added_li), len(removed_li)))
                #log.debug(repr(ex_iptables[:5]))
                if added_li or removed_li:
                    d[hostname] = (added_li, removed_li)
            else:
                #TODO: review this, manage *new* hosts as well
                log.debug('%s removed?' % hostname)
        return d

    #TODO: UT
    @timeit
    def _diff_compiled_and_remote_rules(self, comp_rules):
        """Compare remote and compiled rules and return a diff
        self._remote_confs needs to be populated in advance
        """
        assert self._remote_confs, "self._remote_confs not set \
        before calling _diff_compiled_and_remote_rules"

        new_rules = {}
        for hn, b in comp_rules.iteritems():
            li = self._build_ipt_restore_blocks((hn, b))
            new_rules[hn] = li
        existing_rules = self._extract_ipt_filter_rules(self._remote_confs)
        return self._diff(existing_rules, new_rules)

    def check(self, stop_on_extra_interfaces=False, logger=log):
        """Check the configuration on the firewalls.
        """
        if self.save_needed():
            raise Alert, "Configuration must be saved before check."
        comp_rules = self.compile_rules()
        logger.info('Rules compiled. Getting configurations.')
        self._get_confs()
        logger.debug('Remote confs repr: %s' % repr(self._remote_confs)[:300])
        logger.debug('Checking interfaces.')
        self._check_ifaces(stop_on_extra_interfaces=stop_on_extra_interfaces)
        log.debug('Interface check complete.')
        log.debug('Comparing...')
        diff = self._diff_compiled_and_remote_rules(comp_rules)
        log.debug('Diff completed.')
        return diff

    def get_compiled_rules(self):
        """Return the compiled rules"""
        return self.compile_rules()

    def deploy(self, ignore_unreachables=False, replace_ruleset=False,
        stop_on_extra_interfaces=False):
        """Check and then deploy the configuration to the firewalls.
        Some ignore flags can be set to force the deployment even in case of errors.
        """
        if self.save_needed():
            raise Alert, "Configuration must be saved before deployment."
        comp_rules = self.compile_rules()
        log.debug('Rules compiled. Fetching configurations.')
        sx = self._get_confs(keep_sessions=True)
        log.debug('Checking interfaces.')
        self._check_ifaces(stop_on_extra_interfaces=stop_on_extra_interfaces)
        log.debug('Interface check complete.')
        self._remote_confs = None
        m = map(self._build_ipt_restore, comp_rules.iteritems())
        c = dict(m)
        log.debug('Delivering configurations...')
        sx.deliver_confs(c)

        log.debug('Saving existing configurations...')
        sx.save_existing_confs()

        log.debug('Setting up automatic rollback...')
        out = sx.setup_auto_rollbacks()
        if out:
            raise Alert('Automated rollback enabling failed on %s' % out)

        log.debug('Applying configurations...')
        sx.apply_remote_confs()

        sx._disconnect()
        sx.log_ping()

        log.debug('Cancelling automatic rollback...')
        sx.cancel_auto_rollbacks()

        log.debug('Fetching live configurations...')
        self._get_confs(keep_sessions=False)
        diff = self._diff_compiled_and_remote_rules(comp_rules)

        if diff:
            log.error('Deployment failed!')
#            raise Alert('Deployment failed!')
            #TODO: more context
        else:
            log.debug('Deployment completed.')

    def get_rsa_pub(self):
        """Read RSA public key from ~/.ssh/id_rsa.pub

        :returns: Key (str)
        """

        id_rsa_fn = "%s/.ssh/id_rsa.pub" % getenv("HOME")
        with open(id_rsa_fn) as f:
            id_rsa = f.read()

        assert id_rsa.startswith('ssh-rsa '), "The local RSA key\
in %s does not look valid" % id_rsa_fn

    def generate_otp(self):
        """Generate one-time password used to configure new firewalls
        """
        chars = '0123456789ABCDEFGHIJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        password = [choice(chars) for x in xrange(10)]
        password = ''.join(password)
        return password

    def assimilate(self, target, rsa_pub_key, username, password):
        """Configure a new firewall node interactively.
        Test SSH connectivity, sets up certificates

        :param target: firewall IP address or hostname
        :type target: str.
        :param rsa_pub_key: RSA public key
        :type rsa_pub_key: str.
        :param password: SSH password
        :type password: str.
        """

        cx = SSHConnector(targets={target:[target]}, username=username,
            password=password, ssh_key_autoadd=True)
        print "Setting up SSH connection..."
        out = cx._execute(target, \
            "umask 077;" \
            "mkdir -p ~/.ssh ;" \
            "cat >> ~/.ssh/authorized_keys << EOF || exit 1" \
            "%s" \
            "EOF" \
        )

        log.info("out %s" % out)
        #TODO: test assimilation process


class GitFireSet(FireSet):
    """FireSet implementing Git to manage the configuration repository"""
    def __init__(self, repodir):
        self.rules = Rules(repodir)
        self.hosts = Hosts(repodir)
        self.hostgroups = HostGroups(repodir)
        self.services = Services(repodir)
        self.networks = Networks(repodir)
        self._git_repodir = repodir
        if 'fatal: Not a git repository' in self._git('status')[1]:
            log.debug('Creating Git repo...')
            self._git('init .')
            self._git('add *.csv *.json')
            self._git('commit -m "Configuration database created."')
        super(GitFireSet, self).__init__()

    def version_list(self):
        """Parse git log --date=iso

        Returns:
            a list of lists: [ [author, date, [msg lines], commit_id ], ... ]
        """
        o, e = self._git('log --date=iso')
        if e:
            Alert, "Error while running 'git log --date=iso': %s" % e
        li = []
        msg = []
        author = None
        for r in o.split('\n'):
            if r.startswith('commit '):
                if author:
                    li.append([author, date, msg, commit])
                commit = r[7:]
                msg = []
            elif r.startswith('Author: '):
                author = r[8:]
            elif r.startswith('Date: '):
                date = r[8:]
            elif r:
                msg.append(r.strip())
        return li

    def version_diff(self, commit_id):
        """Parse git diff <commit_id>
        Returns a list of (line, tag), the tag being 'title', 'add',
        'del,' or empty
        """
        tags = {'+': 'add', '-': 'del',  ' ': '',  '':''}
        o, e = self._git('diff %s' % commit_id)
        if e:
            Alert, "Error while runnig 'git diff %s': %s" % \
                (commit_id, e)
        li = []
        for x in o.split('\n'):
            x = x.rstrip()
            # get the title from the filename
            # "+++ b/hostgroups.csv"
            if x.startswith('+++'):
                li.append((x[6:-4], 'title'))
            # ignore some non-diff lines
            elif x.startswith('---') or \
                x.startswith('@@') or \
                x.startswith('diff --git a/') or \
                x.startswith('index '):
                pass
            # add diff lines with the appropriate tag
            else:
                tag = tags[x[:1]]
                li.append((x[1:], tag))
        return li

    def _git(self, cmd):
        from subprocess import Popen, PIPE
        #log.debug('Executing "/usr/bin/git %s" in "%s"' % \
        #    (cmd, self._git_repodir))
        p = Popen('/usr/bin/git %s' % cmd, shell=True, cwd=self._git_repodir,
            stdout=PIPE, stderr=PIPE)
        p.wait()
        return p.communicate()

    def save(self, msg):
        """Commit changes if needed."""
        if not msg:
            msg = '(no message)'
        self._git("add *")
        self._git("commit -m '%s'" % msg)

    def reload(self):
        """Reload all the tables from disk
        """
        for table_name in self._table_names:
            self.__dict__[table_name].reload()

    def reset(self):
        """Reset Git to last commit."""
        o, e = self._git('reset --hard')
        assert 'HEAD is now at' in o, \
            "Git reset --hard output: '%s' error: '%s'" % (o, e)

    def rollback(self, n=None, commit_id=None):
        """Rollback to n commits ago or given a specific commit_id
        """
        assert n is not None or commit_id, "n or commit_id must be specified"
        self.reset()
        if n:
            try:
                n = int(n)
            except ValueError:
                raise Alert, "rollback requires an integer"
            o, e = self._git("reset --hard HEAD~%d" % n)
            assert 'HEAD is now at' in o, \
                "Git reset --hard HEAD~%d output: '%s' error: '%s'" % (n, o, e)
        else:
            o, e = self._git("reset --hard %s" % commit_id)
            assert 'HEAD is now at' in o, "Git reset --hard " \
                "%s output: '%s' error: '%s'" % (commit_id, o, e)

    def save_needed(self):
        """True if commit is required: files has been changed"""
        o, e = self._git('status -uno')
        #log.debug("Git status: '%s'" % (o))
        if 'nothing to commit ' in o:
            return False
        elif '# On branch master' in o:
            return True
        else:
            raise Alert, "Git status output: '%s' error: '%s'" % (o, e)

    # GitFireSet editing

    def _write(self, table):
        """Write the changes to disk without committing on Git"""
        if table == 'hosts':
            self.hosts.save()
        elif table == 'networks':
            self.networks.save()
        elif table == 'services':
            self.services.save()
        elif table == 'rules':
            self.rules.save()
        elif table == 'hostgroups':
            self.hostgroups.save()
        else:
            raise Exception, "Table %s not existing" % table

    def delete(self, table, rid):
        assert table in self._table_names, \
            "Wrong table name for deletion: %s" % table
        try:
            self.__dict__[table].pop(rid)
        except IndexError, e:
            raise Alert, "The element n. %d is not present in table '%s'" % (rid, table)
        self._write(table)


class DemoGitFireSet(GitFireSet):
    """Based on GitFireSet. Provide a demo version without real network interaction.
    The status of the simulated remote hosts is kept on files.
    """
    def __init__(self, repodir):
        GitFireSet.__init__(self, repodir=repodir)
        self.SSHConnector = MockSSHConnector
        self.SSHConnector.repodir = repodir
        self._demo_rulelist = defaultdict(list)

# #  User management  # #

#TODO: add user last access date?

class Users(object):
    """User management, with password hashing.
    users = {'username': ['role','pwdhash','email'], ... }
    """

    def __init__(self, d):
        self._dir = d
        self._users = loadjson('users', d=d)

    def list(self):
        return list(self._users)

    def _save(self):
        """Save users in a JSON file"""
        savejson('users', self._users, d=self._dir)

    def _hash(self, u, pwd): #TODO: should I add salting?
        """Hash username and password"""
        return sha512("%s:::%s" % (u, pwd)).hexdigest()

    def create(self, username, role, pwd, email=None):
        """
        Create a new user

        Args:
            username (string): the username
            role (string): user role
            pwd (string): user password

        Kwargs:
            email (string): optional
        """
        assert username, "Username must be provided."
        assert username not in self._users, "User already exists."
        self._users[username] = [role, self._hash(username, pwd), email]
        self._save()

    def update(self, username, role=None, pwd=None, email=None):
        """Update an user

        Args:
            username (string): the username
        Kwargs:
            role (string): user role
            pwd (string): user password
            email (string): user email
        """
        assert username in self._users, "Non existing user."
        if role is not None:
            self._users[username][0] = role
        if pwd is not None:
            self._users[username][1] = self._hash(username, pwd)
        if email is not None:
            self._users[username][2] = email
        self._save()

    def delete(self, username):
        """Delete an username"""
        try:
            self._users.pop(username)
        except KeyError:
            raise Alert, "Non existing user."
        self._save()

    def validate(self, username, pwd):
        """Validate an username and password"""
        assert username, "Missing username."
        assert username in self._users, "Incorrect user or password."
        assert self._hash(username, pwd) == self._users[username][1], \
            "Incorrect user or password."

    def __len__(self):
        """Count users"""
        return len(self._users)














