import functools
from .status import Event

def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        generator = function(*args, **kwargs)
        next(generator)
        return generator
    return wrapper

@coroutine
def conf_init_handler(successor=None):
    while True:
        event, handler = yield
        if event.kind == Event.CONFINIT:
            handler.handle_conf_init()
        elif successor is not None:
            successor.send(event, handler)
        else:
            print("[Kaniol.Warning] config file init failed")

@coroutine
def start_game_handler(successor=None):
    while True:
        event, handler = yield
        if event.kind == Event.GAMESTART:
            handler.handle_game_start()
        elif successor is not None:
            successor.send(event, handler)
        else:
            print("[Kaniol.Warning] start game failed")

@coroutine
def download_handler(successor=None):
     while True:
        event, handler = yield
        if event.kind = Event.DOWNLOAD:
            handler.handle_download()
        elif successor is not None:
            successor.send(event, handler)
        else:
            print("[Kaniol.Warning] download failed")

@coroutine
def script_handler(successor=None):
     while True:
        event, handler = yield
        if event.kind = Event.SCRIPT:
            handler.handle_script()
        elif successor is not None:
            successor.send(event, handler)
        else:
            print("[Kaniol.Warning] run script failed")