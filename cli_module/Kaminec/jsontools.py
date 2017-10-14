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
#from os import name as sysname


#platform = {'nt':'windows', 'posix':'linux', 'osx':'osx'}
nativekey = "natives-{}".format(system().lower())
#namelist = [('libraries', initlib), ('assetIndex', None), ('downloads', None),
#            ('mainClass', None), ('minecraftArguments', None)]


class JsonComp:
    def __init__(self, comp, init=None):
        if init is None:
            init = lambda comp: comp
        self.comp = init(comp)

    def parse(self, key=None, **args):
        if key is None:
            return self.comp
        else:
            return key(self.comp, **args)

class JsonManager:
    def __init__(self, data, namelist=None):
        self.data = data    #[('libraries','initlib'), ...]
        if namelist is None:
            setattr(self,
                    'rawdata',
                    JsonComp(self.data, None))
        else:
            self.init(namelist)

    def init(self, namelist):
        for name, func in namelist:
            setattr(self,
                    name,
                    JsonComp(self.data[name], func))

def initlib(libs):
    natives = []; names = []
    for i in libs:
        i = AttrDict(i)
        if 'natives' in i:
            name = i.downloads.classifiers[nativekey]["path"]
            sha1 = i.downloads.classifiers[nativekey]["sha1"]
            natives.append((name, sha1))
        else:
            name = i.downloads.artifact.path
            sha1 = i.downloads.artifact.sha1
            names.append((name, sha1))
    return (natives, names)

def initassets(assets):
    data = assets['objects']
    return (objname['hash'] 
            for objname in data.values())

def parseLibArgs(liblists, **args):
        alist = []
        natives, names = liblists
        libpath = args["libpath"]
        nativedir = args["nativedir"]
        gamejar = args["gamejar"]

        addPath = lambda path:join(libpath, path)

        def extractme(native_path, nativedir):
            """Extracting the native libraries which are in need of starting Minecraft"""
            zipf = zips(native_path, mode='r')
            for i in (k for k in zipf.namelist() if "META-INF" not in k):
                zipf.extract(i, nativedir)

        for name, _ in names:
            name = addPath(name)
            alist.append(name)
        for native_path, _ in natives:
            native_path = addPath(native_path)
            extractme(native_path, nativedir)

        alist.append(gamejar)
        return alist

def parseLibURLs(liblists, **args):
    tasks = []
    libpath = args["libpath"]
    lib_task = namedtuple("lib_task", ['path', 'url', 'sha1'])
    urlform = "{prefix}{urlpart}"
    for (path, sha1) in chain(*liblists):
        url = urlform.format(prefix=args["libprefix"], urlpart=path)
        path = join(libpath, path)
        tasks.append(lib_task(path, url, sha1))
    return tasks

def parseAssetsIndexURLs(assets, **args):
    index_task = namedtuple('index_task', ['indexes', 'objects', 'id', 'path', 'url', 'sha1'])
    return index_task(args["asset_index_dir"], 
                args["asset_obj_dir"],
                assets.id,
                join(args["asset_index_dir"], assets.id+'.json'),
                assets.url,
                assets.sha1)

def parseGameURLs(maingame, **args):
    maingame_task = namedtuple("maingame_task", ['path', 'url', 'sha1'])
    versiondir = args["versiondir"]
    version = args["version"]
    clientpath = join(versiondir, version+'.jar')
    client_task = maingame_task(clientpath, 
                                maingame.client.url,
                                maingame.client.sha1)
    #server = maingame.server.url, maingame.server.sha1
    return client_task

def parseAssetsURLs(hashes, **args):
    assetslist = []
    hash02 = slice(0, 2)
    obj_task = namedtuple("obj_task", ['path', 'url', 'hash'])
    for objhash in hashes:
        urlhash = objhash[hash02]
        url = "{prefix}{hash02}/{totalhash}".format(
        prefix=args["assprefix"], hash02=urlhash, totalhash=objhash)
        path = join(args["asset_obj_dir"], urlhash)
        assetslist.append(obj_task(path, url, objhash))
    return assetslist

def parseMcArgs(mcArgs, **args):
    mcArgs = Template(mcArgs)
    mcArgs = mcArgs.substitute(
            auth_player_name=args["user_name"],
            version_name= args["version"],
            game_directory="\"{}\"".format(args["gamepath"]),
            assets_root="\"{}\"".format(args["assets_root"]),
            assets_index_name=args["assetsID"],
            auth_uuid=args["uuid"],
            auth_access_token=args["accessToken"],
            user_type=args["gamemode"],
            version_type="\"LAminec AlphaV2.8\"")
    return mcArgs

@contextmanager
def CalJson(javapath, mainclass, nativedir, libpath, mcArgs):
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