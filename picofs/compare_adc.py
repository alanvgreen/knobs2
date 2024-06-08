"""Code for interacting with the ADC and related hardware."""

import math
import machine
import time


def square(n):
    return n * n


def stddev(data):
    """Sample stddev"""
    n = len(data)
    mu = sum(data) / n
    ss = sum(square(d - mu) for d in data)
    return math.sqrt(ss / (n - 1))


def mean(data):
    n = len(data)
    return sum(data) / n


class AdcReader:
    def setup(self):
        pass

    def read1(self):
        "do one reading"
        return 1

    def label(self):
        return self.__class__.__name__[: -len("Reader")]

    def run(self):
        self.setup()
        start = time.ticks_ms()
        data = [self.read1() for _ in range(30)]
        end = time.ticks_ms()
        ms = (end - start) / 30
        print(f"{self.label():20} {ms:5.2f} {stddev(data):7.2f} {mean(data):10.2f}")


class DummyReader(AdcReader):
    def setup(self):
        pass

    def read1(self):
        return 5


class SimpleReader(AdcReader):
    def __init__(self, n):
        self.n = n

    def label(self):
        return f"Simple({self.n})"

    def setup(self):
        self.p = machine.ADC(26)

    def read1(self):
        s = 0
        for i in range(self.n):
            s += self.p.read_u16() >> 4
        return s // self.n


def test():
    """Compare std_dev in different modes."""

    readers = [
        DummyReader(),
        SimpleReader(1),
        SimpleReader(30),
    ]
    print(f"{'name':20} {'ms':>5}  stddev")
    for r in readers:
        r.run()
