
from pxssh import pxssh
import logging
log = logging.getLogger()

class SSHConnector(object):
    """Manage a pool of pxssh connections to the firewalls. Get the running configuation and deploy new configurations.
    """

    def __init__(self, targets=None, username='firelet'):
        self._pool = {} # connections pool: {'hostname': pxssh session, ... }
        self._targets = targets   # {hostname: [management ip address list ], ... }
        self._username = username

    def _connect(self):
        """Connects to the firewalls on a per-need basis.
        Returns a list of unreachable hosts.
        """
        unreachables = []
        for hostname, addrs in self._targets.iteritems():
            if hostname in self._pool and self._pool[hostname] and self._pool[hostname].isalive():
                continue # already connected
            assert len(addrs), "No management IP address for %s, " % hostname
            ip_addr = addrs[0]      #TODO: cycle through different addrs?
            p = pxssh()
            try:
                log.debug("Connecting to %s" % ip_addr)
                p.login(ip_addr, self._username)
            except Exception, e:
                log.info("Unable to connect to %s as %s: %s" % (hostname, self._username, e))
                unreachables.append(hostname)
            self._pool[hostname] = p
        return unreachables

    def _disconnect(self):
        """Disconnects from the hosts and purge the session from the dict"""
        for hostname, p in self._pool.iteritems():
            try:
                p.logout()
                self._pool[hostname] = None
            except:
                log.debug('Unable to disconnect from host "%s"' % hostname)
        #TODO: delete "None" hosts

    def _send(self, p, s):
        p.sendline(s)
        p.prompt()
        return p.before

    def _interact(self, p, s):
        ret = self._send(p, s)
        return [r.rstrip() for r in ret.split('\n')]

    def get_confs(self, keep_sessions=False):
        """Connects to the firewalls, get the configuration and return:
            { host: [session, ip_addr, iptables-save, interfaces], ... }
        """
        bad = self._connect()
        assert len(bad) < 1, "Oops" + repr(bad)
        confs = {} # {hostname: [[iptables], [ip-addr-show]], ... }

        for hostname, p in self._pool.iteritems():
            iptables = self._interact(p, 'sudo /sbin/iptables-save')
            iptables_p = self.parse_iptables_save(iptables)
            ip_a_s = self._interact(p,'/bin/ip addr show')
            ip_a_s_p = self.parse_ip_addr_show(ip_a_s)
            confs[hostname] = [iptables_p, ip_a_s_p]
        if not keep_sessions:
            log.debug("Closing connections.")
            d = self._disconnect()
        log.debug("Dictionary built by get_confs: %s" % repr(confs))
        return confs


    def parse_iptables_save(self, s):
        """Parse iptables-save output and returns a dict:
        {'filter': [rule, rule, ... ], 'nat': [] }
        """

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
        i['filter'] = b

    #    for q in ('INPUT', 'OUTPUT', 'FORWARD'):
    #        i['filter'][q] = '\n'.join(x for x in block if x.startswith('-A %s' % q))

        return i


    def parse_ip_addr_show(self, s):
        """Parse the output of 'ip addr show' and returns a dict:
        {'iface': (ip_addr_v4, ip_addr_v6)} """
        iface = ip_addr_v4 = ip_addr_v6 = None
        d = {}
        for q in s[1:]:
            if q and not q.startswith('  '):   # new interface definition
                if iface:
                    d[iface] = (ip_addr_v4, ip_addr_v6) # save previous iface, if existing
                iface = q.split()[1][:-1]  # second field, without trailing column
                ip_addr_v4 = ip_addr_v6 = None
            elif q.startswith('    inet '):
                ip_addr_v4 = q.split()[1]
            elif q.startswith('    inet6 '):
                ip_addr_v6 = q.split()[1]
        if iface:
            d[iface] = (ip_addr_v4, ip_addr_v6)
        return d



    def deliver_confs(self, newconfs_d):
        """Connects to the firewall, deliver the configuration.
            hosts_d = { host: [session, ip_addr, iptables-save, interfaces], ... }
            newconfs_d =  {hostname: {iface: [rules, ] }, ... }
        """
        assert isinstance(newconfs_d, dict), "Dict expected"
        self._connect()

        for hostname, p in self._pool.iteritems():
            p.sendline('cat > /tmp/newiptables << EOF')
            p.sendline('# Created by Firelet for host %s' % hostname)
            p.sendline('*filter')
            for iface, rules in newconfs_d[hostname].iteritems():
                [ p.sendline(str(rule)) for rule in rules ]
            p.sendline('COMMIT')
            p.sendline('EOF')
            p.prompt()
            ret = p.before
            log.debug("Deployed ruleset file to %s, got %s" % (hostname, ret)  )
        return


    def apply_remote_confs(self, keep_sessions=False):
        """Loads the deployed ruleset on the firewalls"""
        self._connect()

        for hostname, p in self._pool.iteritems():
            ret = self._interact(p,'/sbin/iptables-restore < /tmp/newiptables')
            log.debug("Deployed ruleset file to %s, got %s" % (hostname, ret)  )

        if not keep_sessions: self._disconnect()
        return



