from bluefors_utils import bluefors
import numpy as np

bf = bluefors()

bluefors_log_path = '/home/arnoldlabws2/ArnoldLab_DRData/bluefors_temp_logs_raw'
#bluefors_log_path = '/Users/joeseibert/Google Drive UCSD/Research/ArnoldLab_DRData'

bluefors_data_start = '18-04-12'
bluefors_data_stop = '18-04-14'

mashed_bluefors_data = bf.bluefors_mashup(bluefors_log_path,bluefors_data_start,bluefors_data_stop)

temp_data = mashed_bluefors_data['T']

final_T_data = {}


for ch in temp_data.keys():

    if np.size(temp_data[ch]) != 1:
        final_T_data[ch] = temp_data[ch]


header = 'UCSD DR Cooldown data \nTime\tTemperature \n(s)\t(K)'

np.savetxt('{}_40K.txt'.format(bluefors_data_start.replace("-","")), final_T_data[1], header = '40K Stage\n' + header)
np.savetxt('{}_4K.txt'.format(bluefors_data_start.replace("-","")), final_T_data[2], header = '4K Stage\n' + header)
np.savetxt('{}_Still.txt'.format(bluefors_data_start.replace("-","")), final_T_data[5], header = 'Still Stage\n' + header)
np.savetxt('{}_CP.txt'.format(bluefors_data_start.replace("-","")), final_T_data[8], header = 'Cold Plate\n' + header)
np.savetxt('{}_MC.txt'.format(bluefors_data_start.replace("-","")), final_T_data[6], header = 'Mixing Chamber\n' + header)
