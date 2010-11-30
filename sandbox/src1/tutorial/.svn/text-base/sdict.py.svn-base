class SDict(dict):
    '''Dictionary that only accepts case-insensitive string keys'''
    def __init__(self, idict = {}):
        '''If intializing dict is non-null, examine keys'''
        keys = idict.keys()
        values = idict.values()
        for i in range(len(keys)):
            if type(keys[i]) != type(''):
                raise TypeError
            keys[i] = keys[i].lower()
        dict.__init__(self)
        for key, value in zip(keys, values):
            self[key] = value
    def __getitem__(self, key):
        if type(key) != type(''):
            raise TypeError
        return dict.__getitem__(self, key.lower())
    def __setitem__(self, key, value):
        if type(key) != type(''):
            raise TypeError
        dict.__setitem__(self, key.lower(), value)
