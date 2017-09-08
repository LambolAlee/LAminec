import json
from os.path import join, exists
from attrdict import AttrDict

class SelectedVersionNotFoundError(Exception):
    pass

class MaskLane:
    def __init__(self, version, lane_etc, *, mode='default', repo='mojang'):
        self.mode = join(lane_etc, mode+'.json')
        self.version = version
        with open(self.mode, encoding="utf-8") as f:
            self.basicdata = json.load(f, object_hook=AttrDict)
        self.mcpath = self.basicdata.mcpath
        if mode == 'default':
            self.mcpath = join(dirname(lane_etc), '.minecraft')
        if self.basicdata.auto_gen:
            self.autoGen(self.mcpath)
        else:
            self.ordinary(self.basicdata.minecraft)
    
    def autoGen(self, mcpath):
        self.assets_root = join(mcpath, 'assets')
        self.assets_index = join(self.assets_root, 'indexes')
        self.assets_obj = join(self.assets_root, 'objects')
        self.libpath = join(mcpath, 'libraries')
        self.versiondir = join(mcpath, 'versions')
        self.selectedvers = join(self.versiondir, self.version)
        self.gamejar = join(self.selectedvers, self.version+'.jar')

    def ordinary(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        self.selectedvers = join(self.versiondir, self.version)
        self.gamejar = join(self.selectedvers, self.version+'.jar')


class Lane(MaskLane):
    def __init__(self, version, lane_etc, lane_repo, *, mode='default', repo='mojang'):
        super().__init__(version, lane_etc, mode=mode, repo=repo)
        if not exists(self.selectedvers):
            raise SelectedVersionNotFoundError("the chosen verison of minecraft is not found.")
        self.repo = join(lane_repo, repo+'.json')
        with open(self.repo, encoding="utf-8") as f:
            self.repodata = json.load(f, object_hook=AttrDict)
        self.initrepo(self.repodata)

    def initrepo(self, data):
        for key, value in data.items():
            setattr(self, key, value)