import random
import rp2

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

@rp2.asm_pio(autopull=True, autopush=True)
def pp_clut_0():
    # 10 insructions to expand 4 bits to 6
    # out transfers = in transfers * 1.5
    out(x, 1)
    out(y, 1)
    in_(y, 1)
    in_(x, 1)
    out(y, 1)
    in_(y, 1)
    in_(x, 1)
    out(y, 1)
    in_(y, 1)
    in_(x, 1)


def pp_clut_1():
    # For each 6 bits, expand to 16
    # 12 instructions.
    # out transfers = in transfers * 8/3s
    out(x, 2)
    in_(x, 2)
    in_(x, 2)
    in_(x, 1)

    out(x, 2)
    in_(x, 2)
    in_(x, 2)
    in_(x, 2)

    out(x, 2)
    in_(x, 2)
    in_(x, 2)
    in_(x, 1)

def double_bits():
    print('\ndouble')
    sm = rp2.StateMachine(0, pp_doubler)
    inp = 0xC00aa00C
    inp = 0x9000_0001
    sm.put(inp)
    sm.active(1)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    print(f"     {sm.get():032b}")
    sm.active(0)


def invert_bits():
    print('\ninvert')
    sm = rp2.StateMachine(0, pp_invert)
    sm.active(1)
    inp = 0xC00aa00C
    sm.put(inp)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    inp = 0x2222_2222
    sm.put(inp)
    print(f"in:  {inp:032b}")
    print(f"out: {sm.get():032b}")
    sm.active(0)


def double_invert_bits():
    print('\ndouble_invert')
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
        treq_sel=4, # PIO 0, State machine 0, RX (output of PIO)
    )
    dma.config(
        read=sm0,
        write=sm1,
        count=n*2,
        ctrl=ctrl_bits,
    )
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


def run():
    #double_bits()
    #invert_bits()
    double_invert_bits()
