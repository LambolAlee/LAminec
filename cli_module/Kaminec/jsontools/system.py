import re
import platform as pf
from shutil import rmtree
from os import walk, remove
from os.path import join
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

JAVA_PATH = "D:\\Program Files\\jre1.8\\bin\\javaw.exe"

STARTCODETEMPLATE = """
    ${javaw_path} ${jvm_args} ${extra_jvm_args}
    -Djava.library.path=${natives_directory} 
    -Dminecraft.launcher.brand=${launcher_name}
    -cp ${classpath} ${mainClass} ${game_args} ${extra_game_args}"""

EXTRA_JVM_SAMPLE = "-XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Xmn128m -Xmx1024m"

def getLane(self, conf_file=None, lane_promotion=LanePromotionDefault):
    return lane_promotion(conf_file)

def getStartCodeTemplate():
    if pf.version() == "10" and SYSNAME == "windows":
        jvm_args = SYSLIST[pf.system()][2:]
    jvm_args = SYSLIST[pf.system()][1]
    return STARTCODETEMPLATE.replace(
        "${jvm_args}", jvm_args)

def removeNativeDir(obj, native_dir):
    try:
        for root, dirs, files in walk(native_dir):
            for f in files:
                remove(join(root, f))
        rmtree(native_dir)
    except:pass
    obj.prepared = False
