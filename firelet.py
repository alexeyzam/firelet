#!/usr/bin/env python

import logging as log
import bottle
from bottle import route, send_file, run, view, request
from bottle import debug as bottle_debug
from collections import defaultdict
from datetime import datetime
from subprocess import Popen, PIPE
from sys import argv, exit
from time import time, sleep, localtime

from lib.confreader import ConfReader
from lib import mailer
from lib.flcore import *

rules = loadcsv('rules')
hosts = loadcsv('hosts')
hostgroups = loadcsv('hostgroups')
services = loadcsv('services')
networks = loadcsv('networks')

#TODO: HG, H, N, Rule, Service creation
#TODO: Rule up/down move
#TODO: say() as a custom log target
#TODO: full rule checking upon Save
#TODO: move fireset editing in flcore

messages = []

def say(s, type='info'):
    """type can be: info, warning, alert"""
    if type == 'error':
        type = 'alert'
    ts = datetime.now().strftime("%H:%M:%S")
    messages.append((type, ts, s))
    if len(messages) > 20:
        messages.pop(0)

def pg(name, default=''):
    return request.POST.get(name, default).strip()

# web services

class WebApp(object):

    def __init__(self, conf):
        self.conf = conf
        self.messages = []

    def say(s, type='info'):
        self.messages.append((type, s))

    @bottle.route('/messages')
    @view('messages')
    def messages():
        return dict(messages=messages)



    @bottle.route('/')
    @view('index')
    def index():
        msg = None

        try:
            title = conf.title
        except:
            title = 'test'
        return dict(msg=msg, title=title)

    @bottle.route('/ruleset')
    @view('ruleset')
    def ruleset():
        return dict(rules=enumerate(rules))

    @bottle.route('/ruleset', method='POST')
    def ruleset():
        global rules
        action = request.POST.get('action', '').strip()
        name = request.POST.get('name', '').strip()
        rid = int(request.POST.get('rid', '-1').strip())
        print "+" * 30, action
        if action == 'delete':
            try:
                bye = rules.pop(rid)
                say("Rule %d \"%s\" deleted." % (rid, bye[1]), type="success")
                return
            except Exception, e:
                say("Unable to delete %s - %s" % (name, e), type="alert")
                abort(500)
        elif action == 'moveup':
            try:
                rules[rid], rules[rid - 1] = rules[rid - 1], rules[rid]
            except Exception, e:
                say("Cannot move rule %d up." % rid)
        elif action == 'movedown':
            try:
                rules[rid], rules[rid + 1] = rules[rid + 1], rules[rid]
            except Exception, e:
                say("Cannot move rule %d down." % rid)




    @bottle.route('/hostgroups')
    @view('hostgroups')
    def hostgroups():
        return dict(hostgroups=hostgroups)

    @bottle.route('/hostgroups', method='POST')
    def hostgroups():
        global hostgroups
        action = request.POST.get('action', '').strip()
        name = request.POST.get('name', '').strip()
        if action == 'delete':
            try:
                from random import random
                if random() > 0.9:
                    raise Exception, "test"
                hostgroups =  [ h for h in hostgroups if h[0] != name ]
                say("Host Group %s deleted." % name, type="success")
                return
            except Exception, e:
                say("Unable to delete %s - %s" % (name, e), type="alert")
                abort(500)


    @bottle.route('/hosts')
    @view('hosts')
    def hosts():
        return dict(hosts=hosts)


    @bottle.route('/hosts', method='POST')
    def hosts():
        global hosts
        action = request.POST.get('action', '').strip()
        if action == 'delete':
            try:
                name = request.POST.get('name', '').strip()
                hosts =  [ h for h in hosts if h[0] != name ]
                say("Host %s deleted." % name, type="success")
                return
            except Exception, e:
                say("Unable to delete %s - %s" % (name, e), type="alert")
                abort(500)

    @bottle.route('/hosts_new', method='POST')
    def hosts_new():
        global hosts
        hostname = pg('hostname')
        iface = pg('iface')
        ip_addr = pg('ip_addr')
        print hostname, iface, ip_addr
        if hostname.startswith("test"):
            print repr(hosts)
            hosts.append((hostname, iface, ip_addr))
            say('Host %s added.' % hostname, type="success")
            return {'ok': True}

        say('Unable to add %s.' % hostname, type="alert")
        return {'ok': False, 'hostname':'Must start with "test"'}



    @bottle.route('/networks')
    @view('networks')
    def networks():
        return dict(networks=networks)

    @bottle.route('/networks', method='POST')
    def networks():
        global networks
        action = request.POST.get('action', '').strip()
        name = request.POST.get('name', '').strip()
        if action == 'delete':
            try:
                networks =  [ h for h in networks if h[0] != name ]
                say("Network %s deleted." % name, type="success")
                return
            except Exception, e:
                say("Unable to delete %s - %s" % (name, e), type="alert")
                abort(500)


    @bottle.route('/services')
    @view('services')
    def services():
        return dict(services=services)

    @bottle.route('/services', method='POST')
    def services():
        global services
        action = request.POST.get('action', '').strip()
        name = request.POST.get('name', '').strip()
        if action == 'delete':
            try:
                services =  [ h for h in services if h[0] != name ]
                say("Service %s deleted." % name, type="success")
                return
            except Exception, e:
                say("Unable to delete %s - %s" % (name, e), type="alert")
                abort(500)


    # management commands

    @bottle.route('/manage')
    @view('manage')
    def manage():
        return dict()

    @bottle.route('/saveneeded')
    def saveneeded():
        return dict(sn=True)

    @bottle.route('/save', method='POST')
    def savebtn():
        msg = request.POST.get('msg', '').strip()
        say('Saving configuration...')
        say("Msg: %s" % msg)
        say('Configuration saved.', type="success")
        print 'woohoo'
        return

    @bottle.route('/reset', method='POST')
    def resetbtn():
        say('Configuration reset.', type="success")
        return

    @bottle.route('/check', method='POST')
    def checkbtn():
        say('Configuration check started...')
        from time import sleep
        sleep(4)
        say('Configuration check successful.', type="success")
        return

    @bottle.route('/deploy', method='POST')
    def deploybtn():
        say('Configuration deployment started...')
        say('Compiling firewall rules...')
        try:
            comp_rules = compile(rules, hosts, hostgroups, services, networks)
            for r in comp_rules:
                say(r)
            rd = select_rules(hosts, comp_rules)
