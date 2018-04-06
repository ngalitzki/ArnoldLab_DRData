from bluefors_utils import bluefors
import numpy as np

bf = bluefors()

bluefors_log_path = '/home/arnoldlabws2/ArnoldLab_DRData/bluefors_temp_logs_raw'
#bluefors_log_path = '/Users/joeseibert/Google Drive UCSD/Research/ArnoldLab_DRData'

bluefors_data_start = '18-03-22'
bluefors_data_stop = '18-03-23'

bluefors_calpath = '/home/arnoldlabws2/ArnoldLab_DRData/sensors/'
bluefors_calfiles = ['R10250.340']
bluefors_standard_channel = 6

srs_datafile = '/home/arnoldlabws2/ArnoldLab_DRData/180321_dr_thermo_cal/Data/20180322-144740RAW.txt'


mashed_bluefors_data = bf.bluefors_mashup(bluefors_log_path,bluefors_data_start,bluefors_data_stop)

#bluefors_cal_data = bf.load_bluefors_cal(bluefors_calpath,bluefors_calfiles)



aligned_data = bf.align_standard_and_uncal_data(bluefors_calpath,bluefors_calfiles,mashed_bluefors_data,bluefors_standard_channel,srs_datafile,0.0,100.0)

cal_data = bf.create_cal_file(aligned_data,'all')
