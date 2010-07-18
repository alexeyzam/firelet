
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


