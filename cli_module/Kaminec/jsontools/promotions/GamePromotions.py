import abc
from string import Template
from collections import namedtuple

from .system import Rule, getStartCodeTemplate, NATIVEKEY

ORDLIBFORM = "{0}/{1}/{2}/{1}-{2}.jar"
NATIVELIBFORM = "{0}/{1}/{2}/{1}-{2}-{3}.jar"

class Promotions(abc.ABCMeta):
    def __init__(self, version):
        self.version = version

    @abc.abstractmethod
    def initLibs(self, lib_data):pass

    @abc.abstractmethod
    def initMcArgs(self, args_data):pass

    @abc.abstractmethod
    def initStartCode(self):pass

    @abc.abstractproperty
    def version(self):pass


class MCPromotNormal(Promotions):
    '''promotion to minecraft 1.12.2 and earlier.'''
    def __init__(self, version):
        self.version = version

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    def initLibs(self, lib_data):
        libs = {"lib_list":[], "native_list":[]}
        for alib in lib_data:
            package, name, version = alib.split(':')
            *tuplelib, which_list, allow = self.parseSingleLib(alib, package, name, version, 
                NATIVEKEY if "extract" in alib else None)
            if not allow:
                continue
            else:
                libs[which_list].append(tuplelib)
        return libs.values()

    def initMcArgs(self, args_data):
        return Template(args_data)

    def initStartCode(self):
        return Template(getStartCodeTemplate())

    @staticmethod
    def parseSingleLib(alib, package, name, version, native_key=None):
        if native_key is None:
            which_list = "native_list"
            lib = NATIVELIBFORM.format(native_key, package.replace('.', '/'), name, version)
            sha1 = alib["downloads"]["classifiers"][native_key]["sha1"]
        else:
            which_list = "lib_list"
            lib = ORDLIBFORM.format(package.replace('.', '/'), name, version)
            sha1 = alib["downloads"]["artifact"]["sha1"]
        try:
            allow = Rule(alib["rules"]).allow
        except KeyError:
            allow = True
        return (lib, sha1, which_list, allow)


class MCPromotForge(MCPromotNormal):
    def __init__(self, version):
        super(MCPromotForge, self).__init__(version)

    def initForgeLibs(self, forge_lib_data):
        forge_list = []
        for forge_lib in lib_data:
            package, name, version = alib.split(':')
            ord_forge_lib = ORDLIBFORM.format(package.replace('.', '/'), name, version)
            forge_list.append(ord_forge_lib)
        return forge_list

    def initMcArgs(self, args_data):
        return Template(args_data)