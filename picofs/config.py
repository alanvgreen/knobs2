import json
import os

_FNAME = "config.json"


class Config:
    def __init__(self):
        self.data = {}
        self.dirty = False

    def read(self, fname=_FNAME):
        try:
            os.stat(fname)
        except:
            self.write(fname, True)

        with open(fname, "r") as f:
            self.data = json.load(f)

    def reset(self):
        self.data = {}
        self.write(force=True)

    def write(self, fname=_FNAME, force=False):
        print("write")
        if not force and not self.dirty:
            return
        with open(fname, "w") as f:
            self.data = json.dump(self.data, f)
        self.dirty = False

    def get_channels(self):
        """List of 5 channels (0-15 or None)"""
        return self.data.get("channels", [None] * 5)

    def set_channels(self, channels):
        self.data["channels"] = channels
        self.dirty = True


CONFIG = Config()
