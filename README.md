# Knobs

A many-knobbed Micropython MIDI Controller project for the RP2040.

This is a personal project that I don't expect anyone will ever replictate
precisely. I hope parts of it may be interesting to others.

## What am I looking at?

- picofs - Unfrozen Python and other files that will end up on the Pico's file
  system.
- freeze - Python to be pre-compiled and frozen into the MicroPython image.
- scripts - Dev-time shell scripts


## Poetry

This project uses [Poetry](https://python-poetry.org/) to managed its development-time dependencies.

## Fonts

Knobs2 uses these OFL licensed fonts:

- [Poetsen One](https://fonts.google.com/specimen/Poetsen+One)
- [Poppins](https://fonts.google.com/specimen/Poppins?query=poppins)

The font files in `freeze/myfonts` were created with the
[micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py)
utility. The derived font files are covered by licenses in the `licenses`
directory.


## Micropython Config

Micropython is unchanged excepting that we enable the UART. This allows us to
plug the Pico's USB cable into a PC (where the Pico provides a MIDI controller
interface) and still use the Micropython REPL from a separate development host
- an RPi 4.
