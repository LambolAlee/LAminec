from .jsontools.system import getLane
from .jsontools.promotions.GamePromotions import MCPromotNormal
from .jsontools.promotions.LanePromotions import LanePromotionDefault
from .jsontools.MCjson import GameJsonManager
from os.path import basename, splitext, join

addParentPath = lambda child_path, parent_path: join(parent_path, child_path)

class Game:
    def __init__(self, 
        
        data_path, 
        game_type="vanilla", 
        conf_file=None,
        lane_promot=LanePromotionDefault, 
        game_promot=MCPromotNormal
        ):

        self.data_path = data_path
        self.game_version = splitext(basename(data_path))[0]
        self.lane = getLane(conf_file, lane_promot)
        self.data_parser = GameJsonManager(
            data_path, game_promot(self.game_version), game_type=game_type)

    def getLibPath(self):
        return list((addParentPath(each_lib, self.lane.libpath)
            for each_lib, _ in self.data_parser.lib_list))
    
    @staticmethod
    def extractMe(native_path):
        try:
            zipf = zips(native_path, mode='r')
        except FileNotFoundError:
            pass
        else:
            for i in (k for k in zipf.namelist() if "META-INF" not in k):
                zipf.extract(i, self.lane.nativedir)

    def getNativesExtracted(self):
        for each_native, _ in self.data_parser.native_path:
            self.extractMe(each_native)

    def getInitInPool(self):
        pass