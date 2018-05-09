import time
import numpy as np
import sys
from datetime import datetime

from prologixInterface import prologixInterface
from psuInterface import psuInterface

#old_stdout = sys.stdout
#log_file = open('Run1.log', 'w')
#sys.stdout = log_file
fname = 'LoadCurve_Run1_Start20170811.txt'

#pro = prologixInterface()
pro = psuInterface(1)
print pro.identify()

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

print('4K Vs: ', fourk_v)
print('MC Vs: ', mc_v)

print type(fourk_v[2])
test1 = str(fourk_v[2])
print type(test1)

data=np.empty([(fourk_steps*mc_steps), 8], dtype=object)

print('Data shape', data.shape)

row=0

wtime = 1
#time.sleep(60*60)


for i, fourkval in enumerate(fourk_v):
     print('4K being set to V, I, P: ', fourkval, fourk_i[i], fourk_p[i])
     pro.setVolt(1,fourkval/2)
     pro.setVolt(2,fourkval/2)


     for j, mcval in enumerate(mc_v):
         print('MC being set to V, I, P: ', mcval, mc_i[j], mc_p[j])
         pro.setVolt(3,mcval)

         if row != 0 and mcval ==0.0:
           time.sleep(wtime)
           print('NOTE: special mc wait time')
         time.sleep(wtime)


         rest_fourk_i = np.float(pro.getCurr(1))
         rest_mc_i = np.float(pro.getCurr(3))

         print('Measured rest current', rest_fourk_i)

         print('Row check', row, i, j)
         data[row, :] = np.array([[time.strftime('%d-%m-%y'), time.strftime('%X'), fourkval, mcval, rest_fourk_i, rest_mc_i, rest_fourk_i**2 * fourk_r, rest_mc_i**2 * mc_r ]])


         row += 1
        
        
time.sleep(5)

pro.setVolt(1,0)
pro.setVolt(2,0)
pro.setVolt(3,0)

time.sleep(5)




print(data)
fmt = '%s\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t'
np.savetxt(fname, data, fmt = '%s')


#sys.stdout = old_stdout
#log_file.close()
