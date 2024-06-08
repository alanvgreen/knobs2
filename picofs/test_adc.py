from machine import ADC, Pin
import time


def test():
    pins = [
        Pin(2, Pin.OUT),
        Pin(3, Pin.OUT),
        Pin(4, Pin.OUT),
    ]

    adcs = [ADC(0), ADC(1)]

    results = []

    for p in pins:
        p.value(1)
        for a in adcs:
            a.read_u16()
            results.append(a.read_u16())
        p.value(0)

    print(results)


test()
