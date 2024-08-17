import asyncio
from machine import ADC, Pin


class PotReader:
    def __init__(self, pot_holder):
        self._pot_holder = pot_holder
        self._adcs = [
            ADC(26),
            ADC(27),
            ADC(28),
        ]
        self._inhibit = Pin(16, Pin.OUT, value=1)
        self._sel = [
            Pin(20, Pin.OUT, value=0),
            Pin(19, Pin.OUT, value=0),
            Pin(17, Pin.OUT, value=0),
            Pin(18, Pin.OUT, value=0),
        ]

    async def read_one(self, idx):
        """Reads the value of a single pot, 0-17"""
        if idx < 16:
            self._sel[0].value(idx & 1)
            self._sel[1].value(idx & 2)
            self._sel[2].value(idx & 4)
            self._sel[3].value(idx & 8)
            self._inhibit.value(0)
            val = self._adcs[0].read_u16()
            self._inhibit.value(1)
            return val
        elif idx < 18:
            return self._adcs[idx - 15].read_u16()
        else:
            print(f"invalid index {idx}")
            return 0

    async def loop(self):
        while True:
            await asyncio.sleep_ms(10)
            for idx in range(18):
                value = await self.read_one(idx)
                self._pot_holder.update(idx, value)
