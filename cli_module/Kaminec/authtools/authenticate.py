import requests
from json import dumps
from ..exceptions import YggdrassilError

AUTH_SERVER = "https://authserver.mojang.com/"
CONTENT_TYPE = "application/json"
HEADERS = {"content-type": CONTENT_TYPE}


def make_requests(endpoint, data):
    req = requests.post(AUTH_SERVER + endpoint, dumps(data),
                        headers=HEADERS, timeout=20)
    return req, check_if_successded(req)


def check_if_successded(req):
    if req.status_code == requests.codes['ok'] or req.status_code == 204:
        return True
    anerror = YggdrassilError(status_code=req.status_code)
    req_json = req.json()
    if 'error' in req_json and 'errorMessage' in req_json:
        message = "[Kaniol.{status_code}] {error}: '{error_message}'"
        message = message.format(status_code=str(req.status_code),
                                 error=req_json["error"],
                                 error_message=req_json["errorMessage"])
        anerror.args = (message,)
        anerror.error = req_json["error"]
        anerror.errormsg = req_json["errorMessage"]
        raise anerror


class Auth2Mc:
    def __init__(self, auth_box, client_token):
        self.auth_box = auth_box
        self.client_token = client_token

    def login(self, password):
        payload = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": self.auth_box.username,
            "password": password,
            "client_token": self.client_token,
            "requestUser": self.auth_box.twitch
        }
        req, res = make_requests('authenticate', payload)
        self.auth_box.update(req.json()["selectedProfile"])
        return (True if res else False)

    def refresh(self):
        req, res = make_requests('refresh',
                            {"accessToken": self.auth_box.token,
                             "clientToken": self.client_token})
        self.auth_box.update(req.json())
        return (True if res else False)

    def validate(self):
        try:
            req, _ = make_requests('validate',
                                {"accessToken": self.auth_box.token,
                                 "clientToken": self.client_token})
        except YggdrassilError:
            return False
        else:
            return True

    def invalidate(self):
        try:
            req, _ = make_requests('invalidate',
                                {"accessToken": self.auth_box.token,
                                 "clientToken": self.client_token})
        except YggdrassilError:
            return False
        else:
            return True

    def sign_out(self, password):
        try:
            req, _ = make_requests('signout',
                                {"username": self.auth_box.username,
                                 "password": password})
        except YggdrassilError:
            return False
        else:
            return True