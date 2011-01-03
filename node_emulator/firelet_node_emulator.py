from sys import exit
from os import environ
from time import sleep
import logging

logging.basicConfig(filename='firelet_ne.log',
    format='%(asctime)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S',
    level=logging.DEBUG)

zz = lambda: sleep(.001)

def ans(fn):
    """Answer with the contents of a file"""
    for l in open(fn):
        print l.strip()
        zz()
    logging.debug("< %s" % fn)

def save_iptables(li, my_name):
    """"""
    fn = "new-iptables-save-%s" % my_name
    open(fn, 'w').writelines(li)

def send_iptables(my_name):
    """"""
    try:
        fn = "new-iptables-save-%s" % my_name
        ans(fn)
    except:
        fn = "test/iptables-save-%s" % my_name
        ans(fn)

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
    my_ipaddr = environ['SSH_CONNECTION'].split()[2]
    my_name = addrmap[my_ipaddr]
    prompt = ''

    logging.info("Connection to %s" % my_name)

    while 1:

        if catting_new_iptables:
            cmd = raw_input()
        else:
            if prompt:
                print prompt
            else:
                print "firelet:%s~$ " % my_name
            cmd = raw_input()
            history.append(cmd)
            logging.info("> %s %s" % (my_name, cmd))

        if cmd == 'exit':
            exit()
        elif cmd == "PS1='[PEXPECT]\$ '":
            prompt = "[PEXPECT]$ "
        elif cmd == 'sudo /sbin/iptables-save':
            send_iptables(my_name)
        elif cmd == '/bin/ip addr show':
            ans("test/ip-addr-show-%s" % my_name)
        elif cmd == 'cat > /tmp/newiptables << EOF':
            catting_new_iptables = True
        elif catting_new_iptables and cmd == 'EOF':
            catting_new_iptables = False
            save_iptables(new_iptables, my_name)
            new_iptables = []
            logging.info("iptables conf sent to %s" % my_name)
        elif catting_new_iptables:
            new_iptables.append(cmd)
        elif cmd == '/sbin/iptables-restore < /etc/firelet/iptables':
            pass # FIXME
        elif cmd == 'history':
            for c in history:
                print c
        else:
            print cmd

if __name__ == '__main__':
    main()
