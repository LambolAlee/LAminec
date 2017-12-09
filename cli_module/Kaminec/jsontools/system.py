import platform as pf
from .promotions import LanePromotionDefault

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

NATIVEKEY = "natives-{}".format(SYSNAME)

JAVA_PATH = ""

STARTCODETEMPLATE = """
    ${javaw_path} ${jvm_args} ${extra_jvm_args}
    -Djava.library.path=${natives_directory} 
    -Dminecraft.launcher.brand=${launcher_name}
    -cp ${classpath} ${mainClass} ${game_args} ${extra_game_args}"""

def getLane(self, conf_file=None, default=LanePromotionDefault):
    return default(conf_file)

def getStartCodeTemplate():
    if pf.version() == "10" and SYSNAME == "windows":
        jvm_args = SYSLIST[pf.system()][2:]
    jvm_args = SYSLIST[pf.system()][1]
    return STARTCODETEMPLATE.replace(
        "${jvm_args}", jvm_args)