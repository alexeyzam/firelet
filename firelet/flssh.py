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

from datetime import datetime

import paramiko
import socket

from threading import Thread

from flutils import Bunch

import logging
log = logging.getLogger(__name__)

from time import time

def timeit(method):
    def timed(*args, **kw):
        t = time()
        log.debug("starting %s <" % method.__name__)
        result = method(*args, **kw)
        log.debug("> end %s %2.3fs" %
            (method.__name__, time() - t)
        )
        return result
    return timed



class Forker(object):
    """Fork a set of threads and wait for their completion"""
    def __init__(self, target, args_list):
        # Set up exception handling
        self.exception = None
        def wrapper(*args, **kwargs):
            try:
                callable(*args, **kwargs)
            except BaseException:
                pass
#                self.exception = sys.exc_info()
        # Kick off thread
        threads = []
        for args in args_list:
            thread = Thread(None, target, '', args)
            threads.append(thread)
            thread.setDaemon(True)
            thread.start()
        map(Thread.join, threads)





class SSHConnector(object):
    """Manage a pool of pxssh connections to the firewalls. Get the running
    configuation and deploy new configurations.
    """

    def __init__(self, targets=None, username='firelet'):
        self._pool = {} # connections pool: {'hostname': pxssh session, ... }
        self._targets = targets   # {hostname: [management ip address list ], ... }
        assert isinstance(targets, dict), "targets must be a dict"
        self._username = username


    @timeit
    def _connect(self):
        """Connects to the firewalls on a per-need basis.
        Returns a list of unreachable hosts.
        """
        unreachables = []

        for hostname, addrs in self._targets.iteritems():

            if hostname in self._pool:
                continue # already connected

            assert len(addrs), "No management IP address for %s, " % hostname
            ip_addr = addrs[0]      #TODO: cycle through different addrs

            c = paramiko.SSHClient()
            c.load_system_host_keys()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #TODO: configurable

            try:
                c.connect(
                    hostname=ip_addr,
                    port=22,
                    username=self._username,
    #                password=password, Q
    #                key_filename=env.key_filename,
                    timeout=10,
    #                allow_agent=not env.no_agent,
    #                look_for_keys=not env.no_keys
                )
                log.debug("Connected to %s" % hostname)
                # add the new connection to the connection pool
                self._pool[hostname] = c
            except Exception, e:
                log.debug("Unable to connect to %s: e" % (hostname, e))
                c.close()
                unreachables.append(hostname)
                #TODO: add proper exception handling

        return unreachables


    @timeit
    def __del__(self):
        """When destroyed, close existing SSH connections"""
        for c in self._pool.itervalues():
            try:
                c.close()
            except Exception, e:
                print e

    def _execute(self, hostname, cmd):
        """Execute remote command"""
        c = self._pool[hostname]
        try:
            stdin, stdout, stderr = c.exec_command(str(cmd))
            out = stdout.readlines()
        except:
            pass #TODO: handle errors
        return map(str.rstrip, out)


    def _get_conf(self, confs, hostname, username):
        """Connect to a firewall and get its configuration.
            Save the output in a dict inside the shared dict "confs"
        """
        iptables_save = self._execute(hostname, 'sudo /sbin/iptables-save')
        ip_addr_show = self._execute(hostname, '/bin/ip addr show')
        confs[hostname] = (iptables_save, ip_addr_show)
        #FIXME: if a host returns unexpected output i.e. missing sudo it should be logged


    @timeit
    def get_confs(self, keep_sessions=False):
        """Connects to the firewalls, get the configuration and return:
            { hostname: Bunch of "session, ip_addr, iptables-save, interfaces", ... }
        """
        self._connect()
        confs = {} # used by the threads to return the confs
        threads = []

        args = [(confs, hn, 'firelet') for hn in self._targets ]
        Forker(self._get_conf, args)

        log.debug("Threads stopped")
        # parse the configurations
        for hostname in self._targets:
            if not confs[hostname]:
                raise Exception, "No configuration received from %s" % hostname
            iptables_save, ip_addr_show = confs[hostname]
            #logging.debug("iptables_save:" + repr(iptables_save))
            iptables_p = self.parse_iptables_save(iptables_save, hostname=hostname)
            #FIXME: iptables-save can be very slow when a firewall cannot resolve localhost
            #log.debug("iptables_p %s" % repr(iptables_p))
            ip_a_s_p = self.parse_ip_addr_show(ip_addr_show)
            d = Bunch(iptables=iptables_p, ip_a_s=ip_a_s_p)
            confs[hostname] = d

        return confs


    def _extract_iptables_save_nat(self, li):
        for line in li:
            pass


    def parse_iptables_save(self, li, hostname=None):
        """Parse iptables-save output and returns a dict:
        {'filter': [rule, rule, ... ], 'nat': [] }

        Input example:
        # Generated by iptables-save v1.4.9 on Sun Feb 20 15:17:57 2011
        *nat
        :PREROUTING ACCEPT [0:0]
        :POSTROUTING ACCEPT [2:120]
        :OUTPUT ACCEPT [2:120]
        -A PREROUTING -d 3.3.3.3/32 -p tcp -m tcp --dport 44 -j ACCEPT
        COMMIT
        # Completed on Sun Feb 20 15:17:57 2011
        # Generated by iptables-save v1.4.9 on Sun Feb 20 15:17:57 2011
        *filter
        :INPUT ACCEPT [18151:2581032]
        :FORWARD ACCEPT [0:0]
        :OUTPUT ACCEPT [18246:2409446]
        -A INPUT -s 3.3.3.3/32 -j ACCEPT
        -A INPUT -d 3.3.3.3/32 -j ACCEPT
        -A INPUT -d 3.3.3.3/32 -p tcp -m tcp --dport 44 -j ACCEPT
        COMMIT
        # Completed on Sun Feb 20 15:17:57 2011"""

        def _rules(x):
            """Extract rules, ignore comments and anything else"""
            return x.startswith(('-A PREROUTING', '-A POSTROUTING',
                '-A OUTPUT', '-A INPUT', '-A FORWARD'))

        r = ('-A PREROUTING', '-A POSTROUTING',
                '-A OUTPUT', '-A INPUT', '-A FORWARD')

        if isinstance(li, str):
            li = li.split('\n')
        try:
            block = li[li.index('*nat'):li.index('COMMIT')]
            nat = filter(_rules, block)
        except ValueError:
            nat = []

        try:
            filter_li = li[li.index('*filter'):]    # start from *filter
            block = filter_li[:filter_li.index('COMMIT')] # up to COMMIT
            f = filter(_rules, block)
        except ValueError:
            log.error("Unable to parse iptables-save output: missing '*filter' and/or 'COMMIT' on %s" \
                % hostname)
            raise Exception, "Unable to parse iptables-save output: missing '*filter' and/or 'COMMIT' in %s" \
                % repr(li)

        return Bunch(nat=nat, filter=f)


    def _is_interface(self, s):
        """Validate an interface definition from 'ip addr show'
        """
        try:
            assert s
            assert s[0] != ' '
            n, name, info = s.split(None, 2)
            if n[-1] == ':' and name[-1] == ':':
                n = int(n[:-1])
                return True
        except:
            pass
        return False


    def parse_ip_addr_show(self, s):
        """Parse the output of 'ip addr show' and returns a dict:
        {'iface': (ip_addr_v4, ip_addr_v6)} """
        iface = ip_addr_v4 = ip_addr_v6 = None
        d = {}
        for q in s:
            if self._is_interface(q):   # new interface definition
                if iface:
                    d[iface] = (ip_addr_v4, ip_addr_v6) # save previous iface, if existing
                iface = q.split()[1][:-1]  # second field, without trailing column
                ip_addr_v4 = ip_addr_v6 = None
            elif iface and q.startswith('    inet '):
                ip_addr_v4 = q.split()[1]
            elif iface and q.startswith('    inet6 '):
                ip_addr_v6 = q.split()[1]
        if iface:
            d[iface] = (ip_addr_v4, ip_addr_v6)
        return d


    def _deliver_conf(self, status, hostname, username, block):
        """Connect to a firewall and deliver iptables configuration.
        """
        tstamp = datetime.utcnow().isoformat()[:19]
        # deliver iptables conf file
        delivery = ["cat > .iptables-%s << EOF" % tstamp]
        delivery.extend(block)
        delivery.append('EOF')
        delivery = '\n'.join(delivery)
        ret = self._execute(hostname, delivery)
        log.debug('Deployed ruleset file to %s, got """%s"""' % (hostname, ret))

        ret = self._execute(hostname, 'sync')
