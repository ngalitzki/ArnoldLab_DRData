import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm


def plotLoad(hdr, data, Zcol):
	#To choose which cold plate setting you would like to reduce axes
	Cval_arr = np.array([0.0,0.21213203,0.3, 0.36742346, 0.42426407, 0.47434165])

	#15, 11 sets MC and Still temps, haven't used much else
	Xcol = 15
	Ycol = 11
	#Set here or pass as arg for what you wnat on Z, usually power applied
#	Zcol = 8
	#Pick a CP power level
	Cval =5 
	
	#Make some units right
	if Zcol==8: convert = 1e3; units = ' (mW)'
	elif Zcol==9 or Zcol==10: convert = 1e6; units = ' (uW)' #1e3 for mW, 1e6 for uW
	elif Zcol>10: convert = 1e3; units = ' (mK)'
	
	#Enforce CP choice
	arr = data[(100*data[:,3]).astype(int)==np.int(100*Cval_arr[Cval])]
	print arr.shape
	
	#Plotting stuff
	fig, ax = plt.subplots(1,1, sharex=True, facecolor='white', figsize=(12,9))
	plt.xlabel(hdr[Xcol]+' (K)')
	plt.ylabel(hdr[Ycol]+' (K)')
	plt.xlim(0,0.25)
	plt.ylim(0.6,1.05)	
	x = arr[:, Xcol]
	y = arr[:, Ycol]
	z = arr[:, Zcol]*convert
	CS = plt.tripcolor(x,y,z)
	#Alternative color method I didn't like as much but kept around
#	ax[1].tricontourf(x,y,z, 5)
	plt.plot(x,y,'ko ')
#	ax[1].plot(x,y, 'ko ')
	#Ugly title line with possibly useful info
	plt.title('LOAD CURVE: Const P_cp = ' + np.str('%.0f'%(1e6*arr[0,9]))+' uW. ' +'Range T_cp: '+ np.str('%.0f'%(1e3*arr[:,13].min())) + ' to ' + np.str('%.0f'%(1e3*arr[:,13].max())) + ' mK')
	plt.grid()
	cb1 = plt.colorbar(CS)
	cb1.set_label(hdr[Zcol]+units)
	plt.show()
	return data

def main(fname):
	data = np.genfromtxt(fname)
	hdr = np.loadtxt(fname, dtype=str, comments='')[0,:]
	print hdr

	plotLoad(hdr, data, 8)
	plotLoad(hdr, data, 10)
	plotLoad(hdr, data, 13)

from sys import argv
if __name__ == "__main__":
	main(str(argv[1]))#, str(argv[2]), str(argv[3]), str(argv[4]))
