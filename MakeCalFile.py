import numpy as np
import scipy.interpolate as scint
from datetime import datetime
from matplotlib import pyplot as plt
from scipy.interpolate import LinearNDInterpolator as LNDI
from scipy.interpolate import interp1d as i1d

def writefile(data, name):
	#NEEDS a serial number, could make this an input variable easily
	SN = 'R10287'

	#HEADER copied from Bluefors file, only change is SN, should double check sensor model
	hdr = 'Sensor Model: \tRU-1000-BF0.007\n'+\
		'Serial Number:\t'+SN+'\n'+\
		'Data Format: \t4 \t(Log Ohms/Kelvin)\n'+\
		'SetPoint Limit: \t100.0 \t(Kelvin)\n'+\
		'Temperature coefficient: \t1 \t(Negative)\n'+\
		'Number of Breakpoints:	\t198\n'+\
		'\n'+\
		'No. \tUnits \tTemperature (K)\n'
	
	#Setup data file to write by adding a Number column
	no = np.arange(1,data.shape[0]+1, dtype=int)
	fdata = np.empty([data.shape[0],3])
	fdata[:,0] = no
	fdata[:,1:3] = data
	#Save file in same format as Bluefors with decimal places defined
	np.savetxt(name, fdata, header=hdr, delimiter='\t', comments='', fmt=['%d','%.5f' ,'%.3f'])
	return fdata

#Basic 1d linear interpolator, extrapolates beyond input range which is bad if you don't have data that covers the required range well
def interpolate(T, R):
	points = zip(T,R)
	points = sorted(points, key=lambda point: point[0])
	T1, R1 = zip(*points)
	plotxVy(T1, R1,'cal T(K)', 'new R(log Ohm)', 'Interpolator inputs')
	return i1d(T1,R1, fill_value='extrapolate')

#Super basic plot function used to check various points of the code
def plotxVy(x, y, xl, yl, title):
	plt.plot(x, y)
	plt.xlabel(xl)
	plt.ylabel(yl)
	plt.title(title)
	plt.show()
	return 1

#Needed to convert the log file data from a time stamp to seconds, essentially used for plotting so not entirely necessary....
def str2timestamp(timestr, epoch=datetime.fromtimestamp(0)):
    """Convert local time string into seconds since epoch (float)."""
    dt = datetime.strptime(timestr, '%H:%M:%S')
    #I don't include the date info so I just subtract the baseline date
	#would need to modify to allow log files from multiple days
    return (dt - datetime(1900,1,1)).total_seconds()

#The fun bit
def main(calTfile, newRfile, calibFile, fname):
	
	#Load some files, ignores date column!
	calT = np.loadtxt(calTfile, delimiter=',', usecols=(1,2), converters={1: str2timestamp})
	newR = np.loadtxt(newRfile, delimiter=',', usecols=(1,2), converters={1: str2timestamp})
	calib = np.loadtxt(calibFile, skiprows=9)

	#Need time cut on data to isolate good readings
	tmin= 0
	tmax = 80000
	calT = calT[ calT[:,0] < tmax]; calT = calT[ calT[:,0] > tmin]
	newR = newR[ newR[:,0] < tmax]; newR = newR[ newR[:,0] > tmin]
	
	#Some useful plots to see whats up
#	plotxVy(calT[:,0], calT[:,1], 'time(s)', 'T(K)', 'Cal TOD')
#	plotxVy(newR[:,0], np.log10(newR[:,1]), 'time(s)', 'log R(Ohm?)', 'unCal TOD')
#	plotxVy(calib[:,1], calib[:,2], 'R(Log Ohm)', 'T(K)', 'Cal File')
#	plotxVy(calT[:,1], np.log10(newR[:,1]), 'cal T(K)', 'new R(log Ohm)', 'Interpolator inputs')
	
	#Create the interpolation function
	func = interpolate(calT[:,1], np.log10(newR[:,1]))
	#Make a single array for the new calibrated data
	data = np.concatenate((np.array([func(calib[:,2])]).T, np.array([calib[:,2]]).T), axis=1)
	#Check that your new data looks right
	plotxVy(data[:,0], data[:,1], 'R (Log Ohm)', 'T(K)', 'New Cal File')
	
	#Make a new file
	writefile(data, fname)

	#Check that it accurately predicts temperatures
	newCal = np.loadtxt(fname, skiprows=9)
	newFunc = interpolate(newCal[:,1], newCal[:,2])
	checkT = newFunc(np.log10(newR[:,1]))
	plt.plot(newR[:,0], checkT, 'ro', newR[:,0], calT[:,1], 'bs')
	plt.show()
	
	return data

from sys import argv
if __name__ == "__main__":
	main(str(argv[1]), str(argv[2]), str(argv[3]), str(argv[4]))
