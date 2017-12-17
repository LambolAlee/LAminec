import Kaminec.Game as game
from multiprocessing import freeze_support
from Kaminec.jsontools.system import Rule
from time import time

data = "D:\\Learning Pythons\\LAminec2nd\\tmp\\1.11.2.json"

def main():
    start = time()
    mc = game.Game(data)
    a = mc.getLibPath()
    print(a)
    delta = time() - start
#    print(mc.cmd)
    return delta

example = [
    {
        "action": "allow"
    },
    {
        "action": "disallow",
        "os": {
            "name": "osx"
        }
    }
]

example2 = [
    {
        "action": "allow",
        "os": {
            "name": "osx"
        }
    }
]

#def main():
#    rule = Rule(example2)
#    print(rule.allow)

if __name__ == '__main__':
#    print(example2)
    sums = 0
#    for i in range(1000):
#       single = main()
#        sums += single
    print(main())
#    print(sums/1000)
