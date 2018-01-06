from os.path import basename, join, splitext
from zipfile import ZipFile
from subprocess import check_call, Popen, PIPE, STDOUT

from .jsontools.MCjson import GameJsonManager
from .jsontools.promotions.GamePromotions import MCPromotNormal
from .jsontools.promotions.LanePromotions import LanePromotionDefault
from .jsontools.system import EXTRA_JVM_SAMPLE, JAVA_PATH, getLane, removeNativeDir

addParentPath = lambda parent_path, child_path: join(parent_path, child_path)

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
        self.nativedir = self.initNativeDir()
        self.data_parser = GameJsonManager(
            data_path, game_promot(self.game_version), game_type=game_type)
        self.prepared = False

    def initNativeDir(self):
        return self.lane.initNativeDir()

    def getLibPath(self):
        return self.data_parser.lib_comp.parsePath()

    def getMcArgs(self, auth_box):
        mcargs = self.data_parser.mcargs.substitute(
            auth_player_name=auth_box["name"],
            version_name="\"LaminecR1 1.0.0.0\"",
            game_directory=self.lane.minecraftdir,
            assets_root=self.lane.assets_root,
            asssets_index_name=self.data_parser.assets_name,
            uuid=auth_box["id"], auth_access_token=auth_box["accessToken"],
            user_type=auth_box["user_type"],
            user_properties=auth_box["user_properties"],
            auth_session=auth_box["id"],
            version_type=self.data_parser.version_name
        )
        return mcargs

    def getStartCode(self, auth_box, extra_jvm=EXTRA_JVM_SAMPLE, extra_mcargs=""):
        self.prepared = True
        self.startcode = self.data_parser.startcode_template.substitute(
            javaw_path=JAVA_PATH, extra_jvm_args=extra_jvm,
            natives_directory=self.lane.nativedir,
            launcher_name="Laminec",
            classpath=";".join(self.getLibPath())
            ,mainClass=self.data_parser.mainClass,
            game_args=self.getMcArgs(auth_box),
            extra_mcargs=extra_mcargs
        )

    def start(self):
        if not prepared:
            raise RuntimeError("[Kaniol] Please run getStartCode(...) and initNativeDir() first!")
        with Popen(cmd, stdout=PIPE, stderr=STDOUT) as proc:
            print("***LAMINEC R1 1.0.0.0***")
            print("[Lambol] successfully launching the game...")
            print("[Kaniol] native directory is ", self.nativedir)
            print("*"*80, proc.stdout.read(), sep='\n')
        removeNativeDir(self, self.nativedir)