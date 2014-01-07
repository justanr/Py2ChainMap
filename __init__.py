"""A backport of ChainMap from Python 3 to Python 2.

See http://hg.python.org/cpython/file/default/Lib/collections/__init__.py#l756 
    for original source code. Everything here is lifted directly from there.
"""

from collections import MutableMapping

class ChainMap(MutableMapping):
    """A ChainMap groups multiple dicts (or other mappings) together
    to create a single, updatable view.

    The underlying mappings are stored in a list. That list is public and can
    be accessed or updated using the *maps* attribute. There is no other state.

    Lookups search the underlying mappings successively until a key is found.
    In contrast, writes, updates and deletions only operate on the first
    mapping.

    """

    def __init__(self, *maps):
        self.maps = list(maps) or [{}]      # always at least one map

    def __missing__(self, key):
        raise KeyError(key)

    def __getitem__(self, key):
        for mapping in self.maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        return self.__missing__(key)

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __len__(self):
        return len(set().union(*self.maps))

    def __iter__(self):
        return iter(set().union(*self.maps))

    def __contains__(self, key):
        return any(key in m for m in self.maps)

    def __bool__(self):
        return any(self.maps)

    # for going backporting recursive_repr as well
    # so a slight deviation by using the ChainMap.parents method
    def __repr__(self):
        return "{0.__class__.__name__}({1})".format(
            self, ', '.join(map(repr, self.parents)))
    
    @classmethod
    def fromkeys(cls, iterable, *args):
        "Create a ChainMap with a single dict created from the iterable"
        return cls(dict.fromkeys(iterable, *args))

    def copy(self):
        "New ChainMap or subclass with a new copy of maps[0] and refs to maps[1:]"
        return self.__class__(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy
    
    def new_child(self, m=None):
        '''New ChainMap followed by all previous maps. If no 
        map is provided an empty dict is used.
        
        '''

        if m is None:
            m = {}

        return self.__class__(m, *self.maps[1:])

    @property
    def parents(self):
        "New ChainMap from maps[1:]"
        return self.__class__(*self.maps[1:])

    def __setitem__(self, key, value):
        self.maps[0][key] = value

    def __delitem__(self, key):
        try:
            del self.maps[0][key]
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    def popitem(self):
        "Remove and return an item pair from maps[0]. Raise KeyError if maps[0] is empty"
        try:
            return self.maps[0].popitem()
        except KeyError:
            raise KeyError("No keys found in the first mapping.")

    def pop(self, key, *args):
        "Remove *key* from maps[0] and return its value. Raise KeyError if *key* not in maps[0]"
        try:
            return self.maps[0].pop(key, *args)
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    def clear(self):
        "Clear maps[0], leaving maps[1:] in tact"
        self.maps[0].clear()


# Recipe taken from the Python3 collections module documentation
class DeepChainMap(ChainMap):
    "Variant of ChainMap that allows direct updates to inner scopes"

    def __setitem__(self, key, value):
        for mapping in self.maps:
            if key in mapping:
                mapping[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        for mapping in self.maps:
            if key in mapping:
                del mapping[key]
                return
        raise KeyError(key)
