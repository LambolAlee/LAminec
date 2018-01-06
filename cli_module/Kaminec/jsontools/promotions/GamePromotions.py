from string import Template
from collections import namedtuple
from ..LibItem import make_comp_items
from ..system import Rule, getStartCodeTemplate, NATIVEKEY

ORDLIBFORM = "{0}/{1}/{2}/{1}-{2}.jar"
NATIVELIBFORM = "{0}/{1}/{2}/{1}-{2}-{3}.jar"

class MCPromotNormal:
    '''promotion to minecraft 1.12.2 and earlier.'''
    def __init__(self, version):
        self.version = version

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    def initLibs(self, lib_data, conf, include_native=False):
        return make_comp_items(lib_data, conf=conf, include_native=include_native)

    def initMcArgs(self, args_data):
        return Template(args_data)

    def initStartCode(self):
        return Template(getStartCodeTemplate())


class MCPromotForge(MCPromotNormal):
    def __init__(self, version):
        super(MCPromotForge, self).__init__(version)

    #sign:change it into the form which is the same as initlib
    def initForgeLibs(self, forge_lib_data):
        forge_list = []
        for forge_lib in forge_lib_data:
            package, name, version = forge_lib["name"].split(':')
            ord_forge_lib = ORDLIBFORM.format(package.replace('.', '/'), name, version)
            forge_list.append(ord_forge_lib)
        return forge_list

    def initMcArgs(self, args_data):
        return Template(args_data)