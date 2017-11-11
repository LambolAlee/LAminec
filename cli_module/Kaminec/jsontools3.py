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
from .exceptions import MojangInformationLackError
#from tempfile import mkdtemp


#LIBINIT = ["libraries", "assetIndex", "downloads", "mainClass", "minecraftArguments"]
#FORGEINIT = ["mainClass", "minecraftArguments", "jar", "libraries", "inheritsFrom", "id"]
nativekey = "natives-{}".format(system().lower())
lib_names = 0
native_names = 1


class GameJsonManager:
    def __init__(self, fjson):
        self.fjson = fjson
        with open(self.fjson) as f:
            self.data = load(f)
        if "inheritsFrom" in self.data:
            self.inheritsFrom_json = self.fjson.replace(
                self.data["id"], self.data["inheritsFrom"])
            with open(self.inheritsFrom_json) as f:
                self.vanilla_data = load(f)
    
    def vanillaParse(self, vanilla_libs):
        natives = []; names = []
        for i in vanilla_libs:
            i = AttrDict(i)
            if 'natives' in i:
                name = i.downloads.classifiers[nativekey]["path"]
                sha1 = i.downloads.classifiers[nativekey]["sha1"]
                natives.append((name, sha1))
            else:
                name = i.downloads.artifact.path
                sha1 = i.downloads.artifact.sha1
                names.append((name, sha1))
        return natives, names

    def forgeParse(self, forge_libs):
        if forge_libs is None:
            return None
        self.names = []
        for i in forge_libs:
            i = AttrDict(i)
            name = i.name.split(':')
            name[0] = name[0].replace('.', '/')
            name.append(name[-2] + '-' + name[-1] + '.jar')
            self.names.append('/'.join(name))
        return self.names

    def getLibrariesList(self, vanilla, forge=None):
        vanilla_list = self.vanillaParse(vanilla)
        forge_list = self.forgeParse(forge)
        return namedtuple("liblist", "vanilla forge")(vanilla_list, forge_list)

    def __call__(self, conf, nativedir):
        if "inheritsFrom" in self.data:
            vanilla_libs = self.vanilla_data["libraries"]
            forge_libs = self.data["libraries"]
            listlibs = self.getLibrariesList(vanilla_libs, forge_libs)
            return GameJsonHandler(
                self.vanilla_data, conf, liblist, nativedir, 
                vanilla_fjson=self.inheritsFrom_json,
                forge_fjson=self.fjson,
                forge_data=self.data)
        else:
            vanilla_libs = self.data["libraries"]
            forge_libs = None
            listlibs = self.getLibrariesList(vanilla_libs, forge_libs)
            return GameJsonHandler(
                self.data, conf, liblist, nativedir,
                vanilla_fjson=self.fjson)


