class Event:
    CONFIGINIT = "config_init"
    GAMESTART = "game_start"
    DOWNLOAD = "download"
    SCRIPT = "script"

    def __init__(self, kind, *events):
        self.kind = kind

class CompositeEvents:
    def __init__(self, *events):
        self.children = []
        self.add(*events)

    def add(self, event, *events):
        self.children.append(event)
        if events:
            self.children.extend(events)
    
    def __iter__(self):
        return iter(self.children)