import json


class VanillaJsonManager:
    def __init__(self, data_path, promot):
        '''Init the Vanilla json data and select the useful parts out of raw data'''
        with open(data_path, encoding="utf-8") as f:
            self.data = json.load(f)
        self.vanilla_data_path = data_path
        self.promot = promot

        self.initLibs()
        self.initMcArgs()
        self.initOtherGameInfo()
        self.initStartCode()
    #Initial methods defined here
    def initLibs(self):
        self.native_list, self.lib_list = self.promot.initLibs(self.data["libraries"])

    def initMcArgs(self):
        self.mcargs = self.promot.initMcArgs(self.data["minecraftArguments"])
#       self.data["arguments"]["game"])
    def initStartCode(self):
        self.startcode_template = self.promot.initStartCode()

    def initOtherGameInfo(self):
        self.gamejar = self.vanilla_data_path.replace(".json", ".jar")
        self.version_name = self.data["id"]
        self.assets_name = self.data["assets"]
        self.mainClass = self.data["mainClass"]
        self.launcherversion = self.data["minimumLauncherVersion"]


class ForgeJsonManager(VanillaJsonManager):
    def __init__(self, data_path, promot):
        '''inherit from VanillaJsonManager to process the forge version'''
        with open(data_path, encoding="utf-8") as f:
            self.forge_data = json.load(f)
        self.forge_data_path = data_path

        self.inherit(data_path, promot)

    def inherit(self, data_path, promot):
        '''process the inheriting relationship'''
        parent_data_path = "{vanilla}.json".format(
            vanilla=self.forge_data["inheritsFrom"])
        super(ForgeJsonManager, self).__init__(parent_data_path, promot)
        self.gamejar = parent_data_path.replace(".json", ".jar")
        self.fitProperties()

    def fitProperties(self):
        '''making the class properties fit in forge version'''
        self.mcargs = self.promot.initMcArgs(self.forge_data["minecraftArguments"])
        self.version_name = self.forge_data["id"]
        self.mainClass = self.forge_data["mainClass"]
        self.lib_list.extend(self.promot.initForgeLibs(self.forge_data["libraries"]))


def GameJsonManager(data_path, promot, game_type="vanilla"):
    '''this is a factory function to instantial the VanillaJsonManager or ForgeJsonManager'''
    if not game_type in ("vanilla", "forge"):
        raise TypeError("[Kaniol] This game type is invalid.")
    else:
        return eval("{0}JsonManager".format(game_type.capitalize()))(data_path, promot)