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


class ClutPio(Activated):
    """Just the PIO bits"""

    def __init__(self):
        self.sm0 = rp2.StateMachine(0, p_clut_b)
        super().__init__(self.sm0)


class ActivatedDma(Activated):
    def __init__(self, read, write):
        self.dma = rp2.DMA()
        super().__init__(self.dma)
        self.read = read
        self.write = write

    def __enter__(self):
        self.dma.read = self.read
        self.dma.write = self.write
        return super().__enter__()


class DmaMemClut(ActivatedDma):
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


class DmaClutMem(ActivatedDma):
    """DMA from clut to memory"""

    def __init__(self, clut, mem):
        super().__init__(clut.sm0, mem)

        ctrl_bits = self.dma.pack_ctrl(
            inc_read=False,
            inc_write=True,
            treq_sel=4, # PIO 0, State machine 0, RX
            size=0, # bytes
        )
        self.dma.config(count=len(mem), ctrl=ctrl_bits)

def run_activated(ctx_mgr, *rest):
    with ctx_mgr:
        if rest:
            run_activated(*rest)
        else:
            while ctx_mgr.active():
                pass

# class ClutPio:
#    """Color lookup table implemented with a PIO."""
#    def __init__(self, mvb, spi):
#        self.mvb = mvb
#        self.sm0 = rp2.StateMachine(0, p_clut_b)
#
#        # Set up dma "in" (mem to pio)
#        words_in = len(mvb) // 4
#        self.dma_in = rp2.DMA()
#        ctrl_bits = self.dma_in.pack_ctrl(
#            inc_read=True,
#            inc_write=False,
#            treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
#            bswap=True,  # So least significant byte is left most
#        )
#        self.dma_in.config(read=mvb, write=self.sm0, count=words_in, ctrl=ctrl_bits)
#
#        # TODO: pump SPI TX clock + bit directly?
#
#        # Set up dma "out" (pio to spi 0)
#        bytes_out = len(mvb) * 4
#        print(f"{len(mvb)=} {words_in=} {bytes_out=}")
#        self.dma_out = rp2.DMA()
#        ctrl_bits = self.dma_out.pack_ctrl(
#            inc_read=False,
#            inc_write=False,
#            treq_sel=16, # SPI0 TX
#            size=0, # bytes
#        )
#        self.dma_out.config(read=self.sm0, write=spi, count=bytes_out, ctrl=ctrl_bits)
#
#        # Set up DMA to ignore SPI RX
#        dev_null = bytearray(4)
#        self.dma_null = rp2.DMA()
#        ctrl_bits = self.dma_null.pack_ctrl(
#            inc_read=False,
#            inc_write=False,
#            treq_sel=17, # SPI0 RX
#            size=0, # bytes
#        )
#        self.dma_null.config(read=spi, write=dev_null, count=bytes_out, ctrl=ctrl_bits)
#
#    def manual_write_read(self, buf_in, buf_out, count):
#        # count is in bytes
#        self.sm0.active(1)
##        for i in range(count):
##            self.sm0.put(buf_in[i] << 24)
##            base = i * 4
##            for j in range(4):
##                buf_out[base+j] = self.sm0.get()
#
#        for i in range(0, count, 4):
#            inp = ((buf_in[i + 0] << 24)
#                   +(buf_in[i + 1] << 16)
#                   +(buf_in[i + 2] << 8)
#                   +(buf_in[i + 3] << 0))
#            self.sm0.put(inp)
#            base = i * 4
#            for j in range(16):
#                buf_out[base+j] = self.sm0.get()
#        self.sm0.active(0)
#
#    def expand(self, val):
#        inb = bytearray(4)
#        inb[0] = val
#        inb[1] = (val >> 8)
#        inb[2] = (val >> 16)
#        inb[3] = (val >> 24)
#        outb = bytearray(16)
#        self.manual_write_read(inb, outb, 4)
#        return outb
#
#    def run(self):
#        self.dma_null.active(1)
#        self.dma_out.active(1)
#        self.dma_in.active(1)
#        while self.dma_null.active():
#            pass
#        self.dma_in.active(0)
#        self.dma_out.active(0)
#        self.dma_null.active(0)
#
#
#
