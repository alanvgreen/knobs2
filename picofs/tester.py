import machine
import time
from machine import mem32
from rp2 import DMA
from uctypes import addressof
from periph import ADCRegisters

#import test_pio
import test_pio2

BLEN = 64

#    ctrl = {
#        "ahb_err": 0, # read only
#        "read_err": 0, # read + write to clear
#        "write_err": 0, # read + write to clear
#        "busy": 0, # read only
#        "sniff_en": 0,
#        "bswap": 0,
#        "irq_quiet": 0,
#        "treq_sel": 0x3f, # 3f is unpaced
#        "chain_to": d.channel,
#        "ring_sel": 0,
#        "ring_size": 0, # No ring
#        "inc_write": 1,
#        "inc_read": 1,
#        "size": 2, # 0 = byte, 2 = word
#        "high_pri": 0,
#        "enable": 1,
#    }

def mk_buf(val):
    buf = bytearray(BLEN)
    for i in range(BLEN):
        buf[i] = val
    return buf


def set_dma_done(dma):
    done_holder = [False]
    def dma_irq_handler(d):
        done_holder[0] = True
    dma.irq(handler=dma_irq_handler)
    return done_holder
    

def buf_to_buf():
    buf_a = mk_buf(0x81)
    buf_b = mk_buf(0)

    d = DMA()
    d.read = addressof(buf_a)
    d.write = addressof(buf_b)
    d.count = BLEN // 4
    d.ctrl = d.pack_ctrl(irq_quiet = False)
    print("before trigger")
    print(f"{buf_a.hex()=}")
    print(f"{buf_b.hex()=}")
    done = set_dma_done(d)
    d.active(True)
    while not done[0]:
        print("---")
    print("=====")
    print("after trigger")
    print(f"{buf_a.hex()=}")
    print(f"{buf_b.hex()=}")


def adc_to_buf():
    adc_regs = ADCRegisters()
    buf_b = mk_buf(0)

    # prep this one channel - set pins up etc
    adc1 = machine.ADC(27)
    adc1.read_u16()

    d = DMA()

    d.read = adc_regs.get_fifo_addr()
    d.write = addressof(buf_b)
    d.count = BLEN // 4
    dreq_adc = 36
    d.ctrl = d.pack_ctrl(
            irq_quiet = False,
            inc_read=False,
            treq_sel=dreq_adc)
    done = set_dma_done(d)

    print("before trigger")
    print(f"{buf_b.hex()=}")

    start = time.ticks_ms()
    adc_regs.prepare(1)
    d.active(True)

    l = d.count
    adc_regs.start()
    while not done[0]:
        time.sleep_ms(1)
        #print(f"{d.count=} {hex(adc_regs.cs)=} {buf_b.hex()=}")
    adc_regs.stop()
    end = time.ticks_ms()
    print(f"{end-start=}")


    print("=====")
    print("after trigger")
    print(f"{buf_b.hex()=}")


DMA_BASE = 0x50000000
SNIFF_CTRL = DMA_BASE + 0x434
SNIFF_DATA = DMA_BASE + 0x438

def init_dma_sniff(channel):
    mem32[SNIFF_DATA] = 0
    mem32[SNIFF_CTRL] = 1 | (channel << 1) | (0xf << 5)

def read_dma_sniff():
    return mem32[SNIFF_DATA]


def adc_to_sum():
    adc_regs = ADCRegisters()
    buf = bytearray(4)

    # prep this one channel - set pins up etc
    adc1 = machine.ADC(27)
    adc1.read_u16()

    d = DMA()

    d.read = adc_regs.get_fifo_addr()
    d.write = addressof(buf)
    d.count = 16 * 256
    dreq_adc = 36
    d.ctrl = d.pack_ctrl(
            irq_quiet = False,
            inc_read=False,
            inc_write=False,
            treq_sel=dreq_adc,
            sniff_en=True)
    done = set_dma_done(d)

    init_dma_sniff(d.channel)

    print("before trigger")
    print(f"{buf.hex()=} {read_dma_sniff()=:6x}")

    start = time.ticks_ms()
    adc_regs.prepare(1)
    d.active(True)

    l = d.count
    adc_regs.start()
    while not done[0]:
        time.sleep_ms(1)
    adc_regs.stop()
    end = time.ticks_ms()
    print(f"{end-start=}")


    print("=====")
    print("after trigger")
    print(f"{buf.hex()=}, {read_dma_sniff()=:6x}")
    print(f"{buf.hex()=}, {read_dma_sniff()=:6d}")

def repr_ba(ba):
    vals = [f"{val:08b}" for val in ba]
    groups = ["_".join(vals[n:n+4]) for n in range(0, len(vals), 4)]
    return " ".join(groups)

def test_clut():
    import hardware_setup
    from clut_pio import ClutPio
    import random
    clut_0 = ClutPio(None, None)
    for i in range(4):
        inp = random.getrandbits(32)
        outp = clut_0.expand(inp)
        print(f"{i:2} in:  {inp:032b}")
        print(f"   out: {repr_ba(outp)}")

def run():
    print("hello")
    #test_clut()
    test_pio2.run()
    #buf_to_buf()
    #adc_to_buf()
    #adc_to_sum()
