import random
import rp2
from rp2 import PIO
from machine import Pin



@rp2.asm_pio(autopull=True, autopush=True)
def pp_doubler():
    out(x, 1)
    in_(x, 1)
    in_(x, 1)


@rp2.asm_pio(autopull=True, autopush=True)
def pp_invert():
    out(x, 1)
    mov(x, invert(x))
    in_(x, 1)


@rp2.asm_pio(
    autopull=True,
    autopush=True,
    out_shiftdir=PIO.SHIFT_RIGHT,
    in_shiftdir=PIO.SHIFT_RIGHT,
)
def pp_clut_0():
    # 10 instructions to expand 4 bits to 6
    # out transfers = in transfers * 1.5
    out(x, 1)
    out(y, 1)
    in_(x, 1)
    in_(y, 1)
    out(y, 1)
    in_(x, 1)
    in_(y, 1)
    out(y, 1)
    in_(x, 1)
    in_(y, 1)


@rp2.asm_pio(
    autopull=True,
    autopush=True,
    out_shiftdir=PIO.SHIFT_RIGHT,
    in_shiftdir=PIO.SHIFT_RIGHT,
)
def pp_clut_1():
    # For each 6 bits, expand to 16
    # 12 instructions.
    # out transfers = in transfers * 8/3s
    out(x, 2)
    in_(x, 1)
    in_(x, 2)
    in_(x, 2)

    out(x, 2)
    in_(x, 2)
    in_(x, 2)
    in_(x, 2)

    out(x, 2)
    in_(x, 1)
    in_(x, 2)
    in_(x, 2)


def double_bits():
    print("\ndouble")
    sm = rp2.StateMachine(0, pp_doubler)
    inp = 0xC00AA00C
    inp = 0x9000_0001
    sm.put(inp)
    sm.active(1)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    print(f"     {sm.get():032b}")
    sm.active(0)


def invert_bits():
    print("\ninvert")
    sm = rp2.StateMachine(0, pp_invert)
    sm.active(1)
    inp = 0xC00AA00C
    sm.put(inp)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    inp = 0x2222_2222
    sm.put(inp)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    sm.active(0)


