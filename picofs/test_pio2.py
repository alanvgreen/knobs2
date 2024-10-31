from clut_pio import p_clut_b
from machine import Pin, SPI, freq
from periph import GPIORegisters
from rp2 import PIO
import random
import rp2
import time

random.seed(0)


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def p_blink_1hz():
    # Cycles: 1 + 1 + 6 + 32 * (30 + 1) = 1000
    irq(rel(0))
    set(pins, 1)
    set(x, 31)                  [5]
    label("delay_high")
    nop()                       [29]
    jmp(x_dec, "delay_high")
    # Cycles: 1 + 1 + 6 + 32 * (30 + 1) = 1000
    nop()
    set(pins, 0)
    set(x, 31)                  [5]
    label("delay_low")
    nop()                       [29]
    jmp(x_dec, "delay_low")

def run_blink_1hz(pin):
    # Create the StateMachine with the blink_1hz program, outputting on Pin(pin).
    sm = rp2.StateMachine(0, p_blink_1hz, freq=2000, set_base=Pin(pin))
    # Set the IRQ handler to print the millisecond timestamp.
    sm.irq(lambda p: print(time.ticks_ms()))
    # Start the StateMachine.
    sm.active(1)


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, sideset_init=rp2.PIO.OUT_LOW)
def p_toggle():
    set(pins, 1)
    nop().side(1)
    set(pins, 0)
    nop().side(0)

def run_toggle():
    prst = Pin(6, Pin.OUT, value=1)
    pcs = Pin(5, Pin.OUT, value=1)
    spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=40_000_000)

    prst(0)
    time.sleep_ms(50)
    prst(1)
    time.sleep_ms(50)

    pcs(0)

    regs = GPIORegisters()
    set_spi = regs.save_ctrl(2, 3)
    sm = rp2.StateMachine(0, p_toggle, freq=freq(), set_base=Pin(2), sideset_base=Pin(3))
    set_pio = regs.save_ctrl(2, 3)
    set_spi()
    time.sleep_ms(50)
    # Start the StateMachine.
    while True:
        set_pio()
        sm.active(1)
        time.sleep_ms(100)
        sm.active(0)
        set_spi()
        time.sleep_ms(100)
        print("again")

def run():
    #run_blink_1hz(25)
    freq(160_000_000)
    print(freq())

    #freq(150_000_000)  # RP2 overclock
    run_toggle()
