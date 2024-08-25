from config import CONFIG


class Controller:
    # TODO: send initial + regular "syncs" to update control values
    # Maybe every five seconds or so?
    # Sends MIDI messages as pots update
    def __init__(self, pot_holder, midi):
        pot_holder.add_callback(self._on_pot_changed)
        self._midi = midi

    def _on_pot_changed(self, idx, val):
        channel, cc = self._get_channel_cc(idx)
        self._midi.control_change(channel, cc, val)

    def _get_channel_cc(self, idx):
        # Given a pot index (0-17), get channel and cc - default to channel zero
        # See https://anotherproducer.com/online-tools-for-musicians/midi-cc-list/
        if idx < 16:
            cc = 16 + (idx % 4)
        else:
            cc = 12 + (idx % 4)
        channel = CONFIG.get_channels()[idx // 4]
        return channel, cc
