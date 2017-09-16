import json
from os.path import join, exists
from attrdict import AttrDict
from collections import namedtuple

paths = namedtuple("Paths", 
    ["assets_root",
     "assets_index",
     "assets_obj",
     "libpath",
     "versiondir",
     "selectedvers",
     "gamejar"])

urls = namedtuple("Urls",
    ["gamelist",
     "libprefix",
     "assprefix"])

class SelectedVersionNotFoundError(Exception):
    pass

def Lane(profile, version):
    gamepath = profile["gamepath"]
    assets_root = join(gamepath, "assets")
    assets_index = join(assets_root, "indexes")
    assets_obj = join(assets_root, "objects")
    libpath = join(gamepath, "libraries")
    versiondir = join(gamepath, "versions")
    selectedvers = join(versiondir, version)
    gamejar = join(selectedvers, version+'.jar')

    if not exists(selectedvers):
        raise SelectedVersionNotFoundError("[Kaniol] the chosen version of minecraft is not found.")
    
    urllisrt = profile["urls"]
    gamelist = urllisrt["gamelist"]
    libprefix = urllisrt["libprefix"]
    assprefix = urllisrt["assprefix"]

    path = paths(gamepath,
                 assets_root,
                 assets_index,
                 assets_obj,
                 libpath,
                 versiondir,
                 selectedvers,
                 gamejar)
    url = urls(gamelist,
               libprefix,
               assprefix)
    return path, url
