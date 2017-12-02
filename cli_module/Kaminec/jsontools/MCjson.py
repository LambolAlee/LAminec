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
        self.lib_list, self.native_list = self.promot.initLibs(self.data["libraries"])

    def initMcArgs(self):
        self.mcargs = self.promot.initMcArgs(self.data.get("minecraftArguments", self.data["arguments"]["game"]))

    def initStartCode(self):
        self.startcode_template = self.promot.initStartCode(self.data.get("arguments"))

    def initOtherGameInfo(self):
        self.version_name = self.data["id"]
        self.assets_name = self.data["assets"]


class ForgeJsonManager(VanillaJsonManager):
    def __init__(self, data_path, promot):
        '''inherit from VanillaJsonManager to process the forge version'''
        with open(data_path, encoding="utf-8") as f:
            self.forge_data = json.load(f)
        self.forge_data_path = data_path

        self.inherit(data_path, promot)

    def inherit(self, data_path, promot):
        '''process the inheriting relationship'''
        parent_data_path = data_path.replace(self.forge_data["id"], self.forge_data["inheritsFrom"])
        super(ForgeJsonManager, self).__init__(parent_data_path, promot)
        self.fitProperties()

    def fitProperties(self):
        '''making the class properties fit in forge version'''
        self.mcargs = self.forge_data["minecraftArguments"]
        self.version_name = self.forge_data["id"]
        self.lib_list.extand(self.promot.initLibs(self.forge_data["libraries"]))


def GameJsonManager(data_path, promot, game_type="vanilla"):
    '''this is a factory function to instantial the VanillaJsonManager or ForgeJsonManager'''
    if not game_type in ["vanilla", "forge"]:
        raise TypeError("[Kaniol] This game type is invalid.")
    else:
        return exec("{0}JsonManager({1}, {2})".format(game_type.capitalize(), data_path, promot))