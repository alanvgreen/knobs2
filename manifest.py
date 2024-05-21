# Include all the regular mpy stuff
include("$(PORT_DIR)/boards/manifest.py")

# Ensure USB MIDI is available
require("usb-device-midi")

# Grab the entire content of the freeze directory
freeze("freeze")
