import visa
import numpy as np
import time
from datetime import datetime

fname = 'LoadCurve_Run1_Start20170811.txt'

rm = visa.ResourceManager()
print(rm.list_resources())

psup = rm.open_resource('USB0::0x05E6::0x2230::9102893::0::INSTR')
print(psup.query('*idn?'))

still_maxP = 18.0/1000 #18 mW 
cp_maxP = 0.9/1000 #900 uW
mc_maxP = 0.6/1000 #600 uW

still_steps = 6
cp_steps = 6
mc_steps = 6

still_p = np.linspace(0, still_maxP, num=still_steps)
cp_p = np.linspace(0, cp_maxP, cp_steps)
mc_p = np.linspace(0, mc_maxP, mc_steps)

still_r = 120
cp_r = 250
mc_r = 120

still_i = np.sqrt(still_p/still_r)
cp_i = np.sqrt(cp_p/cp_r)
mc_i = np.sqrt(mc_p/mc_r)

still_v = still_i * still_r
cp_v = cp_i*cp_r
mc_v = mc_i*mc_r

print('Still Vs: ', still_v)
print('CP Vs: ', cp_v)
print('MC Vs: ', mc_v)

#Columns: date time vs vc vm i... p... 
data=np.empty(((still_steps)*(cp_steps)*(mc_steps), 11), dtype=object)
#data[:] = np.nan
print('Data shape', data.shape)

row=0

for i, val in enumerate(still_v):
	print('Still being set to V, I, P:', val, still_i[i], still_p[i])	 
	psup.write('inst:sel ch1')
	psup.write('volt '+np.str(val))

	for j, cpval in enumerate(cp_v):
		print('CP being set to V, I, P:', cpval, cp_i[j], cp_p[j])	 
		psup.write('inst:sel ch2')
		psup.write('volt '+np.str(cpval))
		

		for k, mcval in enumerate(mc_v):
			print('MC being set to V, I, P:', mcval, mc_i[k], mc_p[k])	 
			psup.write('inst:sel ch3')
			psup.write('volt '+np.str(mcval))

			time.sleep(60*20)	

			psup.write('inst:sel ch1')
			rest_still_i = np.float(psup.query('meas:curr?'))
			psup.write('inst:sel ch2')
			rest_cp_i = np.float(psup.query('meas:curr?'))
			psup.write('inst:sel ch3')
			rest_mc_i = np.float(psup.query('meas:curr?'))
					
			print('Measured rest current', rest_still_i)
			
			#row = i*still_steps**2 + j*cp_steps +k
			print('Row check', row, i, j ,k)
			data[row, :] = np.array([[time.strftime('%d-%m-%y'), time.strftime('%X'), val, cpval, mcval,rest_still_i, rest_cp_i, rest_mc_i, rest_still_i**2 * still_r, rest_cp_i**2 * cp_r, rest_mc_i**2 * mc_r ]]) 
		
			row +=1
print(data)
fmt = '%s\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t'
np.savetxt(fname, data, fmt='%s')

psup.write('inst:sel ch1')
psup.write('volt 0.0')
psup.write('inst:sel ch2')
psup.write('volt 0.0')
psup.write('inst:sel ch3')
psup.write('volt 0.0')

psup.close()