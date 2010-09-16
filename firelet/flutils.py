from copy import deepcopy

class Alert(Exception):
    """Custom exception used to send an alert message to the user"""


class Bunch(object):
    """A dict that exposes its values as attributes."""
    def __init__(self, **kw):
        self.__dict__ = dict(kw)

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def _token(self):
        """Generate a simple hash"""
        return hex(abs(hash(str(self.__dict__))))[2:]

    def validate_token(self, t): #TODO: unit testing
        assert token == self._token(), \
        "Unable to update: one or more items has been modified in the meantime."

    def attr_dict(self):
        """Provide a copy of the internal dict, with a token"""
        d = deepcopy(self.__dict__)
        d['token'] = self._token()
        return d

    def update(self, d):
        """Set/update the internal dictionary"""
        for k in self.__dict__:
            self.__dict__[k] = d[k]


def flag(s):    #TODO: unit testing
    if s in (1, True, '1', 'True', 'y', 'on' ):
        return '1'
    elif s in (0, False, '0', 'False', 'n', 'off', ''):
        return '0'
    else:
        raise Exception, '"%s" is not a valid flag value' % s

def extract(d, keys):
    """Returns a new dict with only the chosen keys, if present"""
    return dict((k, d[k]) for k in keys if k in d)

def extract_all(d, keys):
    """Returns a new dict with only the chosen keys"""
    return dict((k, d[k]) for k in keys)

