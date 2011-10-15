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
import logging
import paramiko
import socket
from time import time
from threading import Thread

from flutils import Bunch

log = logging.getLogger(__name__)

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



class Forker(object):
    """Fork a set of threads and wait for their completion
    """
    def __init__(self, target, args_list, timeout=5):
        """Setup Forker instance

        :param target: function
        :type target: function.
        :param args_list: argument list
        :type args_list: list.
        """
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
        for t in threads:
            t.join(timeout)
        timed_out = filter(Thread.isAlive, threads)
        if timed_out:
            log.error("Some threads timed out: %s" % repr(timed_out))
            #FIXME: do something with timed out threads
            #map(Thread.join, threads)


class SSHConnector(object):
    """Manage a pool of pxssh connections to the firewalls. Get the running
    configuation and deploy new configurations.
    """

    def __init__(self, targets=None, username='firelet',
        ssh_key_autoadd=True, password=None):
        """SSHConnector init

        :param targets: targets {hostname: [management ipaddr list ], ... }
        :type targets: dict.
        :param username: SSH username (defaults to 'firelet')
        :type username: str.
        :param ssh_key_autoadd: ssh key autoadd (defaults to True)
        :type ssh_key_autoadd: bool.
        :param password: SSH password, used only in assimilation (defaults to None)
        :type password: str.
        """

        self._pool = {} # connections pool: {'hostname': pxssh session, ... }
        self._pool_status = {} # connections status: {'hostname': 'status', ... }
        self._targets = targets   # {hostname: [management ip address list ], ... }
        assert isinstance(targets, dict), "targets must be a dict"
        self._username = username
        self._ssh_key_autoadd = ssh_key_autoadd
        #FIXME: logging level for paramiko
#        paramiko_logger = paramiko.util.logging.getLogger()
#        paramiko_logger.setLevel(logging.WARN)
#        log = logging.getLogger()
#        log.setLevel(logging.DEBUG)

    def _connect_one(self, hostname, addrs):
        """Connect to a firewall
        """
        assert len(addrs), "No management IP address for %s, " % hostname

        c = paramiko.SSHClient()
        c.load_system_host_keys()
        #TODO: test ssh_key_autoadd configuration parameter
        if self._ssh_key_autoadd:
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Cycle through IP addrs until a connection is established
        for ip_addr in addrs:
            try:
                log.debug("Connecting to %s on %s" % (hostname, ip_addr))
                c.connect(
                    hostname=ip_addr,
                    port=22,
                    username=self._username,
                    #password=password,
                    #key_filename=env.key_filename,
                    timeout=10,
                    #allow_agent=not env.no_agent,
                    #look_for_keys=not env.no_keys
                )
                c.hostname = hostname
                c.ip_addr = ip_addr
                log.debug("Connected to %s on %s" % (hostname, ip_addr))
                # add the new connection to the connection pool
                self._pool[hostname] = c
                return
            except Exception, e:
                log.info("Unable to connect to %s on %s: %s" % (hostname, ip_addr, e))

        raise Exception("Unable to connect to %s" % (hostname))


    def _connect(self):
        """Connect to the firewalls on a per-need basis.
        Returns a list of unreachable hosts.
        """
        unreachables = []
        args = [ (hn, addrs) for hn, addrs in self._targets.iteritems() if hn not in self._pool ]
        if not args:
            return []
        Forker(self._connect_one, args)
        missing = len(self._targets) - len(self._pool)
        if missing:
            print "missing", missing
        return unreachables


    @timeit
    def __del__(self):
        """When destroyed, close existing SSH connections"""
        for c in self._pool.itervalues():
            try:
                c.close()
            except:
                pass # nothing useful can be done

    @timeit
    def _disconnect(self):
        """Close existing SSH connections"""
        for hn, c in self._pool.items():
            try:
                self._pool.pop(hn)
                c.close()
            except Exception, e:
                log.info("Error while disconnecting from a host: %s" % e)

    #TODO: refactor the use of _connect_one
    # do we have to connect to every firewall every time we run _execute? no

    @timeit
    def _execute(self, hostname, cmd, get_output=True):
        """Execute remote command"""
        self._connect()
