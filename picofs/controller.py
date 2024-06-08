class Config:
    # Defines how pot indexes map to channel and cc index
    # See ihttps://anotherproducer.com/online-tools-for-musicians/midi-cc-list/

    def __init__(self):
        pass

    def get_channel_cc(self, idx):
        if idx < 16:
            # Map channels "1-4", general purpose CC 1-3
            return (idx // 4, 16 + (idx % 4))
        else:
            # Effects controllers 1 and 2 on channel "1"
            return (0, 12 + idx - 16)


class Controller:
    # Sends MIDI messages as pots update
    def __init__(self, pot_holder, config, midi):
        pot_holder.add_callback(self._on_pot_changed)
        self._config = config
        self._midi = midi

    def _on_pot_changed(self, idx, val):
        channel, cc = self._config.get_channel_cc(idx)
        self._midi.control_change(channel, cc, val)
