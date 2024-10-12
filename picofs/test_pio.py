import random
import rp2
from rp2 import PIO
from machine import Pin
from clut_pio import p_clut_b

random.seed(0)


def randb():
    return random.getrandbits(8)


def randa(n):
    return bytearray(randb() for _ in range(n))


def print_bytes(a):
    """Prints a byte array in hexadecimal format, 16 bytes per line, grouped in fours."""
    line_len = 32
    for i in range(0, len(a), 32):
        line = a[i : i + 32]
        hex_values = " ".join(
            "".join("{:02x}".format(b) for b in line[j : j + 4])
            for j in range(0, line_len, 4)
        )
        print(hex_values)


def test_print():
    r = randa(120)
    print_bytes(r)


def print_mapped(inp, outp):
    def ppair(i, n, ni, val):
        r = val[0] >> 3
        g = ((val[0] & 7) << 3) + (val[1] >> 5)
        b = val[1] & 0x1F
        print(f"{i:04x}{n}: {ni:04b} -> {r:05b} {g:06b} {b:05b}")

    if len(outp) != len(inp) * 4:
        raise ValueError("Output array must be 4 times the size of the input array")

    for i in range(len(inp)):
        ppair(i, "m", (inp[i] & 0xF0) >> 4, outp[i * 4 + 0 : i * 4 + 2])
        ppair(i, "l", (inp[i] & 0x0F) >> 0, outp[i * 4 + 2 : i * 4 + 4])
        if i % 4 == 3:
            print()


def print_results(inp, outp):
    print("input")
    print_bytes(inp)
    print("\noutput")
    print_bytes(outp)
    print("\nmapped")
    print_mapped(inp, outp)


def test_print_mapped():
    print_results(randa(120), randa(120 * 4))


def run_test_fn(fn):
    inp = randa(120)
    outp = bytearray(120 * 4)
    fn(inp, outp, 120)
    print_results(inp, outp)


def fn_manual(inp, outp, count):
    sm0 = rp2.StateMachine(0, p_clut_b)
    sm0.active(1)

    for i in range(0, count, 4):
        sm0.put(
            (inp[i + 0] << 24)
            + (inp[i + 1] << 16)
            + (inp[i + 2] << 8)
            + (inp[i + 3] << 0)
        )
        base = i * 4
        for j in range(16):
            outp[base + j] = sm0.get()
    sm0.active(0)


def fn_dma_in(inp, outp, count):
    sm0 = rp2.StateMachine(0, p_clut_b)

    words_in = len(inp) // 4
    dma_in = rp2.DMA()
    ctrl_bits = dma_in.pack_ctrl(
        inc_read=True,
        inc_write=False,
        treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
        bswap=True,  # So least significant byte is left most
    )
    dma_in.config(read=inp, write=sm0, count=words_in, ctrl=ctrl_bits)

    def do_run():
        dma_in.read = inp
        dma_in.active(1)
        # pull output
        for i in range(count * 4):
            outp[i] = sm0.get()
        dma_in.active(0)
    
    sm0.active(1)
    for i in range(5):
        print(f"run {i}")
        do_run()
    sm0.active(0)


def fn_dma_in_out(inp, outp, count):
    sm0 = rp2.StateMachine(0, p_clut_b)

    words_in = len(inp) // 4
    dma_in = rp2.DMA()
    ctrl_bits = dma_in.pack_ctrl(
        inc_read=True,
        inc_write=False,
        treq_sel=0,  # PIO 0, State machine 0, TX (input of PIO)
        bswap=True,  # So least significant byte is left most
    )
    dma_in.config(read=inp, write=sm0, count=words_in, ctrl=ctrl_bits)

    bytes_out=len(inp) * 4
    dma_out = rp2.DMA()
    ctrl_bits = dma_out.pack_ctrl(
        inc_read=False,
        inc_write=True,
        treq_sel=4, # PIO 0, State machine 0, RX
        size=0, # bytes
    )
    dma_out.config(read=sm0, write=outp, count=bytes_out, ctrl=ctrl_bits)

    def do_run():
        dma_out.write = outp
        dma_out.active(1)
        dma_in.read = inp
        dma_in.active(1)

        while dma_out.active(): pass

        dma_in.active(0)
        dma_out.active(0)
    
    sm0.active(1)
    for i in range(5):
        print(f"run {i}")
        do_run()
    sm0.active(0)



def run():
    #run_test_fn(fn_manual)
    #run_test_fn(fn_dma_in)
    run_test_fn(fn_dma_in_out)
    # test_print_mapped()
    # test_print()
