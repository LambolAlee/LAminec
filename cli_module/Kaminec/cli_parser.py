import argparse
from .status import Event, CompositeEvents


class BasicAction(argparse.Action):
    _field = None
    def __init__(self, option_strings, dest, **kwargs):
        super(BasicAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if hasattr(namespace, "kinds"):
            namespace.kinds.add(Event(self._field))
        else:
            kinds = CompositeEvents(Event(self._field))
            setattr(namespace, "kinds", kinds)

class ConfigAction(BasicAction):
    _field = "config_init"

class GameStartAction(BasicAction):
    _field = "game_start"

class DownloadAction(BasicAction):
    _field = "download"

class ScriptAction(BasicAction):
    _field = "script"


def initparser():
    parser = argparse.ArgumentParser(prog="laminec", description="This is a minecraft laucher written in python")

    subparsers = parser.add_subparsers(title="util commands", description="more detailed commands")

    start = subparsers.add_parser("start", help="start the game")
    start.add_argument("game_version", const="last", nargs='?', default="last", action=GameStartAction)
    start.add_argument('-m', '--mojang', dest="mode", action="store_const", default="Legacy", const="mojang")
    start.add_argument('-p', '--password')
    start.add_argument('-u', '--user-name', dest="name", default='steve')

    profinit = subparsers.add_parser("init", help="init the profile")
    profinit.add_argument("rootpath", const=".", nargs='?', default=".", action=ConfigAction)
    profinit.add_argument("gamepath", const="./minecraft", nargs='?', default="./minecraft")


    fetch = subparsers.add_parser("fetch", help="download your games")
    fetch.add_argument('-v', "--game-version", default="latest", action=DownloadAction)

    return parser


if __name__ == '__main__':
    args = initparser().parse_args()
    print(args)
    for i in args.kinds:
        print(i.kind)