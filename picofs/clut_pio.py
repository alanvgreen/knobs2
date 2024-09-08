# A Color Lookup table implemented in a PIO

@rp2.asm_pio(autopull=True, autopush=True)
def clut_0():
    out(x, 1)

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
