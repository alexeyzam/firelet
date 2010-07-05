#!/usr/bin/env python

import logging as log
from beaker.middleware import SessionMiddleware
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
from lib.flcore import FireSet, GitFireSet, DumbFireSet

fs = DumbFireSet()

#TODO: HG, H, N, Rule, Service creation
#TODO: Rule up/down move
#TODO: say() as a custom log target
#TODO: full rule checking upon Save
#TODO: move fireset editing in flcore

msg_list = []

def say(s, type='info'):
    """type can be: info, warning, alert"""
    if type == 'error':
        type = 'alert'
    ts = datetime.now().strftime("%H:%M:%S")
    msg_list.append((type, ts, s))
    if len(msg_list) > 20:
        msg_list.pop(0)

def pg(name, default=''):
    return request.POST.get(name, default).strip()


# # #  web services  # # #


# #  authentication  # #

#    def _validate(user, pwd):
#        if user == 'admin' and pwd == 'admin':
#            return (True, 'admin')
#        return False, ''

def _require(role='auth'):
    """Ensure the user has admin role or is authenticated at least"""
    s = bottle.request.environ.get('beaker.session')
    if not s:
        say("User needs to be authenticated.", type="warning") #TODO: not really explanatory in a multiuser session.
        raise Exception, "User needs to be authenticated."
    if role == 'auth': return
    myrole = s.get('role', '')
    if myrole == role: return
    say("A %s account is required." % repr(role))
    raise Exception



@bottle.route('/login', method='POST')
def login():
    """ """
    s = bottle.request.environ.get('beaker.session')
    if 'username' in s:  # user is authenticated <--> username is set
        say("Already logged in as \"%s\"." % s['username'])
        return
    user = pg('user', '')
    pwd = pg('pwd', '')
    if user =='admin' and pwd == 'admin':   #TODO: setup _validate function and user management
        role = 'admin'
        say("%s logged in." % user, type="success")
        s['username'] = user
        s['role'] = role
        s = bottle.request.environ.get('beaker.session')
        s.save()
        return {'logged_in': True}
    else:
        say("Login denied for \"%s\"" % user, type="warning")
        return {'logged_in': False}



@bottle.route('/logout')
def logout():
    s = bottle.request.environ.get('beaker.session')
    if 'username' in s:
        s.delete()
        say('User logged out.')
    else:
        say('User already logged out.', type='warning')


#
#class WebApp(object):
#
#def __init__(self, conf):
#    self.conf = conf
#    self.messages = []

@bottle.route('/messages')
@view('messages')
def messages():
    return dict(messages=msg_list)

@bottle.route('/')
@view('index')
def index():
    s = bottle.request.environ.get('beaker.session')
    show_logout = True if s and 'username' in s else False
    msg = None

    try:
        title = conf.title
    except:
        title = 'test'
    return dict(msg=msg, title=title, show_logout=show_logout)

# tables interaction

@bottle.route('/ruleset')
@view('ruleset')
def ruleset():
    return dict(rules=enumerate(fs.rules))

@bottle.route('/ruleset', method='POST')
def ruleset():
    global fs
    _require('admin')
    action = pg('action', '')
    name = pg('name', '')
    rid = int(pg('rid', '-1'))
    print "+" * 30, action
    #TODO: rewrite this using OO  Rule() ?
    if action == 'delete':
        try:
            bye = fs.delete('rules', rid)
            print type(bye) #FIXME
            say("Rule %d \"%s\" deleted." % (rid, bye[1]), type="success")
            return
        except Exception, e:
            say("Unable to delete rule %s - %s" % (name, e), type="alert")
            abort(500)
    elif action == 'moveup':
        try:
            fs.rule_moveup(rid)
        except Exception, e:
            say("Cannot move rule %d up." % rid)
    elif action == 'movedown':
        try:
            fs.rule_movedown(rid)
        except Exception, e:
            say("Cannot move rule %d down." % rid)
    elif action == 'disable':
        fs.rule_disable(rid)
        say("Rule %d disabled." % rid)
    elif action == 'enable':
        fs.rule_enable(rid)
        say("Rule %d enabled." % rid)


@bottle.route('/hostgroups')
@view('hostgroups')
def hostgroups():
    return dict(hostgroups=fs.hostgroups)

@bottle.route('/hostgroups', method='POST')
def hostgroups():
    _require('admin')
    action = pg('action', '')
    name = pg('name', '')  #FIXME: move all tables to the new delete-by-rid method
    if action == 'delete':
        try:
            hostgroups =  [ h for h in hostgroups if h[0] != name ]
            say("Host Group %s deleted." % name, type="success")
            return
        except Exception, e:
            say("Unable to delete %s - %s" % (name, e), type="alert")
            abort(500)


@bottle.route('/hosts')
@view('hosts')
def hosts():
    return dict(hosts=fs.hosts)


@bottle.route('/hosts', method='POST')
def hosts():
    _require('admin')
    action = pg('action', '')
    if action == 'delete':
        try:
            name = pg('name', '')
#            hosts =  [ h for h in hosts if h[0] != name ] #FIXME
            say("Host %s deleted." % name, type="success")
            return
        except Exception, e:
            say("Unable to delete %s - %s" % (name, e), type="alert")
            abort(500)

@bottle.route('/hosts_new', method='POST')
def hosts_new():
    _require('admin')
    hostname = pg('hostname')
    iface = pg('iface')
    ip_addr = pg('ip_addr')
    print hostname, iface, ip_addr
    if hostname.startswith("test"):
#        print repr(hosts) #FIXME
#        hosts.append((hostname, iface, ip_addr))
        say('Host %s added.' % hostname, type="success")
        return {'ok': True}

    say('Unable to add %s.' % hostname, type="alert")
    return {'ok': False, 'hostname':'Must start with "test"'}



@bottle.route('/networks')
@view('networks')
def networks():
    return dict(networks=fs.networks)

@bottle.route('/networks', method='POST')
def networks():
    global networks
    _require('admin')
    action = pg('action', '')
    name = pg('name', '')
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
    return dict(services=fs.services)

@bottle.route('/services', method='POST')
def services():
    _require('admin')
    global services
    action = pg('action', '')
    name = pg('name', '')
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
    _require('admin')
    msg = pg('msg', '')
    say('Saving configuration...')
    say("Msg: %s" % msg)
    say('Configuration saved.', type="success")
    print 'woohoo'
    return

@bottle.route('/reset', method='POST')
def resetbtn():
    _require('admin')
    say('Configuration reset.', type="success")
    return

@bottle.route('/check', method='POST')
def checkbtn():
    _require('admin')
    say('Configuration check started...')
    say('Configuration check successful.', type="success")
    return

@bottle.route('/deploy', method='POST')
def deploybtn():
    _require('admin')
    say('Configuration deployment started...')
    say('Compiling firewall rules...')
    try:
        comp_rules = fs.compile()
        for r in comp_rules:
            say(r)
        rd = fs.compile_dict()
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
        bottle.debug(True)
        say("Firelet started in debug mode.", type="success")
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


    session_opts = {
        'session.type': 'cookie',
        'session.validate_key': True,
    }
    app = bottle.default_app()
    app = SessionMiddleware(app, session_opts)

    run(app=app, host=conf.listen_address, port=conf.listen_port, reloader=reload)



if __name__ == "__main__":
    main()













