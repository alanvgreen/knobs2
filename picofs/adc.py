import asyncio
import machine


class PotReader:
    def __init__(self, pot_holder):
        self._pot_holder = pot_holder
        self._adcs = [
            machine.ADC(26),
            machine.ADC(27),
            machine.ADC(28),
        ]

    async def read_one(self, idx):
        """Reads the value of a single pot, 0-17"""
        if idx < 16:
            # adc 0 and multiplexer
            return self._adcs[0].read_u16()
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
