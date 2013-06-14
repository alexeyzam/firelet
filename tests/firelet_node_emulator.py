from sys import exit
from shutil import copyfile
from os import environ
from time import sleep
import logging
import sys, traceback
import glob
import os


logging.basicConfig(filename='firelet_ne.log',
    format='%(asctime)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S',
    level=logging.DEBUG)


fwname = ''
zz = lambda: sleep(.001)

def debug(s, back=False):
    global fwname
    d = "->" if back else "<-"
    logging.debug("%s %s %s" % (d, fwname, s))

def ans(fn):
    """Answer with the contents of a file"""
    cnt = 0
    for line in open(fn):
        print line.rstrip()
        cnt += 1
#        debug( "%s %s" % (fn, line.rstrip()) )
    logging.debug("Sending %s... %d lines" % (fn, cnt))

def save_iptables(li, fwname):
    """Save a new iptables conf locally"""
    fn = "new-iptables-save-%s" % fwname
    open(fn, 'w').writelines(li)

def apply_iptables(fwname):
    """Apply iptables
    Copy a file instead of running iptables-restore
    """
    src = "new-iptables-save-%s" % fwname
    dst = "live-iptables-save-%s" % fwname
    try:
        copyfile(src, dst)
    except:
        pass
    logging.info("Applied conf on %s" % fwname)

def send_iptables(fwname):
    """Deliver an iptables conf"""
    try:
        fn = "live-iptables-save-%s" % fwname
        ans(fn)
        debug("sent live iptables")
        example = """# Created by Firelet for host localhost
            *filter
            # this is an iptables conf test
            # for localhost
            COMMIT
        """
    except Exception, e:
        fn = "test/iptables-save-%s" % fwname
        ans(fn)
        debug("sent iptables from test/")

def reset():
    for filename in glob.glob('new-iptables-save-') :
        os.remove( filename )

def bye(fwname):
    logging.debug("Disconnected from %s" % fwname)
    exit()

def main():
    """"""
    global fwname

    addrmap = {
        "10.66.1.2": "InternalFW",
        "10.66.2.1": "InternalFW",
        "10.66.1.3": "Smeagol",
        "10.66.2.2": "Server001",
        "172.16.2.223": "BorderFW",
        "10.66.1.1": "BorderFW",
        '127.0.0.1': 'localhost'
    }
    history = []
    catting_new_iptables = False
    new_iptables = []
    try:
        my_ipaddr = environ['SSH_CONNECTION'].split()[2]
        fwname = addrmap[my_ipaddr]
    except:
        fwname = ''
    prompt = ''

    debug("connection established")

    while 1:

        # print a prompt if required
        if not catting_new_iptables:
            if prompt:
                print prompt
            else:
                print "firelet:%s~$" % fwname,

        # try getting input (newline is stripped)
        try:
            cmd = raw_input()
        except EOFError:
            bye(fwname)

        if not catting_new_iptables:
            history.append(cmd)
            logging.info("-> %s '%s'" % (fwname, cmd))

        # process cmd
        try:
            if cmd == 'exit':
                bye(fwname)
            elif cmd == "PS1='[PEXPECT]\$ '":
                prompt = "[PEXPECT]$ "

            # get iptables
            elif cmd == 'sudo /sbin/iptables-save':
                send_iptables(fwname)
            elif cmd == '/bin/ip addr show':
                ans("test/ip-addr-show-%s" % fwname)

            # iptables delivery
            elif cmd.startswith('cat >') and cmd.endswith('<< EOF') and 'iptables' in cmd:
                logging.info("Receiving iptables conf for %s" % fwname)
                catting_new_iptables = True
            elif catting_new_iptables and cmd == 'EOF':
                catting_new_iptables = False
                save_iptables(new_iptables, fwname)
                logging.info("Saving iptables conf for %s" % fwname)
                new_iptables = []
            elif catting_new_iptables:
                new_iptables.append(cmd + '\n')

            # apply
            elif cmd == '/sbin/iptables-restore < /etc/firelet/iptables':
                apply_iptables(fwname)

            elif cmd == 'history':
                for c in history:
                    print c

            # reset live and new configuration
            elif cmd == '##reset':
                reset()
            elif cmd.startswith('###'):
                fwname = cmd[3:]

            else:
                from subprocess import Popen
                p = Popen(cmd, shell=True)
                os.waitpid(p.pid, 0)[1]

        except Exception, e:
            logging.error("Emulator exception")
            traceback.print_exc(file=open("/tmp/%s.trace" % fwname, "a"))
            logging.error("%s", e)

if __name__ == '__main__':
    main()
