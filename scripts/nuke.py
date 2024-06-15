import os

# Based on https://gist.github.com/romilly/5a1ff86d1e4d87e084b76d5651f23a40

# This will fail on big python
import rp2

# deletes everything in the Micropython current directory
def nuke(directory='.', keep_this=True):
    for fi in os.ilistdir(directory):
        fn, ft = fi[0:2] # can be 3 or 4 items returned!
        fp = '%s/%s' % (directory, fn)
        print('removing %s' % fp) 
        if ft == 0x8000:
            os.remove(fp)
        else:
            nuke(fp)
            os.rmdir(fp)


