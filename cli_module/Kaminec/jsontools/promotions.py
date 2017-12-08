import abc

class Promotions(abc.ABCMeta):
    @abc.abstractmethod
    def initLibs(self, lib_data):pass

    @abc.abstractmethod
    def initMcArgs(self, args_data):pass

    @abc.abstractmethod
    def initStartCode(self, args_data):pass

    @abc.abstractproperty
    def version(self):pass


class MCPromotNormal(Promotions):
    '''promotion to minecraft 1.12.2 and earlier.'''
    def initLibs(self, lib_data):
        