from zipfile import ZipFile as zips
from collections import namedtuple
from os.path import join, abspath
from attrdict import AttrDict
from itertools import chain
from shutil import rmtree
from os import walk, remove
from string import Template
from contextlib import contextmanager
from platform import system
from json import load
#from tempfile import mkdtemp

#LIBINIT = ["libraries", "assetIndex", "downloads", "mainClass", "minecraftArguments"]
#FORGEINIT = ["mainClass", "minecraftArguments", "jar", "libraries", "inheritsFrom", "id"]
nativekey = "natives-{}".format(system().lower())


class VanillaJsonManager:
    def __init__(self, vanilla_json):
        self.data = JsonHandler(vanilla_json)
        self.gamejar = vanilla_json.replace(".json", ".jar")

    def processRawDatas(self, libs):
        natives = []; names = []
        for i in libs:
            i = AttrDict(i)
            if 'natives' in i:
                print(nativekey in i.downloads.classifiers)
                name = i.downloads.classifiers[nativekey]["path"]
                sha1 = i.downloads.classifiers[nativekey]["sha1"]
                natives.append((name, sha1))
            else:
                name = i.downloads.artifact.path
                sha1 = i.downloads.artifact.sha1
                names.append((name, sha1))
        self.libs = namedtuple('libs', 'natives names')(natives, names)
        return self.libs

    def parselibs(self, libpath, nativedir, gamejar="default"):
        vanilla_list = []
        natives, names = self.processRawDatas(self.data.libraries)

        addParentPath = lambda path:join(libpath, path)

        def extractme(native_path, nativedir):
            """Extracting the native libraries which are in need of starting Minecraft"""
            try:
                zipf = zips(native_path, mode='r')
            except FileNotFoundError:
                pass
            else:
                for i in (k for k in zipf.namelist() if "META-INF" not in k):
                    zipf.extract(i, nativedir)

        for name, _ in names:
            vanilla_list.append(addParentPath(name))
        for native_path, _ in natives:
            extractme(addParentPath(native_path), nativedir)

        if gamejar == "default":
            gamejar = self.gamejar
        vanilla_list.append(gamejar)
        return ";".join(vanilla_list)


class ForgeJsonManager(VanillaJsonManager):
    def __init__(self, forge_json):
        self.forge_data = JsonHandler(forge_json)
        self.gamejar = forge_json.replace(
            self.forge_data.id, 
            self.forge_data.jar)\
           .replace('.json', '.jar')
        self.inheritsFrom_json = forge_json.replace(
            self.forge_data.id, self.forge_data.inheritsFrom)
        super().__init__(self.inheritsFrom_json)

    def processrawdatas(self, libs):
        self.libs = []
        for i in libs:
            i = AttrDict(i)
            name = i.name.split(':')
            name[0] = name[0].replace('.', '/')
            name.append(name[-2] + '-' + name[-1] + '.jar')
            self.libs.append('/'.join(name))
        return self.libs

    def parselibs(self, libpath, nativedir):
        forge_list = []
        addParentPath = lambda path:join(libpath, path)
        for name in self.processrawdatas(self.forge_data.libraries):
            name  = addParentPath(name)
            forge_list.append(name)
        forge_list = ";".join(forge_list)
        vanilla_list = super().parselibs(libpath, nativedir, self.gamejar)
        final_list = forge_list + ";" + vanilla_list
        return final_list


def JsonHandler(jsonfile):
    with open(jsonfile) as f:
        data = load(f)
    handle = namedtuple("JsonHandler", data.keys())(*data.values())
    return handle

def genMcArgs(jsm , user_name, gamepath, assets_root, uuid, accessToken=None, gamemode="Legacy"):
        if gamemode == "Legacy":
            accessToken = uuid
        if isinstance(jsm, ForgeJsonManager):
            version = jsm.forge_data.id
            minecraftArguments = jsm.forge_data.minecraftArguments
        else:
            version = jsm.data.id
            minecraftArguments = jsm.data.minecraftArguments
        mcArgs = Template(minecraftArguments).substitute(
                auth_player_name=user_name,
                version_name=version,
                game_directory="\"{}\"".format(gamepath),
                assets_root="\"{}\"".format(assets_root),
                assets_index_name=jsm.data.assets,
                auth_uuid=uuid,
                auth_access_token=accessToken,
                user_type=gamemode,
                version_type="\"LAminec AlphaV3K\"")
        return mcArgs

@contextmanager
def CalJson(javapath, mainclass, libpath, mcArgs, nativedir):
    command = javapath \
            + "-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump "\
            + "-XX:+UseG1GC "\
            + "-XX:-UseAdaptiveSizePolicy "\
            + "-XX:-OmitStackTraceInFastThrow "\
            + "-Xmn128m -Xmx1024m "\
            + "-Djava.library.path={} ".format(nativedir)\
            + "-Dfml.ignoreInvalidMinecraftCertificates=true "\
            + "-Dfml.ignorePatchDiscrepancies=true "\
            + "-cp {} {} {} --height 480 --width 854".format(libpath, mainclass, mcArgs)
    try:
        yield command
    finally:
        try:
            for root, dirs, files in walk(nativedir):
                for f in files:
                    remove(join(root, f))
            rmtree(nativedir)
        except:pass