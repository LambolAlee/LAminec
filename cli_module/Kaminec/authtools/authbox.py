import json
from collections import UserDict


class AuthBox(UserDict):
    def __init__(self, config_file):
        self.config_file = config_file
        self._loadConfig()

    def _loadConfig(self):
        with open(self.config_file, encoding="utf-8") as f:
            self.raw_data = json.load(f)
            self.data = self.raw_data["auth-box-settings"]

    def update(self, **newResp):
        super(AuthBox, self).update(**newResp)
        self.save()

    def save(self):
        self.raw_data["auth-box-settings"].update(self)
        with open(self.config_file, 'w', encoding="utf-8") as f:
            json.dump(self.raw_data, f, indent="\t")

    def reload(self):
        self._loadConfig()

    def login(self):pass

    def refresh(self):pass

    def sign_out(self):pass

#I don't know how to  prevent user to change the value of self.data