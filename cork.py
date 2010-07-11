#
# Authentication module for Bottle (not used by Firelet)
#

import bottle
from bottle import request


# #  User management  # #

#TODO: add creation and last access date?

class Users(object):
    """User management, with password hashing.
    users = {'username': ['role','pwdhash','email'], ... }
    """

    def __init__(self, d=''):
        self._dir = d
        try:
            self._users = loadjson('users', d=d)
        except:
            self._users = {} #TODO: raise alert?

    def _save(self):
        savejson('users', self._users, d=self._dir)

    def _hash(self, u, pwd): #TODO: should I add salting?
        return sha512("%s:::%s" % (u, pwd)).hexdigest()

    def create(self, username, role, pwd, email=None):
        assert username, "Username must be provided."
        assert username not in self._users, "User already exists."
        self._users[username] = [role, self._hash(username, pwd), email]
        self._save()

    def update(self, username, role=None, pwd=None, email=None):
        assert username in self._users, "Non existing user."
        if role is not None:
            self._users[username][0] = role
        if pwd is not None:
            self._users[username][1] = self._hash(username, pwd)
        if email is not None:
            self._users[username][2] = email
        self._save()

    def delete(self, username):
        try:
            self._users.pop(username)
        except KeyError:
            raise Alert, "Non existing user."
        self._save()

    def validate(self, username, pwd):
        assert username, "Missing username."
        assert username in self._users, "Incorrect user or password."
        assert self._hash(username, pwd) == self._users[username][1], "Incorrect user or password."


# #  Bottle methods  # #

def pg(name, default=''):
    return request.POST.get(name, default).strip()



@bottle.route('/login', method='POST')
def login():
    """ """
    s = bottle.request.environ.get('beaker.session')
    if 'username' in s:  # user is authenticated <--> username is set
        say("Already logged in as \"%s\"." % s['username'])
        return {'logged_in': True}
    user = pg('user', '')
    pwd = pg('pwd', '')
    try:
        users.validate(user, pwd)
        role = users._users[user][0]
        say("User %s with role %s logged in." % (user, role), level="success")
        s['username'] = user
        s['role'] = role
        s = bottle.request.environ.get('beaker.session')
        s.save()
        return {'logged_in': True}
    except (Alert, AssertionError), e:
        say("Login denied for \"%s\": %s" % (user, e), level="warning")
        return {'logged_in': False}



@bottle.route('/logout')
def logout():
    s = bottle.request.environ.get('beaker.session')
    if 'username' in s:
        s.delete()
        say('User logged out.')
    else:
        say('User already logged out.', level='warning')

