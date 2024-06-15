class Pot:
    # Handles processing for a Pot
    HYSTERESIS = 1 << 7

    def __init__(self, idx, callback):
        self.idx = idx
        self._raw = 0  # 16 bit value
        self._callback = callback

    @property
    def cooked(self):
        # A value between 0 and 127
        # TODO: needs some more work to calibrate
        # TODO: dead zones near the ends?
        return self._raw >> 9

    def update_raw(self, new_value):
        """Update with 16 bit new_value"""
        if abs(self._raw - new_value) >= self.HYSTERESIS:
            self._raw = new_value
            self._callback(self.idx, self.cooked)


class PotHolder:
    # Holds 18 pot values.
    NPOTS = 18

    def __init__(self):
        self._pots = [Pot(i, self._pot_callback) for i in range(self.NPOTS)]
        self._callbacks = []

    def add_callback(self, cb):
        self._callbacks.append(cb)

    def _pot_callback(self, idx, cooked_value):
        for cb in self._callbacks:
            cb(idx, cooked_value)

    def get_values(self):
        return [p.cooked for p in self._pots]

    def update(self, idx, raw_value):
        # idx is 0-17
        # raw_value is in range 0-65535
        # print("update", idx, raw_value)
        self._pots[idx].update_raw(raw_value)
