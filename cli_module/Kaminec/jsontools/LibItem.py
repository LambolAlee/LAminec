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
        self.extend(*items, conf=conf, include_native=include_native)

    def extend(self, first, *items, *, conf, include_native=False):
        if include_native: 
            self.extend(i.init(conf) for i in chain((first, ), items) if not i.allow)
        else:
            self.data.extend(i.init(conf) for i in chain((first, ), items))