from collections import UserDict
from json import load, dump
from uuid import uuid1 as ranuid
from os.path import join
from tempfile import mkdtemp
from shutil import copy2
from os import remove
from functools import wraps


class ProfileBrokenError(Exception):
    pass


class Profile(UserDict):
    def __init__(self, data_file):
        try:
            with open(data_file) as f:
                self.data = load(f)
        except OSError:
            raise ProfileBrokenError("[Kaniol] The given json file may be broken.")
        self.data_file = data_file

    @backup
    def save(self, name, uid, gversion, token="", mode='Legacy'):
        print("Saving profile lab.json ...")
        self.savelastUser(name, uid, gversion, token="", mode='Legacy')
        with open(self.data_file, 'w') as f:
            dump(self.data, f)
        return True

    def parseLastUser(self):
        lastUser = self.data["lastUser"]
        if not lastUser:
            return False, None
        else:
            lastUser = lastUser.split('+')
            return True, lastUser

    def savelastUser(self, name, uid, gversion, token="", mode='Legacy'):
        lastUser = '+'.join((mode, name, uid, token, gversion))
        self["lastUser"] = lastUser
        return


def makeProfile(adir, javapath, rootpath, gamepath):
    INNER = {
    "java":javapath,
    "rootpath":rootpath,
    "gamepath":gamepath,
    "lastUser":"",
    "client_token":uuid1(),
    "Legacy":{},
    "mojang":{},
    "preloadScripts":[],
    "urls":{
        "gamelist":"https://launchermeta.mojang.com/mc/game/version_manifest.json",
        "libprefix":"https://libraries.minecraft.net/",
        "assprefix":"https://resources.download.minecraft.net/"
            }
    }
    with open(join(adir, "lab2.json"), 'w') as f:
        dump(INNER, f)
    return

def backup(func):
    @wraps(func)
    def decration(instance):
        with mkdtemp() as dtmp:
            backf = copy2(instance.data_file, dtmp)
            try:
                res = func(instance)
            except OSError:
                print("[Kaniol] Saving porfile failed.Now trying to restore it.")
                remove(instance.data_file)
                copy2(backf, instance.data_file)
                res = False
        return res
    return decration