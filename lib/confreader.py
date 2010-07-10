from ConfigParser import SafeConfigParser

class ConfReader(object):
    def __init__(self, fn):
        defaults = {
            'title': 'Firelet',
            'listen_address': 'localhost',
            'listen_port': 8082,
            'logfile': 'firelet.log',
            'demo_mode': False,
            'smtp_server_addr': '',
            'email_source': 'firelet@localhost.local',
            'email_dests': 'root@localhost',
        }
         #TODO: validate strings from the .ini file  ---> fmt = "-ofmt:%" + conf.ip_list_netflow_address
        self.__slots__ = defaults.keys()
        config = SafeConfigParser(defaults)
        config.read(fn)

        for name, default in defaults.iteritems():
            if type(default) == int:
                self.__dict__[name] = config.getint('global', name)
            elif type(default) == float:
                self.__dict__[name] = config.getfloat('global', name)
            else:
                self.__dict__[name] = config.get('global', name)

