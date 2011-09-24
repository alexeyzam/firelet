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

from ConfigParser import SafeConfigParser


class ConfReader(object):
    def __init__(self, fn):
        defaults = {
            'title': 'Firelet',
            'listen_address': 'localhost',
            'listen_port': 8082,
            'logfile': 'firelet.log',
            'data_dir': '/var/lib/firelet',
            'demo_mode': False,
            'smtp_server_addr': '',
            'email_sender': 'firelet@localhost.local',
            'email_recipients': 'root@localhost',
            'email_smtp_server': 'localhost',
            'public_url': '',
            'stop_on_extra_interfaces': False,
            'ssh_username': 'firelet',
            'ssh_key_autoadd': True,
        }

        self.__slots__ = defaults.keys()
        config = SafeConfigParser(defaults)
        config.read(fn)

        for name, default in defaults.iteritems():
            caster = type(default)
            value = config.get('global', name, default)
            try:
                if caster == bool:
                    value = (value == 'True')
                else:
                    value = caster(value)
                self.__dict__[name] = value
            except: # pragma: no cover
                raise Exception("Unable to convert parameter '%s' having \
value '%s' to %s in configuration file %s" % (name, value, caster, fn))

