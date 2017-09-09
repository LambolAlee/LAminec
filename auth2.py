import requests
import json, sys
from attrdict import AttrDict
from collections import namedtuple


#: The base url for Yggdrassil requests
AUTH_SERVER = "https://authserver.mojang.com/"
CONTENT_TYPE = "application/json"
HEADERS = {"content-type": CONTENT_TYPE}
Profile = namedtuple("Profile", 'profile, twitch')


def make_requests(endpoint, data):
    req = requests.post(AUTH_SERVER + endpoint, json.dumps(data), 
        headers=HEADERS, timeout=20)
    check_if_failed(req)
    return req

def check_if_failed(req):
    if res.status_code == requests.codes['ok'] or res.status_code == 204:
        return None
    anerror = YggdrassilError(status_code=req.status_code)
    req_json = req.json()
    if 'error' in req_json and 'errorMessage' in req_json:
        message = "[Kaniol {status_code}] {error}: '{error_message}'"
        message = message.format(status_code=str(req.status_code),
                                 error=req_json["error"],
                                 error_message=req_json["errorMessage"])
        anerror.args = (message,)
        anerror.error = req_json["error"]
        anerror.errormsg = req_json["errorMessage"]
        raise anerror

class YggdrassilError(Exception):
    error = None
    errormsg = None
    status_code = None
    def __init__(self, error=None, errormsg=None, status_code=None):
        super(YggdrassilError, self).__init__(errormsg)
        self.error = error
        self.errormsg = errormsg
        self.status_code = status_code

class ClientTokenNotMatchedError(Exception):
    pass


class Auth2:
    def __init__(self, username=None, access_token=None, client_token=None, *, twitch=False):
        self.username = username
        self.access_token = access_token
        self.client_token = client_token
        self.twitch = twitch

    def login(self, username, password, client_token):
        payload = {
                    "agent":{
                              "name":"Minecraft", 
                              "version":1
                            }, 
                    "username":username, 
                    "password":password, 
                    "client_token":client_token,
                    "requestUser": self.twitch
                  }
        req = make_requests('authenticate', payload)
        resp = AttrDict(req.json())
        self.username = username
        self.access_token = resp.accessToken
        if client_token != resp.clientToken:
            msg = "The client you given[{client}] != [{get_client}]"
            msg.format(client=client_token, get_client=resp.clientToken)
            raise ClientTokenNotMatchedError(msg)
        else:
            self.client_token = resp.clientToken
        try:
            profile = AttrDict(resp.selectedProfile)
            twitch = AttrDict(resp.user)
        except KeyError:
            self.prof = Profile(profile, None)
        else:
            self.prof = Profile(profile, twitch)
        return True

    def refresh(self):
        req = make_requests('refresh', 
            {"accessToken":self.access_token,
            "clientToken":self.client_token})
        resp = AttrDict(req.json())
        self.access_token = resp.accessToken
        self.client_token = resp.clientToken
        return True

    def validate(self):
        try:
            req = make_requests('validate', 
                {"accessToken":self.access_token,
                "clientToken":self.client_token})
        except YggdrassilError:
            return False
        else:
            return True


    def invalidate(self):
        try:
            req = make_requests('invalidate', 
                {"accessToken":self.access_token,
                "clientToken":self.client_token})
        except YggdrassilError:
            return False
        else:
            return True

    def sign_out(self, username, password):
        req = make_requests('signout',
            {"username":self.username,
             "password":password})
        return True