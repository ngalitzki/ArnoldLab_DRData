from prologixInterface import prologixInterface
import time, sys
import subprocess as sp
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f',
    help = 'Temperature log file. Use absolute path',
    action = 'store')

lastTempsStr = sp.check_output('tail ' + f, shell = True).split('n')[-1]
lastTemps = lastTempsStr.split(',')

try:
    while True:
        if lastTemps[]

except KeyboardInterrupt:
    print '\nReceived interrupt - exiting.'
    sys.exit()
    
