# A Color Lookup table implemented in a PIO
import rp2
import hardware_setup as hs


@rp2.asm_pio(
    autopull=True,
    autopush=True,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    in_shiftdir=rp2.PIO.SHIFT_RIGHT,
    push_thresh=8,
)
def p_clut():
    # For each 4 bits, expand to 16
    out(x, 1)  # Get color LSB

    out(y, 1)  # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1)  # G 6 bits
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1)  # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)


class ClutPio:
    """Color lookup table implemented with a PIO."""
    def __init__(self, mvb):
        self.mvb = mvb
        self.sm0 = rp2.StateMachine(0, p_clut)
        self.sm0.active(1)

        # Set up dma "in" (mem to pio)
        words_in = len(mvb) // 4
        self.dma_in = rp2.DMA()
        ctrl_bits = self.dma_in.pack_ctrl(
            inc_read=True,
            inc_write=False,
            treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
        )
        self.dma_in.config(read=mvb, write=self.sm0, count=words_in, ctrl=ctrl_bits)

        # Set up dma "out" (pio to spi 0)
        bytes_out = len(mvb) * 4
        print(f"{len(mvb)=} {words_in=} {bytes_out=}")
        self.dma_out = rp2.DMA()
        ctrl_bits = self.dma_out.pack_ctrl(
            inc_read=False,
            inc_write=False,
            treq_sel=16, # SPI0 TX
            size=0, # bytes
        )
        self.dma_out.config(read=self.sm0, write=hs.spi, count=bytes_out, ctrl=ctrl_bits)

        # Set up DMA to ignore SPI RX
        dev_null = bytearray(4)
        self.dma_null = rp2.DMA()
        ctrl_bits = self.dma_null.pack_ctrl(
            inc_read=False,
            inc_write=False,
            treq_sel=17, # SPI0 RX
            size=0, # bytes
        )
        self.dma_null.config(read=hs.spi, write=dev_null, count=bytes_out, ctrl=ctrl_bits)

    def run(self):
        print('dma begin')
        self.dma_null.active(1)
        self.dma_out.active(1)
        self.dma_in.active(1)
        while self.dma_null.active():
            pass
        self.dma_in.active(0)
        self.dma_out.active(0)
        self.dma_null.active(0)
        print('dma end')