def double_invert_bits():
    print("\ndouble_invert")
    sm0 = rp2.StateMachine(0, pp_doubler)
    sm1 = rp2.StateMachine(1, pp_invert)

    n = 10

    dma = rp2.DMA()
    ctrl_bits = dma.pack_ctrl(
        inc_read=False,
        inc_write=False,
        # need to be super careful about how this is driven
        # dreq must go on slower component, but if that is the transmitter, then
        # data must 100% be read at dreq time
        # Would be easy to get de-synchronised, I guess
        treq_sel=4,  # PIO 0, State machine 0, RX (output of PIO)
    )
    dma.config(read=sm0, write=sm1, count=(n * 3) // 2, ctrl=ctrl_bits)
    dma.active(1)
    sm0.active(1)
    sm1.active(1)

    for i in range(n):
        inp = random.getrandbits(32)
        sm0.put(inp)
        print(f"{i:2} in:  {inp:032b}")
        print(f"   out: {sm1.get():032b}")
        print(f"        {sm1.get():032b}")

    dma.active(0)
    sm0.active(0)
    sm1.active(0)


def bf(n):
    return "_".join(f"{(n >> i) % 16:04b}" for i in range(28, -1, -4))


def run_pp_clut_0():
    print("\npp clut 0")
    sm0 = rp2.StateMachine(0, pp_clut_0)
    n = 16
    buf_in = bytearray(n * 4)
    for i in range(len(buf_in)):
        k = (i * 2) + ((i * 2 + 1) << 4)
        buf_in[i] = k

    sm0.active(1)
    for i in range(n):
        print(i)
        inp = (
            buf_in[i * 4 + 0]
            + (buf_in[i * 4 + 1] << 8)
            + (buf_in[i * 4 + 2] << 16)
            + (buf_in[i * 4 + 3] << 24)
        )

        print(f"{bf(inp)=}")
        sm0.put(inp)

        # hardcode move from here to there
        tmp = sm0.get()
        print(f"{bf(tmp)=}")
        if i % 2 == 1:
            tmp = sm0.get()
            print(f"{bf(tmp)=}")
    sm0.active(0)


CLUT_0_VALS = [
    0b000000,
    0b010101,
    0b000010,
    0b010111,
    0b001000,
    0b011101,
    0b001010,
    0b011111,
    0b100000,
    0b110101,
    0b100010,
    0b110111,
    0b101000,
    0b111101,
    0b101010,
    0b111111,
]


def run_pp_clut_1():
    print("\npp clut 1")
    sm1 = rp2.StateMachine(1, pp_clut_1)
    n = 3  # words = 12 bytes
    buf_in = bytearray(n * 4)
    for i in range(4):
        k = (
            (CLUT_0_VALS[i * 4 + 0] << 0)
            + (CLUT_0_VALS[i * 4 + 1] << 6)
            + (CLUT_0_VALS[i * 4 + 2] << 12)
            + (CLUT_0_VALS[i * 4 + 3] << 18)
        )

        buf_in[i * 3 + 0] = k
        buf_in[i * 3 + 1] = k >> 8
        buf_in[i * 3 + 2] = k >> 16

    sm1.active(1)
    for i in range(n):
        print(i)
        inp = (
            buf_in[i * 4 + 0]
            + (buf_in[i * 4 + 1] << 8)
            + (buf_in[i * 4 + 2] << 16)
            + (buf_in[i * 4 + 3] << 24)
        )

        print(f"{bf(inp)=}")
        sm1.put(inp)

        # hardcode move from here to there
        tmp = sm1.get()
        print(f"{bf(tmp)=}")
        tmp = sm1.get()
        print(f"{bf(tmp)=}")
        if i % 3 in (1, 2):
            tmp = sm1.get()
            print(f"{bf(tmp)=}")
    sm1.active(0)


def run_pp_clut():
    print("\npp clut")
    sm0 = rp2.StateMachine(0, pp_clut_0)
    sm1 = rp2.StateMachine(1, pp_clut_1)

    n = 16

    buf_in = bytearray(n * 4)
    for i in range(len(buf_in)):
        k = (i * 2) + ((i * 2 + 1) << 4)
        buf_in[i] = k
    buf_out = bytearray(n * 4 * 4)

    pp_dma = rp2.DMA()
    ctrl_bits = pp_dma.pack_ctrl(
        inc_read=False,
        inc_write=False,
        # need to be super careful about how this is driven
        # dreq must go on slower component, but if that is the transmitter, then
        # data must 100% be read at dreq time
        # Would be easy to get de-synchronised, I guess
        treq_sel=5,  # PIO 0, State machine 1, TX (input of PIO)
    )
    pp_dma.config(read=sm0, write=sm1, count=(n * 3) //2, ctrl=ctrl_bits)
    sm0.active(1)
    sm1.active(1)
    pp_dma.active(1)

    for i in range(n):
        print(i)
        inp = (
            buf_in[i * 4 + 0]
            + (buf_in[i * 4 + 1] << 8)
            + (buf_in[i * 4 + 2] << 16)
            + (buf_in[i * 4 + 3] << 24)
        )

        print(f"{bf(inp)=}")
        sm0.put(inp)

        def sm1fetch(n):
            print(f"sm1fetch({n})")
            while not sm1.rx_fifo(): pass
            val = sm1.get()
            print(f"{n:3}: {bf(val)=}")
            buf_out[n + 0] = val
            buf_out[n + 1] = val >> 8
            buf_out[n + 2] = val >> 16
            buf_out[n + 3] = val >> 24

        sm1fetch(i*16)
        sm1fetch(i*16+4)
        sm1fetch(i*16+8)
        sm1fetch(i*16+12)

    pp_dma.active(0)
    sm0.active(0)
    sm1.active(0)
    print("done")


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def p_blink_1hz():
    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000
    set(pins, 1)
    set(x, 31)                  [6]
    label("delay_high")
    nop()                       [29]
    jmp(x_dec, "delay_high")

    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000
    set(pins, 0)
    set(x, 31)                  [6]
    label("delay_low")
    nop()                       [29]
    jmp(x_dec, "delay_low")


def run_blink_1hz():
    # Create and start a StateMachine with blink_1hz, outputting on Pin(25)
    sm = rp2.StateMachine(0, p_blink_1hz, freq=4000, set_base=Pin(25))
    sm.active(1)


@rp2.asm_pio(
    autopull=True,
    autopush=True,
    out_shiftdir=PIO.SHIFT_RIGHT,
    in_shiftdir=PIO.SHIFT_RIGHT,
)
def p_clut():
    # For each 4 bits, expand to 16
    out(x, 1) # Get color LSB

    out(y, 1) # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1) # G 6 bits
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

    out(y, 1) # R 5 bits
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)
    in_(x, 1)
    in_(y, 1)

def run_clut():
    print("\np clut")
    sm0 = rp2.StateMachine(0, p_clut)
    n = 8
    buf_in = bytearray(n * 4)
    for i in range(len(buf_in)):
        buf_in[i] = random.getrandbits(8)

    sm0.active(1)
    for i in range(n):
        inp = (
            buf_in[i * 4 + 0]
            + (buf_in[i * 4 + 1] << 8)
            + (buf_in[i * 4 + 2] << 16)
            + (buf_in[i * 4 + 3] << 24)
        )

        print(f"{i:2}: {bf(inp)=}")
        sm0.put(inp)
        for j in range(4):
            print(f"  {j}: {bf(sm0.get())=}")
    sm0.active(0)

@rp2.asm_pio(
    autopull=True,
    autopush=True,
    out_shiftdir=PIO.SHIFT_RIGHT,
    in_shiftdir=PIO.SHIFT_RIGHT,
)
def p_fake():
    # For each 4 bits, expand to 16
    out(x, 4)
    in_(null, 16) # Get color LSB

def run_fake():
    print("\nrun clut 1")
    sm = rp2.StateMachine(0, p_fake)
    inp = 0x0
    sm.active(1)
    sm.put(inp)
    print(f"in:  {bf(inp)=}")
    print(f"out: {bf(sm.get())=}")
    print(f"out: {bf(sm.get())=}")
    print(f"out: {bf(sm.get())=}")
    print(f"out: {bf(sm.get())=}")
    sm.active(0)

@rp2.asm_pio(
    autopull=True,
    autopush=False,
    out_shiftdir=PIO.SHIFT_RIGHT,
    in_shiftdir=PIO.SHIFT_LEFT,
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

def run_clut_b():
    print("\np clut b")
    sm0 = rp2.StateMachine(0, p_clut_b)
    n = 2
    buf_in = bytearray(n * 4)
    for i in range(len(buf_in)):
        buf_in[i] = ((i*2+1) << 4) + (i * 2) #random.getrandbits(8)

    sm0.active(1)
    for i in range(n):
        inp = (
            buf_in[i * 4 + 0]
            + (buf_in[i * 4 + 1] << 8)
            + (buf_in[i * 4 + 2] << 16)
            + (buf_in[i * 4 + 3] << 24)
        )

        print(f"{i:2}: {bf(inp)=}")
        sm0.put(inp)
        for j in range(16):
            print(f"  {j}: {bf(sm0.get())=}")
    sm0.active(0)

def run():
    run_clut_b()
    # double_bits()
    # invert_bits()
    #double_invert_bits()
    #run_pp_clut()
    #run_pp_clut_0()
    #run_pp_clut_1()
    #run_blink_1hz()
    #run_fake()
    #run_clut()
