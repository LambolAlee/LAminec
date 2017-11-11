import collections
import json
from tempfile import TemporaryFile
from shutil import copy2
from os.path import basename, splitext

class Config(collections.UserDict):
    def __init__(self, user_json):
        self.user_json = user_json
        self.username = splitext(user_json)[0]
        with open(user_json) as f:
            self.data = json.load(f)
            self._rollback = dict(self.data)

    def save(self):
        with open(self.user_json, 'w') as f:
            try:
                json.dump(self.data, f)
            except OSError:
                print("[Kaniol] Failed to write your changes into the config file.Now rolling back")
                json.dump(self._rollback, f)
                return "RollBack"
            else:
                return "SaveDone"