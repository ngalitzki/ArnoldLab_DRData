import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import time
farr = np.empty(())
index=0

#Needed to convert the log file data from a time stamp to seconds, essentially used for plotting so not entirely necessary....
def str2timestamp(timestr, epoch=datetime.fromtimestamp(0)):
    """Convert local time string into seconds since epoch (float)."""
    fullstr=farr[index]+' ' +timestr
    time = datetime.strptime(fullstr, '%y-%m-%d %H:%M:%S')
    return time

#def str2datestamp(timestr, epoch=datetime.fromtimestamp(0)):
 #   """Convert local time string into seconds since epoch (float)."""
  #  date = datetime.strptime(timestr, ' %y-%m-%d')
    #I don't include the date info so I just subtract the baseline date
	#would need to modify to allow log files from multiple days
    #return (dt - datetime(1900,1,1)).total_seconds()
   # return date


#The fun bit
def main(fname):
	global farr
	farr = np.array(['17-08-10', '17-08-11', '17-08-12','17-08-13','17-08-14','17-08-15',])
	charr = np.array(['Flowmeter ', 'CH5 T ', 'CH6 T ', 'CH8 T '])

	#Load some files!
	hdr_str='#Date time Flowmeter StillT MCT CPT'
	for k, name in enumerate(farr):
		global index
		index=k
		flist = np.empty((charr.shape[0],), dtype=object)
		
		#Make file names
		for j, chan in enumerate(charr):
			flist[j] = name+'/'+chan+name+'.log'

		#Iterate through files, nested so each day's data is merged then all the days are merged
		for i, name in enumerate(flist):
			if i==0:
				chdata = np.genfromtxt(name, delimiter=',', usecols=(1,2), skip_footer=1, converters={1: str2timestamp}, dtype = object)
				length = chdata.shape[0]
				continue
			else:
				arr = np.genfromtxt(name, delimiter=',', usecols=(2,), skip_footer=1, dtype=object)
				#Annoying sequence to deal with the flowmeter sampling at a slightly different time resulting in a 2 or 3 point discrepency.
				diff = arr.shape[0]-length
				
				if diff > 0: arr = arr[0:arr.shape[0]-diff, :]
				elif diff < 0: chdata = chdata[0:chdata.shape[0]-diff,:] 
			chdata = np.concatenate((chdata,np.transpose(np.array([arr]))), axis=1)
			 
		if k==0: alldata = chdata
		else: alldata = np.concatenate((alldata,chdata), axis=0) 
	
	#Save to text
	np.savetxt(fname, alldata, fmt='%s', header=hdr_str)

	print alldata[:,1].astype(np.float)
	plt.plot(alldata[:,0], alldata[:,1].astype(np.float))
	plt.xlabel('time')
	plt.ylabel('T')
	plt.title('T test')
	plt.show()
	#Some useful plots to see whats up
#	plotxVy(calT[:,0], calT[:,1], 'time(s)', 'T(K)', 'Cal TOD')
#	plotxVy(newR[:,0], np.log10(newR[:,1]), 'time(s)', 'log R(Ohm?)', 'unCal TOD')
#	plotxVy(calib[:,1], calib[:,2], 'R(Log Ohm)', 'T(K)', 'Cal File')
#	plotxVy(calT[:,1], np.log10(newR[:,1]), 'cal T(K)', 'new R(log Ohm)', 'Interpolator inputs')
	
	return alldata

from sys import argv
if __name__ == "__main__":
	main(str(argv[1]))#, str(argv[2]), str(argv[3]), str(argv[4]))
