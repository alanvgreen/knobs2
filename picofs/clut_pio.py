# A Color Lookup table implemented in a PIO
import rp2

@rp2.asm_pio(
    autopull=True,
    autopush=False,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    in_shiftdir=rp2.PIO.SHIFT_LEFT,
)
def p_clut_b():
    # For each 4 bits, expand to 16
    out(x, 1) # Get color LSB

    out(y, 1) # B 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1) # G 6 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    push()
    #in_(null, 24) # Fill ISR, force push
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)

    out(y, 1) # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    push()
    #in_(null, 24) # Fill ISR, force push


class ClutPio:
    """Color lookup table implemented with a PIO."""
    def __init__(self, mvb, spi):
        self.mvb = mvb
        self.sm0 = rp2.StateMachine(0, p_clut_b)

        # Set up dma "in" (mem to pio)
        words_in = len(mvb) // 4
        self.dma_in = rp2.DMA()
        ctrl_bits = self.dma_in.pack_ctrl(
            inc_read=True,
            inc_write=False,
            treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
            bswap=True,  # So least significant byte is left most
        )
        self.dma_in.config(read=mvb, write=self.sm0, count=words_in, ctrl=ctrl_bits)

        # TODO: pump SPI TX clock + bit directly?

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
        self.dma_out.config(read=self.sm0, write=spi, count=bytes_out, ctrl=ctrl_bits)

        # Set up DMA to ignore SPI RX
        dev_null = bytearray(4)
        self.dma_null = rp2.DMA()
        ctrl_bits = self.dma_null.pack_ctrl(
            inc_read=False,
            inc_write=False,
            treq_sel=17, # SPI0 RX
            size=0, # bytes
        )
        self.dma_null.config(read=spi, write=dev_null, count=bytes_out, ctrl=ctrl_bits)

    def manual_write_read(self, buf_in, buf_out, count):
        # count is in bytes
        self.sm0.active(1)
#        for i in range(count):
#            self.sm0.put(buf_in[i] << 24)
#            base = i * 4
#            for j in range(4):
#                buf_out[base+j] = self.sm0.get()

        for i in range(0, count, 4):
            inp = ((buf_in[i + 0] << 24)
                   +(buf_in[i + 1] << 16)
                   +(buf_in[i + 2] << 8)
                   +(buf_in[i + 3] << 0))
            self.sm0.put(inp)
            base = i * 4
            for j in range(16):
                buf_out[base+j] = self.sm0.get()
        self.sm0.active(0)

    def expand(self, val):
        inb = bytearray(4)
        inb[0] = val 
        inb[1] = (val >> 8) 
        inb[2] = (val >> 16) 
        inb[3] = (val >> 24) 
        outb = bytearray(16)
        self.manual_write_read(inb, outb, 4)
        return outb

    def run(self):
        self.dma_null.active(1)
        self.dma_out.active(1)
        self.dma_in.active(1)
        while self.dma_null.active():
            pass
        self.dma_in.active(0)
        self.dma_out.active(0)
        self.dma_null.active(0)



