import asyncio
from machine import ADC, Pin, mem32
from periph import ADCRegisters
from rp2 import DMA
from uctypes import addressof

DMA_BASE = 0x50000000
DUMMY_BUF = bytearray(4)
DMA_COUNT = 256 # ideally, a multiple of 16
SNIFF_DIV = DMA_COUNT // 16
SNIFF_CTRL = DMA_BASE + 0x434
SNIFF_DATA = DMA_BASE + 0x438

def init_dma_sniff(channel):
    """Set up DMA Sniff controller for summing.

    channel: DMA channel to sum
    """
    mem32[SNIFF_DATA] = 0
    enable = 1
    sniff_channel = channel << 1
    sum_fn = 0xf << 5
    mem32[SNIFF_CTRL] = 1 | (channel << 1) | (0xf << 5)
    mem32[SNIFF_CTRL] = enable | sniff_channel | sum_fn

def read_dma_sniff():
    return mem32[SNIFF_DATA] // SNIFF_DIV


def init_dma_channel(addr):
    """Initialises the dma channel for ADC.

    Will use the sniff hardware to sum the ADC output.

    Params:
      - addr
    """
    d = DMA()

    d.read = addr
    d.write = addressof(DUMMY_BUF)
    d.count = DMA_COUNT
    dreq_adc = 36
    d.ctrl = d.pack_ctrl(
            irq_quiet = False,
            inc_read=False,
            inc_write=False,
            treq_sel=dreq_adc,
            sniff_en=True)
    init_dma_sniff(d.channel)
    return d

class PotReader:
    def __init__(self, pot_holder):
        self._pot_holder = pot_holder
        # init every ADC channel by doing one read
        self._adcs = [
            ADC(26),
            ADC(27),
            ADC(28),
        ]
        for a in self._adcs:
            a.read_u16()

        self._inhibit = Pin(16, Pin.OUT, value=1)
        self._sel = [
            Pin(20, Pin.OUT, value=0),
            Pin(19, Pin.OUT, value=0),
            Pin(17, Pin.OUT, value=0),
            Pin(18, Pin.OUT, value=0),
        ]
        self._adc_regs = ADCRegisters()
        self._dma = init_dma_channel(self._adc_regs.get_fifo_addr())


    async def read_adc_channel(self, adc_channel):
        init_dma_sniff(self._dma.channel)
        self._adc_regs.prepare(adc_channel)
        self._dma.active(True)
        self._adc_regs.start()
        while self._dma.active():
            # replace with wake-up callback
            await asyncio.sleep_ms(0)
        self._adc_regs.stop()
        return read_dma_sniff()

    async def read_one(self, idx):
        """Reads the value of a single pot, 0-17"""
        if idx < 16:
            # Channel zero via mux
            self._sel[0].value(idx & 1)
            self._sel[1].value(idx & 2)
            self._sel[2].value(idx & 4)
            self._sel[3].value(idx & 8)
            self._inhibit.value(0)
            #val = await self.read_adc_channel(0)
            val = self._adcs[0].read_u16()
            self._inhibit.value(1)
            return val
        elif idx < 18:
            # read channel one or two
            return self._adcs[idx-15].read_u16()
            return await self.read_adc_channel(idx-15)
        else:
            print(f"invalid index {idx}")
            return 0

    async def loop(self):
        while True:
            for idx in range(18):
                value = await self.read_one(idx)
                self._pot_holder.update(idx, value)
                # Give other things a chance to run
                await asyncio.sleep_ms(1)
