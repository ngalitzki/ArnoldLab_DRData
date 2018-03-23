import visa
import numpy as np
import time
import sys
from datetime import datetime

old_stdout = sys.stdout
log_file = open('Run1.log', 'w')
sys.stdout = log_file
fname = 'LoadCurve_Run1_Start20170811.txt'

rm = visa.ResourceManager()
print(rm.list_resources())

psup = rm.open_resource('USB0::0x05E6::0x2230::9102893::0::INSTR')
print(psup.query('*idn?'))

fourk_maxP = 2.0 #2 W
mc_maxP = 0.6/1000 #600 uW

fourk_steps = 6
mc_steps = 6

fourk_p = np.linspace(0, fourk_maxP, fourk_steps)
mc_p = np.linspace(0, mc_maxP, mc_steps)

fourk_r = 1000
mc_r = 120

fourk_i = np.sqrt(fourk_p/fourk_r)
mc_i = np.sqrt(mc_p/mc_r)

fourk_v = fourk_i*fourk_r
mc_v = mc_i * mc_r

for i, fourkval in enumerate(fourk_v):
    print('4K being set to V, I, P: ', fourkval, fourk_i[i], fourk_p[i])
    psup.write('inst:sel ch1')
    psup.write('volt '+np.str(fourkval))

    for j, mcval in enumerate(mc_v):
        print('MC being set to V, I, P: ', mcval, mc_i[j], mc_p[j])
        psup.write('inst:sel ch2')
        psup.write('volt '+np.str(mcval))

        time.sleep(5)
