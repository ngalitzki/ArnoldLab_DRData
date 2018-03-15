import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import time
import random
farr = np.empty(())
index=0

#Needed to convert the log file data from a time stamp to seconds, essentially used for plotting so not entirely necessary....
def str2timestamp(timestr, epoch=datetime.fromtimestamp(0)):
    """Convert local time string into seconds since epoch (float)."""
    time = datetime.strptime(timestr, '%H:%M:%S')
    return time

#def str2datestamp(timestr, epoch=datetime.fromtimestamp(0)):
 #   """Convert local time string into seconds since epoch (float)."""
  #  date = datetime.strptime(timestr, ' %y-%m-%d')
    #I don't include the date info so I just subtract the baseline date
	#would need to modify to allow log files from multiple days
    #return (dt - datetime(1900,1,1)).total_seconds()
   # return date


def fopener(fname, dtype):
	rawdata = np.genfromtxt(fname, converters= {1: str2timestamp}, dtype=object)
	data = rawdata[:, 1:rawdata.shape[1]]
	for i, row in enumerate(rawdata):
		if dtype: date = datetime.strptime(row[0], '%Y-%m-%d')
		else: 
			date = datetime.strptime(row[0], '%d-%m-%y')
#			dt = random.randint(0,59)		
#			date = date.replace(month=date.month-1, day=date.day+7, minute=dt)
		data[i,0] = data[i,0].replace(year=date.year, month=date.month, day=date.day)	
	return data

#The fun bit
def main(psup_file, ls_file, fname):
	psup_arr = fopener(psup_file, 0)
	ls_arr = fopener(ls_file, 1)

	data = np.empty((psup_arr.shape[0], psup_arr.shape[1]+6), dtype=object)
	data[:, 0:psup_arr.shape[1]] = psup_arr[:,:]
	print data[0, :]
	for i, row in enumerate(psup_arr):
		dt_arr = row[0] - ls_arr[:,0]
		helper = np.vectorize(lambda x: x.total_seconds())
		#print np.min(np.abs(helper(dt_arr)))
		cut_arr = ls_arr[np.logical_and(helper(dt_arr)>0, helper(dt_arr)<300)]
		still_arr = cut_arr[:,1].astype(np.float)
		cp_arr = cut_arr[:,3].astype(np.float)
		mc_arr = cut_arr[:,2].astype(np.float)
		data[i,row.shape[0] : row.shape[0]+6] = np.array([np.mean(still_arr), np.std(still_arr), np.mean(cp_arr), np.std(cp_arr), np.mean(mc_arr), np.std(mc_arr)])
	print data[0, :]
	#	print psup_arr[helper(dt_arr)<60*60]		
	#Save to text
	hdr_str = '#time v_s v_c v_m i_s i_c i_m p_s p_c p_m T_s sT_s T_c sT_c T_m sT_m'
	np.savetxt(fname, data, fmt='%s', header=hdr_str)

	plt.plot(data[:,9], data[:,14].astype(np.float), 'o')
	plt.xlabel('time')
	plt.ylabel('T')
	plt.title('T test')
	plt.show()
	
	return data

from sys import argv
if __name__ == "__main__":
	main(str(argv[1]), str(argv[2]), str(argv[3]))#, str(argv[4]))
