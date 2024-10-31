# A Color Lookup table implemented in a PIO
import rp2
import time
from machine import Pin, freq

from periph import GPIORegisters


# SCK clock is default low.
# data is clocked on transition from low to high


@rp2.asm_pio(
    autopull=True,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    fifo_join=rp2.PIO.JOIN_TX,
    out_init=rp2.PIO.OUT_LOW,
    sideset_init=rp2.PIO.OUT_LOW,
)
def p_clut_b():
    # For each 4 bits, expand to 16
    # Words (with bytes reversed) in
    # Bytes out (because that's what SPI expects)

    # ISR will hold LSB
    out(isr, 1).side(0)

    # Red
    out(y, 1).side(0)   # Y holds Red MSB
    set(x, 2).side(0)

    label("R")
    mov(pins, y).side(0)
    nop().side(1)
    mov(pins, isr).side(0)
    jmp(x_dec, "R").side(1)
    mov(pins, y).side(0)

    # Green
    out(y, 1).side(1)
    set(x, 2).side(0)

    label("G")
    mov(pins, y).side(0)
    nop().side(1)
    mov(pins, isr).side(0)
    jmp(x_dec, "G").side(1)

    # Blue
    out(y, 1).side(0)
    set(x, 2).side(0)

    label("B")
    mov(pins, y).side(0)
    nop().side(1)
    mov(pins, isr).side(0)
    jmp(x_dec, "B").side(1)
    mov(pins, y).side(0)
    nop().side(1) # Wasted?

@rp2.asm_pio(
    autopull=True,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    fifo_join=rp2.PIO.JOIN_TX,
    set_init=rp2.PIO.OUT_LOW, # COPI
    sideset_init=rp2.PIO.OUT_LOW, # CLK
)
def p_green_b():
    # Uses set instead of move
    out(x, 4).side(0) # consume 4 bits of color

    set(x, 5).side(0)
    label("R")
    set(pins, 0).side(0)
    jmp(x_dec, "R").side(1)

    set(x, 6).side(0)
    label("G")
    set(pins, 1).side(0)
    jmp(x_dec, "G").side(1)

    set(x, 5).side(0)
    label("B")
    set(pins, 0).side(0)
    jmp(x_dec, "B").side(1)


class ClutPio:
    """Just the PIO bits"""

    # TODO:
    # - set frequency to 80Mhz or so
    # - Data out, clock low then Raise clock to toggle data out
    # - Functions to connect / disconnect data out and side set to PIO

    def __init__(self):
        regs = GPIORegisters()
        self.set_pins_spi = regs.save_ctrl(2, 3)
        self.sm0 = rp2.StateMachine(
            0,
            #prog=p_clut_b,
            prog=p_green_b,
            #freq=freq(),
            freq=20_000_000,
            out_base=Pin(3),  # COPI
            set_base=Pin(3),  # COPI
            sideset_base=Pin(2),  # SCK
        )
        self.set_pins_pio0 = regs.save_ctrl(2, 3)
        self.set_pins_spi()

    def activate(self):
        self.set_pins_pio0()
        self.sm0.active(1)

    def deactivate(self):
        self.sm0.active(0)
        self.set_pins_spi()

    def wait_until_done(self):
        # wait for the tx fifo to drain
        while self.sm0.tx_fifo(): 
            pass
        time.sleep_us(1)


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
        )
        self.dma.config(count=len(mem) // 4, ctrl=ctrl_bits)
