import json
import os

_FNAME = "cfg.json"


class Config:
    def __init__(self, fname):
        self._data = None
        self._dirty = False
        self._fname = fname
        self.maybe_read()

    def maybe_read(self):
        if self._data is not None:
            return
        try:
            os.stat(_FNAME)
        except:
            self._data = {}
            return

        print(f"reading config from {self._fname}")
        with open(self._fname, "r") as f:
            self._data = json.load(f) or {}

    def reset(self):
        self._data = {}
        self.write(force=True)

    def write(self, force=False):
        do_it = self._dirty or force
        if not do_it:
            return

        print(f"writing config to {self._fname}")
        with open(self._fname, "w") as f:
            json.dump(self._data, f)
        self._dirty = False

    def get_channels(self):
        """List of 5 channels (0-15), the first four of which are unique"""
        d = self._data.setdefault("channels", [0, 1, 2, 3, 0])
        return d

    def set_channel(self, group_idx, new_value):
        # Save old value and set new value
        clist = self.get_channels()
        old_value = clist[group_idx]
        clist[group_idx] = new_value
        self._dirty = True

        # For the groups that must be unique, fix any clashing value
        if group_idx > 3:
            return
        for g in range(4):
            if g != group_idx:
                if clist[g] == new_value:
                    clist[g] = old_value


CONFIG = Config(_FNAME)
