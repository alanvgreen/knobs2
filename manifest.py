# Include all the regular mpy stuff
include("$(PORT_DIR)/boards/manifest.py")

# Grab the entire content of this directory
freeze("freeze")