#        if hostname not in self._pool:
#            log.info("Setting up connection to %s" % hostname)
#            ip_addrs = self._targets[hostname]
#            self._connect_one(self, hostname, ip_addrs)
#            assert hostname in self._pool, "EWW" #TODO:

        c = self._pool[hostname]
        self._pool_status[hostname] = ''
        assert not isinstance(c, str), repr(c)

        if hostname not in self._pool:
            log.info("Not connected to %s" % hostname)
            return

        if get_output:
            try:
                stdin, stdout, stderr = c.exec_command(cmd)
                out = stdout.readlines()
                self._pool_status[hostname] = 'ok'
                return map(str.rstrip, out)
            except Exception, e:
                #TODO: handle failed executions.
                self._pool_status[hostname] = "%s" % e
            return None

        else:
            c.exec_command(cmd)

    @timeit
    def _get_conf(self, confs, hostname, username):
        """Connect to a firewall and get its configuration.
            Save the output in a dict inside the shared dict "confs"
        """
        self._execute(hostname, 'logger -t firelet "Fetching existing configuration %s"' % hostname)
        iptables_save = self._execute(hostname, 'sudo /sbin/iptables-save')
        ip_addr_show = self._execute(hostname, '/bin/ip addr show')
        #log.debug("iptables save on %s: %s..." % (hostname, repr(iptables_save)[:130]))
        confs[hostname] = (iptables_save, ip_addr_show)

    @timeit
    def get_confs(self, keep_sessions=False):
        """Connects to the firewalls, get the configuration and

        :return: { hostname: Bunch of "session, ip_addr, iptables-save, interfaces", ... }
        :rtype: dict
        """
        self._connect()
        confs = {} # used by the threads to return the confs
        threads = []

        args = [(confs, hn, 'firelet') for hn in self._targets ]
        Forker(self._get_conf, args)

        # parse the configurations
        for hostname in self._targets:
            if hostname not in confs:
                raise Exception, "No configuration received from %s" % hostname
            iptables_save, ip_addr_show = confs[hostname]
            logging.debug("iptables_save:" + repr(iptables_save))
            iptables_p = self.parse_iptables_save(iptables_save, hostname=hostname)
            #FIXME: iptables-save can be very slow when a firewall cannot resolve localhost
            #log.debug("iptables_p %s" % repr(iptables_p))
            ip_a_s_p = self.parse_ip_addr_show(ip_addr_show)
            d = Bunch(iptables=iptables_p, ip_a_s=ip_a_s_p)
            confs[hostname] = d
        #FIXME: if a host returns unexpected output i.e. missing sudo it should be logged

        return confs

    def _extract_iptables_save_nat(self, li):
        """Extract NAT table configuration from iptables-save
        :param li: iptables-save output
        :type li: list.
        """
        pass
        #TODO: implement _extract_iptables_save_nat

    def parse_iptables_save(self, li, hostname=None):
        """Parse iptables-save output and returns a dict:
        
        :param li: iptables-save output
        :type li: list.
        :param hostname: hostname (optional)
        :type hostname: str.
        :return: {'filter': [rule, rule, ... ], 'nat': [] }
        :rtype: dict of lists
        """

        example = """Input example:
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
        # Completed on Sun Feb 20 15:17:57 2011
        """
        
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
            log.error("Unable to parse iptables-save output: missing '*filter'"
                " and/or 'COMMIT' on %s: %s" % (hostname, repr(li)))
            raise Exception, "Unable to parse iptables-save output: missing "
            "'*filter' and/or 'COMMIT' in %s" % repr(li)

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
            return False
        return False

    def parse_ip_addr_show(self, s):
        """Parse the output of 'ip addr show' and returns a dict:
        
        :param s: ip addr show output
        :type s: list.
        :rtype: {'iface': (ip_addr_v4, ip_addr_v6)}
        """
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
        delivery = ["cat > .iptables-%s << EOF" % tstamp] + block + ['EOF']
        delivery = '\n'.join(delivery)
        ret = self._execute(hostname, delivery)
        log.debug('Deployed ruleset file to %s, got """%s"""' % (hostname, ret))

        ret = self._execute(hostname, 'sync')
