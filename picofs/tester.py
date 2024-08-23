from rp2 import DMA
from uctypes import addressof

BLEN = 64


def mk_buf(val):
    buf = bytearray(BLEN)
    for i in range(BLEN):
        buf[i] = val
    return buf


def buf_to_buf():
    buf_a = mk_buf(0x81)
    buf_b = mk_buf(0)
    print(f"{buf_a.hex()=}")
    print(f"{buf_b.hex()=}")

    d = DMA()
    d.read = addressof(buf_a)
    d.write = addressof(buf_b)
    d.count = BLEN // 4
    ctrl = {
        "inc_read": 0,
        "high_pri": 0,
        "write_err": 0,
        "ring_sel": 0,
        "enable": 0,
        "treq_sel": 0,
        "sniff_en": 0,
        "irq_quiet": 0,
        "read_err": 0,
        "chain_to": 0,
        "busy": 0,
        "inc_write": 0,
        "ring_size": 0,
        "bswap": 0,
        "size": 0,
        "ahb_err": 0,
    }
    d.ctrl = DMA.pack(ctrl)


def run():
    print("hello")
    buf_to_buf()