#        ret = self._execute(hostname, "[ -f iptables_current ] && /bin/cp -f iptables_current iptables_previous")
#        log.debug('Copied ruleset file to %s, got """%s"""' % (hostname, ret)  )
        # setup symlink
        ret = self._execute(hostname, "/bin/ln -fs .iptables-%s iptables_current" % tstamp)
        log.debug('Linked ruleset file to %s, got """%s"""' % (hostname, ret)  )
        status[hostname] = 'ok'
        return


    # TODO: unit testing
    def _gen_iptables_restore(self, hostname, rules):
        """Generate an iptable-restore-compatible configuration block
        Return a list
        """
        block = ["# Created by Firelet for host %s" % hostname]
        block.append('*filter')
        block.append(':INPUT ACCEPT') #FIXME: consider using DROP
        #FIXME: forwarding should depend on the host
        # being a network firewall or not
        block.append(':FORWARD ACCEPT')
        block.append(':OUTPUT ACCEPT')
        for rule in rules:
            block.append(str(rule))
        block.append('COMMIT')
        return block


    @timeit
    def deliver_confs(self, newconfs_d):
        """Connects to firewalls and deliver the configuration
            using multiple threads.
            hosts_d = { host: [session, ip_addr, iptables-save, interfaces], ... }
            newconfs_d =  {hostname: [rule, ... ], ... }
        """
        assert isinstance(newconfs_d, dict), "Dict expected"
        self._connect()
        status = {}
        args = []
        for hn in self._targets:
            block = self._gen_iptables_restore(hn, newconfs_d[hn])
            args.append((status, hn, 'firelet', block))

        Forker(self._deliver_conf, args)
        return status


    def _apply_remote_conf(self, status, hostname, username):
        """Run iptables-restore on a firewall
        """
        log.debug("Applying conf on %s..." % hostname)
        iptables_save = self._execute(hostname,'sudo /sbin/iptables-restore < iptables_current')
        log.debug("iptables-restore output on %s %s" % (hostname, iptables_save))
        status[hostname] = 'ok'


    @timeit
    def apply_remote_confs(self, keep_sessions=False):
        """Load the deployed ruleset on the firewalls"""
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._apply_remote_conf, args)
        return status

    #FIXME: reimplement _disconnect here



