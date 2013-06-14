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

from logging import getLogger
from nose.tools import raises, assert_raises, with_setup
from webtest import TestApp, AppError
import os

log = getLogger(__name__)
deb = log.debug

from testingutils import setup_dir, teardown_dir

from firelet import fireletd

#@with_setup(setup_dir, teardown_dir)
#def test_not_auth():
##    debug_mode = True
##    bottle.debug(True)
##    globals()['users'] = Users(d=repodir)
#    app = bottle.default_app()
##    app = SessionMiddleware(app, session_opts)
#    result = app.handle('/', 'GET')
#    assert 'Please insert your credentials' in result

#TODO: implement webapp testing
REDIR = '302 Found'
app = None
tmpdir = None
orig_dir = None

def setup():
    setup_dir()
    # create global TestApp instance
    global app
    app = TestApp(fireletd.app)

def teardown():
    teardown_dir()
    app = None

@raises(AppError)
def test_bogus_page():
    app.get('/bogus_page')

def test_index_page():
    assert app.get('/').status == '200 OK'

def login():
    """run setup_app and log in"""
    global app
    setup_app()
    p = app.post('/login', {'user': 'admin', 'pwd': 'admin'})












