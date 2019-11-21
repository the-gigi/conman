
class ConManBase(dict):
    def __init__(self):
        dict.__init__(self)
        self._conf = {}

    def __getitem__(self, k):
        return self._conf.__getitem__(k)

    def __setitem__(self, k, v):
        raise NotImplementedError

    def __repr__(self):
        return repr(self._conf)