#TODO: fix MockSSHConnector

class MockSSHConnector(SSHConnector):
    """Used in Demo mode and during unit testing to prevent network interactions.
    Only some methods from SSHConnector are redefined.
    """


    def get_confs(self, keep_sessions=False):
        """Connects to the firewalls, get the configuration and return:
            { hostname: Bunch of "session, ip_addr, iptables-save, interfaces", ... }
        """
        bad = self._connect()
        assert len(bad) < 1, "Cannot connect to a host:" + repr(bad)
        confs = {} # {hostname:  Bunch(), ... }

        for hostname, p in self._pool.iteritems():
            iptables = self._interact(p, 'sudo /sbin/iptables-save')
            iptables_p = self.parse_iptables_save(iptables)
            ip_a_s = self._interact(p,'/bin/ip addr show')
            ip_a_s_p = self.parse_ip_addr_show(ip_a_s)
            confs[hostname] = Bunch(iptables=iptables, ip_a_s=ip_a_s_p)
        if not keep_sessions:
            log.debug("Closing connections.")
            d = self._disconnect()
#        log.debug("Dictionary built by get_confs: %s" % repr(confs))
        return confs





    def _connect(self):
        """Connects to the firewalls on a per-need basis.
        Returns a list of unreachable hosts.
        """
        unreachables = []
        for hostname, addrs in self._targets.iteritems():
            if hostname in self._pool and self._pool[hostname]:
                continue # already connected
            assert len(addrs), "No management IP address for %s, " % hostname
            ip_addr = addrs[0]      #TODO: cycle through different addrs?
            p = hostname # Instead of a pxssh session, the hostname is stored here
            self._pool[hostname] = p
        return unreachables

    def _disconnect(self):
        """Disconnects from the hosts and purge the session from the dict"""
        for hostname, p in self._pool.iteritems():
            try:
#                p.logout()
                self._pool[hostname] = None
            except:
                log.debug('Unable to disconnect from host "%s"' % hostname)
        #TODO: delete "None" hosts

    def _interact(self, p, s):
        """Fake interaction using files instead of SSH connections"""
        d = self.repodir
        if s == 'sudo /sbin/iptables-save':
            log.debug("Reading from %s/iptables-save-%s" % (d, p))
            return map(str.rstrip, open('%s/iptables-save-%s' % (d, p)))
        elif s == '/bin/ip addr show':
            log.debug("Reading from %s/ip-addr-show-%s" % (d, p))
            return map(str.rstrip, open('%s/ip-addr-show-%s' % (d, p)))
        else:
            raise NotImplementedError

    def deliver_confs(self, newconfs_d):
        """Write the conf on local temp files instead of delivering it.
            newconfs_d =  {hostname: [iptables-save line, line, line, ], ... }
        """
        assert isinstance(newconfs_d, dict), "Dict expected"
        self._connect()
        d = self.repodir
        for hostname, p in self._pool.iteritems():
            li = newconfs_d[hostname]
            log.debug("Writing to %s/iptables-save-%s and -x" % (d, p))
            open('%s/iptables-save-%s' % (d, p), 'w').write('\n'.join(li)+'\n')
            open('%s/iptables-save-%s-x' % (d, p), 'w').write('\n'.join(li)+'\n')
            ret = ''
#            log.debug("Deployed ruleset file to %s, got %s" % (hostname, ret)  )
        return
        #TODO: fix deliver_confs in SSHConnector

    def apply_remote_confs(self, keep_sessions=False):
        """Loads the deployed ruleset on the firewalls"""
        self._connect()
        # No way to test the iptables-restore.
        if not keep_sessions: self._disconnect()
        return



