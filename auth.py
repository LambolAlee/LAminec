import requests
import json, sys
from attrdict import AttrDict


class LoginFailedError(Exception):
    pass

class Auth:
    def __init__(self, username, password):
        self.data = {"agent":{"name":"Minecraft", "version":1}, "username":'', "password":'', "requestUser": False}
        self.data["username"]=username
        self.data["password"]=password
        self.data = json.dumps(self.data)
        self.yggdrasil = "https://authserver.mojang.com/authenticate"
        self.headers = {"Content-Type":"application/json"}

    def login(self):
        self.mcreq = requests.post(self.yggdrasil, self.data, headers=self.headers, timeout=20)
        self.mcresp = AttrDict(self.mcreq.json())
        try:
            self.mcreq.raise_for_status()
        except requests.exceptions.HTTPError:
            error = self.mcresp.error
            errormsg = self.mcresp.errorMessage
            raise LoginFailedError(error, errormsg)
        return self.mcresp.accessToken, self.mcresp.selectedProfile.id, self.mcresp.selectedProfile.name

#    def save(self):
#        with open('test.json', 'w') as f:
#            json.dump(self.mcresp, f)