from ...util import addParentPath, extractMe, tasks

ORDLIBFORM = "{0}/{1}/{2}/{1}-{2}.jar"
NATIVELIBFORM = "{0}/{1}/{2}/{1}-{2}-{3}.jar"


def parseAllLibs(single_lib):
    package, name, version = single_lib["name"].split(':')
    if "extract" in single_lib:
        lib_type = "native"
        name = NATIVELIBFORM.format(
            package.replace('.', '/'), name, version, NATIVEKEY)
        sha1 = single_lib["downloads"]["classifiers"][NATIVEKEY]["sha1"]
    else:
        lib_type = "common"
        name = ORDLIBFORM.format(
            package.replace('.', '/'), name, version)
        sha1 = single_lib["downloads"]["artifact"]["sha1"]
    return lib_type, name, sha1


class CommonLibParser:
    def __init__(self, parsed_single_lib, lane_conf):
        self.lib = parsed_single_lib
        self.conf = lane_conf

    def parsePath(self):
        return addParentPath(self.conf.lane["libdir"], self.lib.name)

    def parseUrl(self):
        lib_url = "{prefix}{urlpart}".format(
            prefix=self.conf.url["library"], urlpart=path)
        return tasks["lib_task"](self.parsePath(), lib_url, self.lib.sha1)


class NativeLibParser(CommonLibParser):
    def parsePath(self):
        extractMe(addParentPath(self.conf.lane["libdir"], self.lib.name), 
            self.conf.lane["nativedir"])
