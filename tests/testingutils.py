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

from json import dumps
from os import listdir, mkdir
from tempfile import mkdtemp
from time import time
import inspect
import logging
import os
import sys

import pytest
repodir = pytest.mark.usefixtures("repodir")
class BaseFunctionalTesting(object):
    def setup(self):
        self._setup_repodir()
        pass

    def _setup_repodir(self):
        self._repodir = repodir

    def teardown(self):
        pass

    def _teardown_repodir(self, *a):
        pass



def show(s, o=None):
    """Log an object representation"""

    stack = [x[3] for x in inspect.stack()]
    if 'runTest' in stack:
        rt = stack.index('runTest')
        stack = stack[1:rt]
    else:
        stack = stack[1:3]
    stack = "->".join(reversed(stack))

    try:
        d = dumps(o, indent=2)
    except:
        d = repr(o)
    li = d.split('\n')

    if len(li) < 3:
        if o:
            return "%s %s: %s" % (stack, s, repr(o))
        else:
            return "%s %s" % (stack, s)
    else:
        indented = "\n    ".join(li)
        return "\n-------- [%s] ---------\n    %s\n----- [end of %s] -----\n" % (s, indented, s)


# utility functions

def string_in_list(s, li):
    """Count how many times a string is contained in a list of strings
    No exact match is required
    >>> strings_in_list('p', ['apple'])
    1
    """
    return sum((1 for x in li if s in str(x)))

def test_string_in_list():
    li = ['apple', 'p', '', None, 123, '   ']
    assert string_in_list('p', li) == 2

def assert_equal_line_by_line(li1, li2):
    for x, y in zip(li1, li2):
        assert x == y, "'%s' differs from '%s' in:\n%s\n%s\n" % (repr(li1), repr(li2))

def duplicates(li):
    """Find duplicate elements in a list
    Return [ (item, number_of_instances), ... ]
    """
    return [(i,li.count(i))  for i in set(li) if li.count(i) > 1 ]

