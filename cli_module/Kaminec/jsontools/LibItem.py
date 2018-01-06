from itertools import chain
from functools import partial
from collections import UserList
from .system import Rule, NATIVEKEY
from .promotions.ParsePromotion import parseAllLibs
from .promotions.ParsePromotion import CommonLibParser, NativeLibParser


class LibItem:
    def __init__(self, single_lib):
        self.raw = single_lib
        self.parseRule()

    def setParser(self, conf):
        self._parse_promot = eval(
            "{0}LibParser".format(self.type.capitalize())(self, conf))

    def parseRule(self):
        try:
            self.allow = Rule(self.raw["rules"]).allow
        except KeyError:
            self.allow = True

    def init(self, conf):
        self.type, self.name, self.sha1 = parseAllLibs(self.raw)
        self.setParser(conf)
        return self

    def __getattribute__(self, key):
        return getattr(self._parse_promot, key)


class CompLibItem(UserList):
    def __init__(self, *items, *, conf, include_native=False):
        self.conf = conf
        self.include_native = include_native
        if items:
            self.extend(*items)

    def extend(self, first, *items):
        if self.include_native: 
            self.data.extend(i.init(self.conf) for i in chain((first, ), items) if i.allow)
        else:
            self.data.extend(i.init(self.conf) for i in chain((first, ), items))

    def append(self, first):
        if self.include_native:
            self.data.append(first.init(self.conf) if i.allow)
        else:
            self.data.append(first.init(self.conf))

    def _applyForEachItem(self, key):
        def wrapperedParser(*args):
            return [getattr(i, key)(*args) for i in self]
        return wrapperedParser

    def __getattribute__(self, key):
        return self._applyForEachItem(key)


def make_single_item(single_lib):
    return LibItem(single_lib)


def make_comp_items(liblist, conf, include_native=False):
    comp_items = CompLibItem(conf=conf, include_native=include_native)
    for i in liblist:
        comp_items.append(make_single_item(i))
    return comp_items
