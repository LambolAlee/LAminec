class ProfileBrokenError(Exception):
    pass

class SelectedVersionNotFoundError(Exception):
    pass

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