#            say(q for q in repr(rd).split('\n'))
        except Exception, e:
            say("Compilation failed: %s" % e,  type="alert")
            return
        say('Configuration deployed.', type="success")
        return


    # serving files

    @bottle.route('/static/:filename#[a-zA-Z0-9_\.?\/?]+#')
    def static_file(filename):
        if filename == '/jquery-ui.js':
            send_file('/usr/share/javascript/jquery-ui/jquery-ui.js') #TODO: support other distros
        elif filename == 'jquery.min.js':
            send_file('/usr/share/javascript/jquery/jquery.min.js', root='/')
        elif filename == 'jquery-ui.custom.css': #TODO: support version change
            send_file('/usr/share/javascript/jquery-ui/css/smoothness/jquery-ui-1.7.2.custom.css')
        else:
            send_file(filename, root='static')

    @bottle.route('/favicon.ico')
    def favicon():
        send_file('favicon.ico', root='static')

#webapp = WebApp(conf)






def main():
    global conf

    try:
        fn = argv[1:]
        if '-D' in fn: fn.remove('-D')
        if not fn: fn = 'firelet.ini'
        conf = ConfReader(fn=fn)
    except Exception, e:
        log.error("Exception %s while reading configuration file '%s'" % (e, fn))
        exit(1)

    # logging

    if '-D' in argv:
        debug_mode = True
        log.basicConfig(level=log.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')
        log.debug("Debug mode")
        bottle_debug(True)
        reload = True
    else:
        debug_mode = False
        log.basicConfig(level=log.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=conf.logfile,
                    filemode='w')
        reload = False

    say("Firelet started.", type="success")

    run(host=conf.listen_address, port=conf.listen_port, reloader=reload)

#    log.info("Terminating daemon...")
#    log.info("Terminated.")


if __name__ == "__main__":
    main()













