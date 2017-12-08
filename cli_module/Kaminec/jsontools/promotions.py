import abc
from string import Template

from .system import Rule, StartCodeTemplate

ord_lib_form = "{0}/{1}/{2}/{1}-{2}.jar"
native_lib_form = "{0}/{1}/{2}/{1}-{2}-{3}.jar"

class Promotions(abc.ABCMeta):
    def __init__(self, version):
        self.version = version

    @abc.abstractmethod
    def initLibs(self, lib_data, native_key):pass

    @abc.abstractmethod
    def initMcArgs(self, args_data):pass

    @abc.abstractmethod
    def initStartCode(self):pass

    @abc.abstractproperty
    def version(self):pass

class PromotionsVersionNotMatchError(NameError):pass

class MCPromotNormal(Promotions):
    '''promotion to minecraft 1.12.2 and earlier.'''
    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    def initLibs(self, lib_data, native_key):
        native_list = [];lib_list = []
        for alib in lib_data:
            package, name, version = alib.split(':')
            if "extract" in alib:
                native_lib = native_lib_form.format(native_key, package.replace('.', '/'), name, version)
                sha1 = alib["downloads"]["classifiers"][native_key]["sha1"]
                try:
                    rule = Rule(alib["rules"])
                except KeyError:
                    pass
                native_list.append((native_lib, sha1, rule))
            ord_lib = ord_lib_form.format(package.replace('.', '/'), name, version)
            sha1 = alib["downloads"]["artifact"]["sha1"]
            try:
                rule = Rule(alib["rules"])
            except KeyError:
                lib_list.append((ord_lib, sha1, None))
            else:
                lib_list.append((ord_lib, sha1, rule))
        return lib_list, native_list

    def initMcArgs(self, args_data):
        return Template(args_data)

    def initStartCode(self):
        return Template(StartCodeTemplate)


class MCPromotSpecial(MCPromotNormal):
    def initLibs(self, lib_data):
        forge_list = []
        for forge_lib in lib_data:
            package, name, version = alib.split(':')
            ord_forge_lib = ord_lib_form.format(package.replace('.', '/'), name, version)
            forge_list.append(ord_forge_lib)
        return forge_list

    def initMcArgs(self, args_data):pass