#        ret = self._execute(hostname, "[ -f iptables_current ] && /bin/cp -f iptables_current iptables_previous")
#        log.debug('Copied ruleset file to %s, got """%s"""' % (hostname, ret)  )
        # setup symlink
        ret = self._execute(hostname, "/bin/ln -fs .iptables-%s iptables_current" % tstamp)
        self._execute(hostname, 'logger -t firelet "Existing configuration saved"')
        log.debug('Linked ruleset file to %s, got """%s"""' % (hostname, ret)  )
        status[hostname] = 'ok'
        return

    @timeit
    def deliver_confs(self, newconfs_d):
        """Connects to firewalls and deliver the configuration
        using multiple threads.
        
        :arg newconfs_d: configurations: {hostname: [rule, ... ], ... }
        :type newconfs_d: dict
        :returns: status
        :rtype: dict
        """
        # hosts_d = { host: [session, ip_addr, iptables-save, interfaces], ... }
        assert isinstance(newconfs_d, dict), "Dict expected"
        self._connect()
        status = {}
        args = []
        for hn in self._targets:
            block = newconfs_d[hn]
            args.append((status, hn, 'firelet', block))

        Forker(self._deliver_conf, args)
        return status


    def _save_existing_conf(self, status, hostname, username):
        """Run iptables-save to save a copy of the existing configuration
        """
        log.debug("Saving conf on %s..." % hostname)
        self._execute(hostname, 'logger -t firelet "Saving running configuration"')
        iptables_out = self._execute(hostname,
            'sudo /sbin/iptables-save > iptables_previous 2>&1')
        if iptables_out == []:
            status[hostname] = 'ok'
        else:
            log.warn("iptables-save output on %s %s" % (hostname, iptables_out))

    @timeit
    def save_existing_confs(self, keep_sessions=False):
        """Run _save_existing_conf on the firewalls
        
        :return: status
        :rtype: dict
        """
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._save_existing_conf, args)
        return status


    def _setup_auto_rollback(self, status, hostname, username):
        """Run iptables-restore automatically on a firewall after a timeout.
        The previously saved conf will be loaded.
        """
        #log.debug(" on %s..." % hostname)
        self._execute(hostname, "rm -f rollback.pid; ("
            "logger -t firelet 'Automatic rollback enabled';"
            "sleep 15;"
            "logger -t firelet 'Rolling back configuration!';"
            "sudo /sbin/iptables-restore < iptables_previous && "
            "logger -t firelet 'Configuration rolled back!';"
            "rm -f rollback.pid;"
            ") 2>/dev/null & echo $! > rollback.pid", get_output=False
        )
        log.debug("Auto rollback enabled on %s" % hostname)

    @timeit
    def setup_auto_rollbacks(self, keep_sessions=False):
        """Setup the auto-rollback script on the firewalls.
        Iptables-restore is ran automatically after a timeout,
        and the previously saved configuration is loaded.
        
        :return: status
        :rtype: dict
        """
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._setup_auto_rollback, args)
        return status


    def _cancel_auto_rollback(self, status, hostname, username):
        """Kill the running auto-rollback script
        """
        log.debug("Killing auto-rollback on %s" % hostname)
        self._execute(hostname, 'logger -t firelet "Cancelling automatic rollback"')
        out = self._execute(hostname, "kill $(cat rollback.pid); rm -f rollback.pid")
        if out == []:
            status[hostname] = 'ok'
        else:
            log.warn("killing auto-rollback output on %s %s" % (hostname, out))

    @timeit
    def cancel_auto_rollbacks(self, keep_sessions=False):
        """Kill the auto-rollback script running on the firewalls
        :return: status
        :rtype: dict
        """
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._cancel_auto_rollback, args)
        failed = set(self._targets) - set(status)
        if failed:
            raise Exception, "Cancelling rollback failed on %s" % ', '.join(failed)
        return status


    def _apply_remote_conf(self, status, hostname, username):
        """Run iptables-restore on a firewall
        """
        log.debug("Applying conf on %s..." % hostname)
        self._execute(hostname, 'logger -t firelet "Applying new firewall configuration"')
        self._execute(hostname, 'logger -t firelet "cur file: $(wc -l iptables_current)"')
        self._execute(hostname, 'logger -t firelet "ipt-save: $(sudo iptables-save | wc -l)"')
        iptables_out = self._execute(hostname,
            'sudo /sbin/iptables-restore < iptables_current 2>&1')
        if iptables_out == []:
            status[hostname] = 'ok'
        else:
            log.warn("iptables-restore output on %s %s" % (hostname, iptables_out))
            self._execute(hostname, 'logger -t firelet "iptables-restore failed"')
        self._execute(hostname, 'logger -t firelet "$(sudo iptables-save | wc -l)"')

    @timeit
    def apply_remote_confs(self, keep_sessions=False):
        """Load the deployed ruleset on the firewalls"""
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._apply_remote_conf, args)
        return status


    def _log_ping(self, status, hostname, username):
        self._execute(hostname, 'logger -t firelet ping')

    @timeit
    def log_ping(self):
        """Connect to the firewalls and log a 'ping' message on syslog
        """
        status = {}
        args = [(status, hn, 'firelet') for hn in self._targets ]
        Forker(self._log_ping, args)
        return status


#TODO: fix MockSSHConnector

class MockSSHConnector(SSHConnector):
    """Used in Demo mode and during unit testing to prevent network interactions.
    Only some methods from SSHConnector are redefined.
    """

    def _connect_one(self, hostname, addrs):
        self._pool[hostname] = 'fake_connection'

    def _disconnect(self):
        pass

    def _execute(self, hostname, s, get_output=True):
        """Execute remote command"""
        self._connect()
        d = self.repodir
        h = hostname
        # Used by _get_conf
        if s == 'sudo /sbin/iptables-save':
            log.debug("Reading from %s/iptables-save-%s" % (d, h))
            return map(str.rstrip, open('%s/iptables-save-%s' % (d, h)))
        elif s == '/bin/ip addr show':
            log.debug("Reading from %s/ip-addr-show-%s" % (d, h))
            return map(str.rstrip, open('%s/ip-addr-show-%s' % (d, h)))
        # Used by _deliver_conf
        elif 'cat > .iptables' in s:
            log.debug("Writing to %s/iptables-save-%s and -x" % (d, h))
            li = s.split('\n')[1:-1]
            open('%s/iptables-save-%s' % (d, h), 'w').write('\n'.join(li)+'\n')
            open('%s/iptables-save-%s-x' % (d, h), 'w').write('\n'.join(li)+'\n')
        else:
            # Ignore other commands
            ignored = ('logger -t',
                'kill $(cat rollback.pid)',
                'sudo /sbin/iptables-restore < iptables_current',
                'sudo /sbin/iptables-save > iptables_previous',
                'sync',
                '/bin/ln -fs .iptables'
            )
            for i in ignored:
                if i in s:
                    return []
            # Exception on unknown ones
            raise NotImplementedError, s






