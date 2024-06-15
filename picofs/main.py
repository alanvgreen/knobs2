# Start app on boot/reboot
#
# To prevent the app from starting:
#
# 1. Connect to a repl with mpremote tool
# 2. Use Ctrl-C to stop the application
# 3. Type: `import os;os.unlink('main.py')
# 4. Disconnect and reconnect the device
#
# At this point the REPL should be available and
# code can be modified / deleted as desired.
#
import app

app.start()
