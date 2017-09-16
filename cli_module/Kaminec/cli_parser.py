import argparse


def initparser():
    parser = argparse.ArgumentParser(prog="laminec", description="This is a minecraft laucher written in python")

    subparsers = parser.add_subparsers(title="util commands", description="more detailed commands")

    start = subparsers.add_parser("start", help="start the game")
    start.add_argument("game_version", const="last", nargs='?', default="last")
    start.add_argument('-m', '--mojang', dest="mode", action="store_const", default="Legacy", const="mojang")
    start.add_argument('-p', '--password')
    start.add_argument('-u', '--user-name', dest="name", default='steve')

    profinit = subparsers.add_parser("init", help="init the profile")
    profinit.add_argument("rootpath", const=".", nargs='?', default=".")
    profinit.add_argument("gamepath", const="./minecraft", nargs='?', default="./minecraft")


    fetch = subparsers.add_parser("fetch", help="download your games")
    fetch.add_argument('-v', "--game-version", default="latest")

    return parser


if __name__ == '__main__':
    args = parser.parse_args()
    print(args)