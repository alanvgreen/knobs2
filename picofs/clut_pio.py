# A Color Lookup table implemented in a PIO
import rp2


@rp2.asm_pio(
    autopull=True,
    autopush=True,
    push_thresh=8,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    in_shiftdir=rp2.PIO.SHIFT_LEFT,
)
def p_clut_b():
    # For each 4 bits, expand to 16
    # Words (with bytes reversed) in
    # Bytes out (because that's what SPI expects)
    out(x, 1)  # Get color LSB (MSB of nybble)

    out(y, 1)  # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1)  # G 6 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)

    out(y, 1)  # B 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)


class Activated:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __enter__(self):
        self.wrapped.active(1)
        return self

    def __exit__(self, type, value, tb):
        self.wrapped.active(0)

    def active(self):
        return self.wrapped.active()


class ClutPio:
    """Just the PIO bits"""

    def __init__(self):
        self.sm0 = rp2.StateMachine(0, p_clut_b)
        self.sm0.active(1)

    def wait_for_output(self):
        while not self.sm0.rx_fifo():
            pass


class RestartableDma:
    def __init__(self, read, write):
        self.dma = rp2.DMA()
        self.read = read
        self.write = write

    def start(self):
        self.dma.read = self.read
        self.dma.write = self.write
        self.dma.active(1)

    def wait_until_done(self):
        while self.dma.active():
            pass


class DmaMemClut(RestartableDma):
    """DMA from memory to clut"""

    def __init__(self, mem, clut):
        super().__init__(mem, clut.sm0)

        ctrl_bits = self.dma.pack_ctrl(
            inc_read=True,
            inc_write=False,
            treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
            bswap=True,  # So least significant byte is left most
        )
        self.dma.config(count=len(mem) // 4, ctrl=ctrl_bits)


class DmaClutSpi(RestartableDma):
    """DMA from clut to SPI device"""

    def __init__(self, clut, spi, count):
        super().__init__(clut.sm0, spi)

        ctrl_bits = self.dma.pack_ctrl(
            inc_read=False,
            inc_write=False,
            treq_sel=16, # SPI0 TX
            size=0, # bytes
        )
        self.dma.config(count=count, ctrl=ctrl_bits)

class DmaSpiNull(RestartableDma):
    """DMA from SPI to /dev/null"""

    def __init__(self, spi, count):
        dev_null = bytearray(4)
        super().__init__(spi, dev_null)

        ctrl_bits = self.dma.pack_ctrl(
            inc_read=False,
            inc_write=False,
            treq_sel=17, # SPI0 RX
            size=0, # bytes
        )
        self.dma.config(count=count, ctrl=ctrl_bits)
