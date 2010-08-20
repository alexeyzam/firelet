
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

def flag(s):    #TODO: unit testing
    if s in (1, True, '1', 'True', 'y', 'on' ):
        return '1'
    elif s in (0, False, '0', 'False', 'n', 'off', ''):
        return '0'
    else:
        raise Exception, '"%s" is not a valid flag value' % s
