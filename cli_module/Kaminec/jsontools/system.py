import re
import platform as pf
from .promotions.LanePromotions import LanePromotionDefault


SYSLIST = {
    'Windows':[
        'windows',
        '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump',
        '-Dos.name=Windows 10',
        '-Dos.version=10.0'], 
    'Darwin':[
        'osx',
        '-XstartOnFirstThread'], 
    'Linux':['linux', '']}

SYSNAME = SYSLIST[pf.system()][0]

SYSVERSION = pf.version()

NATIVEKEY = "natives-{}".format(SYSNAME)

JAVA_PATH = ""

STARTCODETEMPLATE = """
    ${javaw_path} ${jvm_args} ${extra_jvm_args}
    -Djava.library.path=${natives_directory} 
    -Dminecraft.launcher.brand=${launcher_name}
    -cp ${classpath} ${mainClass} ${game_args} ${extra_game_args}"""

def getLane(self, conf_file=None, lane_promotion=LanePromotionDefault):
    return lane_promotion(conf_file)

def getStartCodeTemplate():
    if pf.version() == "10" and SYSNAME == "windows":
        jvm_args = SYSLIST[pf.system()][2:]
    jvm_args = SYSLIST[pf.system()][1]
    return STARTCODETEMPLATE.replace(
        "${jvm_args}", jvm_args)


class Rule:
    def __init__(self, arule, sysname=SYSNAME, sysversion=SYSVERSION):
        self.arule = arule
        self.sysname = sysname
        self.sysversion = sysversion
        self.allow = self.parseRule()

    def parseRule(self):
        return self.assertWhetherAllow()

    def assertWhetherAllow(self):
        if self.arule["action"] == "disallow":
            #Assert Disallow
            allow = (self.sysname != self.arule["os"]["name"])
            return allow
        else:
            #Assert Allow
            return self.assertAllow()

    def assertAllow(self):
        try:
            allow = (self.sysname == self.arule["os"])
        except KeyError:
            allow = True
        else:
            try:
                pattern = self.arule["os"]["version"]
            except KeyError:
                allow = True
            else:
                allow = re.match(pattern, self.sysversion) if pattern else True
        return allow