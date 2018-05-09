import time
import numpy as np
import sys, os
from datetime import datetime
import subprocess as sp

from psuInterface import psuInterface

old_stdout = sys.stdout

if os.path.isfile('Run1.log'):
    print 'Error: will overwrite data. Ending.'
    sys.exit()

log_file = open('Run1.log', 'w')
sys.stdout = log_file
fname = 'LoadCurve_4Konly.txt'


pro = psuInterface(1)

fourk_maxP = 2.0 #2 W
mc_maxP = 0.24/1000 #240 uW

fourk_steps = 8

fourk_p = np.linspace(0, fourk_maxP, fourk_steps)
fourk_r = 1000

mc_r = 120

fourk_i = np.sqrt(fourk_p/fourk_r)
mc_i = np.sqrt(mc_maxP/mc_r)

fourk_v = fourk_i*fourk_r
mc_v = mc_i * mc_r

print('4K Vs: ', fourk_v)
print ('Mixing chamber V: ', mc_v)

data=np.empty([(fourk_steps), 5], dtype=object)

print('Data shape', data.shape)

row=0

pro.setVolt(3, mc_v)
time.sleep(.2)

wtime = 20*60
time.sleep(60*60)


for i, fourkval in enumerate(fourk_v):
     print('4K being set to V, I, P: ', fourkval, fourk_i[i], fourk_p[i])
     pro.setVolt(1,fourkval/2)
     pro.setVolt(2,fourkval/2)

     time.sleep(wtime)



     rest_fourk_i = np.float(pro.getCurr(1))
     rest_mc_i = np.float(pro.getCurr(3))

     print('Measured rest current', rest_fourk_i)

     print('Row check', row, i)
     data[row, :] = np.array([[time.strftime('%d-%m-%y'), time.strftime('%X'), fourkval, rest_fourk_i, rest_fourk_i**2 * fourk_r ]])


     row += 1


time.sleep(0.2)

pro.setVolt(1,0)
pro.setVolt(2,0)
pro.setVolt(3,0)

time.sleep(0.2)




print(data)
fmt = '%s\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t'
np.savetxt(fname, data, fmt = '%s')


sys.stdout = old_stdout
log_file.close()
