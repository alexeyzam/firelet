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

zz = lambda: sleep(.001)

def ans(fn):
    """Answer with the contents of a file"""
    for line in open(fn):
        print line.rstrip()
#    logging.debug("< %s" % fn)

def save_iptables(li, my_name):
    """Save a new iptables conf locally"""
    fn = "new-iptables-save-%s" % my_name
    open(fn, 'w').writelines(li)

def apply_iptables(my_name):
    """Apply iptables
    Copy a file instead of running iptables-restore
    """
    src = "new-iptables-save-%s" % my_name
    dst = "live-iptables-save-%s" % my_name
    try:
        copyfile(src, dst)
    except:
        pass
    logging.info("Applied conf on %s" % my_name)

def send_iptables(my_name):
    """Deliver an iptables conf"""
    try:
        fn = "live-iptables-save-%s" % my_name
        ans(fn)
        logging.info("live iptables fetched from %s" % my_name)
       #logging.debug(open(fn).readlines())
        example = """# Created by Firelet for host localhost
            *filter
            # this is an iptables conf test
            # for localhost
            COMMIT
        """
    except:
        pass
#        fn = "test/iptables-save-%s" % my_name
#        ans(fn)

def reset():
    for filename in glob.glob('new-iptables-save-') :
        os.remove( filename )

def bye(my_name):
    logging.debug("Disconnected from %s" % my_name)
    exit()

def main():
    """"""
    addrmap = {
        "10.66.1.2": "Bilbo",
        "10.66.2.1": "Bilbo",
        "10.66.1.3": "Smeagol",
        "10.66.2.2": "Fangorn",
        "172.16.2.223": "Gandalf",
        "10.66.1.1": "Gandalf",
        '127.0.0.1': 'localhost'
    }
    history = []
    catting_new_iptables = False
    new_iptables = []
    try:
        my_ipaddr = environ['SSH_CONNECTION'].split()[2]
        my_name = addrmap[my_ipaddr]
    except:
        my_name = ''
    prompt = ''

    logging.info("Connection to %s" % my_name)

    while 1:

        # print a prompt if required
        if not catting_new_iptables:
            if prompt:
                print prompt
            else:
                print "firelet:%s~$" % my_name,

        # try getting input (newline is stripped)
        try:
            cmd = raw_input()
        except EOFError:
            bye(my_name)

        if not catting_new_iptables:
            history.append(cmd)
#            logging.info("> %s '%s'" % (my_name, cmd))

        # process cmd
        try:
            if cmd == 'exit':
                bye(my_name)
            elif cmd == "PS1='[PEXPECT]\$ '":
                prompt = "[PEXPECT]$ "

            # get iptables
            elif cmd == 'sudo /sbin/iptables-save':
                send_iptables(my_name)
            elif cmd == '/bin/ip addr show':
                ans("test/ip-addr-show-%s" % my_name)

            # iptables delivery
            elif cmd.startswith('cat >') and cmd.endswith('<< EOF') and 'iptables' in cmd:
                logging.info("Receiving iptables conf for %s" % my_name)
                catting_new_iptables = True
            elif catting_new_iptables and cmd == 'EOF':
                catting_new_iptables = False
                save_iptables(new_iptables, my_name)
                logging.info("Saving iptables conf for %s" % my_name)
                new_iptables = []
            elif catting_new_iptables:
                new_iptables.append(cmd + '\n')

            # apply
            elif cmd == '/sbin/iptables-restore < /etc/firelet/iptables':
                apply_iptables(my_name)

            elif cmd == 'history':
                for c in history:
                    print c

            # reset live and new configuration
            elif cmd == '##reset':
                reset()
            elif cmd.startswith('###'):
                my_name = cmd[3:]

            else:
                from subprocess import Popen
                p = Popen(cmd, shell=True)
                os.waitpid(p.pid, 0)[1]

        except Exception, e:
            logging.error("Emulator exception")
            traceback.print_exc(file=open("/tmp/%s.trace" % my_name, "a"))
            logging.error("%s", e)

if __name__ == '__main__':
    main()
