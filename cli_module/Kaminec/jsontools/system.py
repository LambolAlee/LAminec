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
    def __init__(self, rule_list, sysname=SYSNAME, sysversion=SYSVERSION):
        self.rule_list = rule_list
        self.sysname = sysname
        self.sysversion = sysversion
        self.allow = all(self.parseRule(each_rule) for each_rule in rule_list)

    def parseRule(self, each_rule):
        return self.assertWhetherAllow(each_rule)

    def assertWhetherAllow(self, each_rule):
        if each_rule["action"] == "disallow":
            #Assert Disallow
            allow = (self.sysname != each_rule["os"]["name"])
            return allow
        else:
            #Assert Allow
            return self.assertAllow(each_rule)

    def assertAllow(self, each_rule):
        try:
            allow = (self.sysname == each_rule["os"])
        except KeyError:
            allow = True
        else:
            try:
                pattern = each_rule["os"]["version"]
            except KeyError:
                allow = True
            else:
                allow = re.match(pattern, self.sysversion) if pattern else True
        return allow