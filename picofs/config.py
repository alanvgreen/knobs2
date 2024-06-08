import json

_FNAME = "config.json"

class Config:
    def __init__(self):
        self.data = {}
        self.dirty = False

    def read(self, fname=_FNAME):
        with open(fname, "r") as f:
            self.data = json.load(f)

    def reset(self):
        self.dirty = True
        self.data = {}
        self.write()

    def write(self, fname=_FNAME):
        if not self.dirty:
            return
        with open(fname, "w") as f:
            self.data = json.dump(f)
        self.dirty = False

    def get_channels(self):
        """List of 5 channels (0-15 or None)"""
        return self.data.get("channels", [None] * 5)

    def set_channels(self, channels):
        self.data["channels"] = channels
        self.dirty = True


CONFIG = Config()
