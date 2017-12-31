from zipfile import ZipFile
from os.path import join
from collections import namedtuple


tasks = {"lib_task": namedtuple("lib_task", ['path', 'url', 'sha1']),
         "index_task": namedtuple(
            'index_task', ['indexes', 'objects', 'id', 'path', 'url', 'sha1']),
         "maingame_task": namedtuple("maingame_task", ['path', 'url', 'sha1']),
         "obj_task": namedtuple("obj_task", ['path', 'url', 'hash'])}


def extractMe(native_path, nativedir):
    try:
        zipf = ZipFile(native_path, mode='r')
    except FileNotFoundError:
        print("not found %s" % native_path)
    else:
        for i in (k for k in zipf.namelist() if "META-INF" not in k):
            zipf.extract(i, nativedir)


def addParentPath(parent_path, child_path): return join(
    parent_path, child_path)
