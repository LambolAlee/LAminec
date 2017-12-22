from tempfile import mkdtemp

class LanePromotionDefault:
    def __init__(self, conf_file):
        self.initPaths()

    def initPaths(self):
        self.libdir = "F:\\mine_for_test\\.minecraft\\libraries"
        self.nativedir = "C:\\Users\\Administrator\\Desktop\\tmp\\natives"

    def initNativeDir(self):
        return mkdtemp()