class GameJsonHandler:
    def __init__(self, data, conf, liblist, nativedir, **extra_args):
        self.data = data
        self.conf = conf
        self.liblist = liblist
        self.nativedir = nativedir
        self.extra = extra_args
        self.vanill_fjson = extra_args["vanilla_fjson"]
        self.forge_data = extra_args["forge_data"] if "forge_data" in extra_args else None
        self.forge_fjson = extra_args["forge_fjson"] if "forge_fjson" in extra_args else None
        self.extra = extra_args

    def getLibs(self):
        paths = ""
        addParentPath = lambda path:join(self.conf["libpath"], path)
        
        def extractme(native_path):
            """Extracting the native libraries which are in need of starting Minecraft"""
            try:
                zipf = zips(native_path, mode='r')
            except FileNotFoundError:
                pass
            else:
                for i in (k for k in zipf.namelist() if "META-INF" not in k):
                    zipf.extract(i, self.nativedir)

        if not self.liblist.forge is None:
            gamejar = self.forge_fjson.replace(
                self.forge_data["id"], 
                self.forge_data["jar"]).replace(
                '.json', '.jar')
            for name in self.liblist.forge:
                paths += (addParentPath(name) + ";")
        else:
            gamejar = self.vanilla_fjson.replace(".json", ".jar")
        
        for native, _ in self.liblist.vanilla[native_names]:
            extractme(addParentPath(native))
        for name, _ in self.liblist.vanilla[lib_names]:
            paths += (addParentPath(name) + ";")
        

        paths += gamejar
        return paths

    def getMcArgs(self, Legacy=True, uuid=None, accessToken=None):
        if self.forge_data is None:
            args = self.data["minecraftArguments"]
            version = self.data["id"]
        else:
            args = self.forge_data["minecraftArguments"]
            version = self.forge_data["id"]
        if Legacy:
            accessToken = uuid = self.conf["uuid"]
            user_type = "Legacy"
        else:
            if uuid is None or accessToken is None:
                raise MojangInformationLackError(
                    "[Kaniol] The game cant start because of the lack of your mojang information!")
            else:
                user_type = "mojang"       
        args = args.replace("${auth_player_name}", self.conf["auth_player_name"])\
                   .replace("${version_name}", version)\
                   .replace("${game_directory}", self.conf["game_directory"])\
                   .replace("${assets_root}", self.conf["assets_root"])\
                   .replace("${auth_uuid}", uuid)\
                   .replace("${auth_access_token}", accessToken)\
                   .replace("${user_type}", user_type)\
                   .replace("${version_type}", "\"LAminec R1 1.0.0.0\"")
        return args

    @contextmanager
    def CalJson(javapath, Legacy=True, uuid=None, accessToken=None):
        if self.forge_data is None:
            mainClass = self.data["mainClass"]
        else:
            mainClass = self.forge_data["mainClass"]
        args = self.getMcArgs(Legacy, uuid, accessToken)
        command = javapath \
            + "-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump "\
            + "-XX:+UseG1GC "\
            + "-XX:-UseAdaptiveSizePolicy "\
            + "-XX:-OmitStackTraceInFastThrow "\
            + "-Xmn128m -Xmx1024m "\
            + "-Djava.library.path={} ".format(self.nativedir)\
            + "-Dfml.ignoreInvalidMinecraftCertificates=true "\
            + "-Dfml.ignorePatchDiscrepancies=true "\
            + "-cp {} {} {} --height 480 --width 854".format(self.getLibs, mainClass, args)
        try:
            yield command
        finally:
            print(self.nativedir)
            try:
            for root, dirs, files in walk(self.nativedir):
                for f in files:
                    remove(join(root, f))
            rmtree(self.nativedir)
        except:pass

    def getLibUrls(self):
        tasks = []
        libpath = self.conf["libpath"]
        lib_task = namedtuple("lib_task", ['path', 'url', 'sha1'])
        urlform = "{prefix}{urlpart}"
        for (path, sha1) in self.liblists.vanilla:
            url = urlform.format(prefix=self.conf["libprefix"], urlpart=path)
            path = join(libpath, path)
            tasks.append(lib_task(path, url, sha1))
        if self.liblist.forge is not None:
            for path in self.liblist.forge:
                #the forge website is waited to be proved
                url = urlform.format(prefix=self.conf["libprefix"], urlpart=path)
                path = join(libpath, path)
                tasks.append(lib_task(path, url, None))
        return tasks

    def getAssetsIndexUrls(self):
        index_task = namedtuple('index_task', ['indexes', 'objects', 'id', 'path', 'url', 'sha1'])
        return index_task(
                self.conf["asset_index_dir"], 
                self.conf["asset_obj_dir"],
                self.data["assets"],
                join(self.conf["assets_index_dir"], self.data["assets"] + ".json"),
                self.data["assetIndex"]["url"],
                self.data["assetIndex"]["sha1"])

    def getGameUrls(self):
        maingame_task = namedtuple("maingame_task", ['path', 'url', 'sha1'])
        if self.forge_data is None:
            version = self.data["id"]
        else:
            version = self.forge_data["id"]
        versiondir = self.conf["versiondir"]
        clientpath = join(versiondir, version+'.jar')
        client_task = maingame_task(clientpath, 
                                self.data["downloads"]["client"]["url"],
                                self.data["downloads"]["client"]["sha1"])
        #server = maingame.server.url, maingame.server.sha1
        return client_task