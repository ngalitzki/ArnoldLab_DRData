import os, time, datetime
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
#import statsmodels.api as sm
import linecache as lc
import subprocess as sp


###############################################################################
###############################################################################
###############################################################################

class bluefors():

    def now():
        return str(datetime.datetime.now())[:-7].replace(':', '').replace('-', '').replace(' ', '-')

###############################################################################
###############################################################################
###############################################################################
    def brutalize_bluefors_log(self, bluefors_datafile, epoch = datetime.datetime.fromtimestamp(0)):
        '''
        - stupid BF log files are organized in folders according to date with a new one created each day...
          then by channel R and channel T, then inside the file: date, time, value
        - need to import all data from one day from all channels and give it unix timestamps
        '''


        self.bluefors_datafile = bluefors_datafile

        d = np.genfromtxt(bluefors_datafile, delimiter = 18, dtype = '|S21')
        temperatures = np.loadtxt(bluefors_datafile, delimiter = ',', usecols = (2))

        times = []

        for t in d[:, 0]:

            new_t = datetime.datetime.strptime(t, ' %d-%m-%y,%H:%M:%S')
            times.append(time.mktime(new_t.timetuple()))

        times = np.array(times)

        bluefors_data = np.transpose(np.array([times, temperatures]))

        return bluefors_data

###############################################################################
###############################################################################
###############################################################################
    def bluefors_mashup(self, bluefors_log_path, start_folder, stop_folder, plot_data = True):
        '''
        - if 'start_folder' and 'stop_folder' are left as 'None' this takes all BF data folders (one per date)
          in 'bluefors_log_path' and concatenates their data into dictionairies 'R_data' and 'T_data'.
        - if 'start_folder' and 'stop_folder' are specified you get a mahsup of everything between
          'start_folder' and 'stop_folder'.
        - if 'start_folder' is specified but 'stop_folder' is left as 'None' this brings everything after
          'start_folder' to the mashup party
        - oh, and you also get a sensible unix timestamp which is constructed in 'brutalize_bluefors_log', wooo!
        '''


        self.bluefors_log_path = bluefors_log_path
        self.start_folder = start_folder
        self.stop_folder = stop_folder

        # would be good to add functionality to detect which channels are actually active...
        # but we're not here for that fancy stuff, brute force baby!
        possible_channels = [1, 2, 3, 4, 5, 6, 7, 8]

        # this is just initialization
        channel_files = {}
        R_data = {}
        T_data = {}

        # more initialization...
        for ch in possible_channels:
            channel_files[ch] = {'R': [], 'T': []}
            R_data[ch] = {}
            T_data[ch] = {}

        # here we build a list of all the data files and their date folders that will get the mashup treatment

        folders = os.listdir(bluefors_log_path)
        folders = sorted(folders)


        if start_folder != None and stop_folder == None:

            print 'mashing up everything after', start_folder
            start_folder_index = folders.index(start_folder)
            folders = folders[start_folder_index:]

        elif start_folder != None and stop_folder != None:

            print 'mashing things up between {} and {}'.format(start_folder, stop_folder)
            start_folder_index = folders.index(start_folder)
            stop_folder_index = folders.index(stop_folder)
            folders = folders[start_folder_index:stop_folder_index+1]

        for folder in folders:

            files = os.listdir(bluefors_log_path + '/{}/'.format(folder))

            for f in files:

                if f[:2] == 'CH' and f[4] == 'R':
                    channel_files[int(f[2])]['R'].append(bluefors_log_path +'/{}/'.format(folder) + f)

                elif f[:2] == 'CH' and f[4] == 'T':
                    channel_files[int(f[2])]['T'].append(bluefors_log_path +'/{}/'.format(folder) + f)


        # now actually load the data
        for ch in channel_files.keys():

            bluefors_data = []

            for f in channel_files[ch]['R']:

                bluefors_data.append(self.brutalize_bluefors_log(f))

            if len(bluefors_data) != 0:

                R_data[ch] = np.concatenate(np.array(bluefors_data), axis = 0)

            bluefors_data = []

            for f in channel_files[ch]['T']:

                bluefors_data.append(self.brutalize_bluefors_log(f))

                T_data[ch] = np.concatenate(np.array(bluefors_data), axis = 0)

        if plot_data:

            plt.figure(figsize = (8,6))



            for ch in T_data.keys():

                try:
                    # convert unix time to hours since the first data point
                    # assuming this is the start of the run or something sensible like that...

                    t = (T_data[ch][:, 0] - T_data[ch][0, 0])
                    #/ 60. / 60.
                    plt.plot(t, T_data[ch][:, 1], label = 'CH {:.0f}'.format(ch))

                except TypeError:

                    print 'no data in channel', ch
                    pass

            plt.yscale('log')
            plt.xlabel('Time [hrs]')
            plt.ylabel('Temperature [K]')
            plt.legend()
            plt.grid(color = '.5')
            plt.tight_layout()
            plt.savefig('{}_full_run_all_channels.jpg'.format(folders[0].replace('-', '')), dpi = 150)


        mashed_bluefors_data = {'R': R_data, 'T': T_data}

        return mashed_bluefors_data

#################################################################################
#################################################################################
#################################################################################
    def load_bluefors_cal(self, bluefors_calpath, bluefors_calfiles, plot_calibrations = True):
        '''
        - pretty self-explanatory...saves a plot if you want it to...
        - should work well if you want to specify multiple files if done correctly
        '''

        self.bluefors_calpath = bluefors_calpath
        self.bluefors_calfiles = bluefors_calfiles

        bluefors_cal_data = {}

        print 'loading data from BF cal file:', bluefors_calfiles

        for f in bluefors_calfiles:

            bluefors_cal_data[f] = {}

            data = np.loadtxt(bluefors_calpath + f, skiprows = 9, usecols = (1, 2))

            # stupid units in BF sensor file are log(Ohms)/Kelvin...*faceplam*
            R = 10**(data[:, 0])
            bluefors_cal_data[f]['R'] = R
            bluefors_cal_data[f]['T'] = data[:, 1]

        if plot_calibrations:

            plt.figure(figsize = (8,6))

            for k in bluefors_cal_data.keys():
                plt.plot(bluefors_cal_data[k]['T'], bluefors_cal_data[k]['R'], linewidth = 2, label = k[:-4])

            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel('Temperature [K]')
            plt.ylabel('Resistance [$\Omega$]')
            plt.title('Bluefors Calibration Curves')
            plt.grid(color = '.5')
            plt.legend(framealpha = 1)
            plt.tight_layout()
            #plt.savefig('{}_bluefors_cal_curves.jpg'.format(now()[:9]), dpi = 150)
            plt.savefig('{}_bluefors_cal_curves.jpg'.format(bluefors_calfiles[0]), dpi = 150)

        return bluefors_cal_data

#################################################################################
#################################################################################
#################################################################################
    def align_standard_and_uncal_data(self,bluefors_calpath, bluefors_calfiles, mashed_bluefors_data, bluefors_standard_channel,
                                      srs_datafile_fullpath_fullpath, mintemp, maxtemp, all_plots = True):
        '''
        - "master" function to make cal files. identifies measured points closest to the points in the standard's calibraiton file
          since these will have the lowest measurement error. then aligns these measured points with the uncalibrated data

        - this assumes every column in the raw units file from the SRS logger is a sensor that needs calibration
          (except the time column of course...)
        - 'bluefors_calpath' is the root folder containing the BF calibration files
        - 'buefors_calfiles' should be a list of length ONE containing the name of the calibration file of the standard
        - 'bluefors_standard_channel' specifies the channel in the BF LS332 where the calibration standard is located
        - 'maxtemp' and 'mintemp' should be specified to help chop thermometry glitches from ranging difficulties
        - 'bluefors_calfiles' is a list of just the filenames (no path) of the calibration files
        - 'srs_datafile_fullpath_fullpath' is the full path to the raw units SRS data file
        '''

        # load the BF calibration for the sensor we will use as our standard
        standard_calibration = self.load_bluefors_cal(bluefors_calpath, bluefors_calfiles)
        standard_calibration = standard_calibration[bluefors_calfiles[0]]

        R_data = mashed_bluefors_data['R']
        T_data = mashed_bluefors_data['T']

        # the BF log from the LS332 seems to rail at 0.0 K if the channel is open or disabled
        # so this chops out data where T is read as 0.0 K, i.e. where the data is invalid
        valid_indices_all = np.where(T_data[bluefors_standard_channel][:, 1] != 0.0)[0]
        valid_T_data_all = T_data[bluefors_standard_channel][valid_indices_all, :]
        valid_R_data_all = R_data[bluefors_standard_channel][valid_indices_all, :]

        # this gathers calibration data across the whole run based on the premise that the data points closest
        # to the calibration points are the best. this makes some sense because statistically it is more likely
        # for the measured datum to be closest to the calibrated datum when the temperature is moving the slowest.
        # in the event of multiple crossings of any given calibrated datum this should (hopefully) select the best
        # measured datum for creating calibration curves. that being said, adding filters to preferentially select
        # points based on the slope around the measured datum would likely be better...
        minindices_all = []
        standard_R_all = []
        standard_T_all =  []

        for i in range(len(standard_calibration['T'])):

            # only use data within our specified max and min T
            if standard_calibration['T'][i] < maxtemp and standard_calibration['T'][i] > mintemp:
                diff_all = np.abs(valid_T_data_all[:, 1] - standard_calibration['T'][i])
                minindex_all = np.where(diff_all == np.min(diff_all))[0][0]
                minindices_all.append(minindex_all)
                standard_R_all.append(standard_calibration['R'][i])
                standard_T_all.append(standard_calibration['T'][i])

        # standard_R_all and standard_T_all are the values to use from the calibration file
        # measured_R_all and measured_T_all are the values measured during the run that are closest to the calibrated data
        standard_R_all = np.array(standard_R_all)
        standard_T_all = np.array(standard_T_all)
        measured_R_all = np.sort(valid_R_data_all[minindices_all, 1])
        measured_T_all = np.sort(valid_T_data_all[minindices_all, 1])[::-1]
        bluefors_times_all = valid_R_data_all[minindices_all, 0]
        R_diff_all = standard_R_all - measured_R_all
        T_diff_all = standard_T_all - measured_T_all

        dTdt_all = []
        dRdt_all = []

        for i in range(measured_T_all.shape[0] - 1):

            dTdt_all.append((measured_T_all[i + 1] - measured_T_all[i]) / (bluefors_times_all[i + 1] - bluefors_times_all[i]))
            dRdt_all.append((measured_R_all[i + 1] - measured_R_all[i]) / (bluefors_times_all[i + 1] - bluefors_times_all[i]))

        dTdt_all = np.array(dTdt_all)
        dRdt_all = np.array(dRdt_all)

        t1 = (valid_T_data_all[:, 0] - valid_T_data_all[0, 0]) / 60. / 60.
        t2_all = (bluefors_times_all - valid_T_data_all[0, 0]) / 60. / 60.

        # this plot shows selected points using the entire "run" dataset
        plt.figure(figsize = (8,6))
        plt.yscale('log')
        plt.plot(t1, valid_T_data_all[:, 1])
        plt.scatter(t2_all, measured_T_all, marker = 'x', color = 'r')
        plt.xlabel('Time [hrs]')
        plt.ylabel('Temperature [K]')
        plt.title('Selected Points: Entire Run')
        plt.grid(color = '.5')
        plt.tight_layout()
        #plt.show()
        plt.savefig('full_run_and_selected_points_all.jpg', dpi = 150)

        # this helps the script chop the data into 3 regimes: all of it, cooldown only, and warmup only
        t_basetemp = input('enter time in hrs when base temp was reached')
        t_warmup = input('enter time in hours when warmup was started from base temp')

        minindices_cooldown = []
        minindices_warmup = []
        standard_R_cooldown = []
        standard_R_warmup = []
        standard_T_cooldown =  []
        standard_T_warmup = []

        # chop out outlandish temperatures so the script doesn't break
        cooldown_indices = np.where(t1 < t_basetemp)[0]
        warmup_indices = np.where(t1 > t_warmup)[0]

        valid_R_data_cooldown = valid_R_data_all[cooldown_indices]
        valid_T_data_cooldown = valid_T_data_all[cooldown_indices]
        valid_R_data_warmup = valid_R_data_all[warmup_indices]
        valid_T_data_warmup = valid_T_data_all[warmup_indices]

        # this loop gathers data from the entire run that coincides with the data in the
        # standard's calibration file (lowest measurement error at these points)
        for i in range(len(standard_calibration['T'])):

            # only use data within our specified max and min T
            if standard_calibration['T'][i] < maxtemp and standard_calibration['T'][i] > mintemp:

                diff_cooldown = np.abs(valid_T_data_cooldown[:, 1] - standard_calibration['T'][i])
                minindex_cooldown = np.where(diff_cooldown == np.min(diff_cooldown))[0][0]
                minindices_cooldown.append(minindex_cooldown)
                standard_R_cooldown.append(standard_calibration['R'][i])
                standard_T_cooldown.append(standard_calibration['T'][i])

                diff_warmup = np.abs(valid_T_data_warmup[:, 1] - standard_calibration['T'][i])
                minindex_warmup = np.where(diff_warmup == np.min(diff_warmup))[0][0]
                minindices_warmup.append(minindex_warmup)
                standard_R_warmup.append(standard_calibration['R'][i])
                standard_T_warmup.append(standard_calibration['T'][i])

        # grind away with the same procedure for COOLDOWN and WARMUP
        standard_R_cooldown = np.array(standard_R_cooldown)
        standard_T_cooldown = np.array(standard_T_cooldown)
        measured_R_cooldown = np.sort(valid_R_data_cooldown[minindices_cooldown, 1])
        measured_T_cooldown = np.sort(valid_T_data_cooldown[minindices_cooldown, 1])[::-1]
        bluefors_times_cooldown = valid_R_data_cooldown[minindices_cooldown, 0]
        R_diff_cooldown = standard_R_cooldown - measured_R_cooldown
        T_diff_cooldown = standard_T_cooldown - measured_T_cooldown

        standard_R_warmup = np.array(standard_R_warmup)
        standard_T_warmup = np.array(standard_T_warmup)
        measured_R_warmup = np.sort(valid_R_data_warmup[minindices_warmup, 1])
        measured_T_warmup = np.sort(valid_T_data_warmup[minindices_warmup, 1])[::-1]
        bluefors_times_warmup = valid_R_data_warmup[minindices_warmup, 0]
        R_diff_warmup = standard_R_warmup - measured_R_warmup
        T_diff_warmup = standard_T_warmup - measured_T_warmup

        t1_cooldown = (valid_T_data_cooldown[:, 0] - valid_T_data_cooldown[0, 0]) / 60. / 60.
        t2_cooldown = (bluefors_times_cooldown - valid_T_data_cooldown[0, 0]) / 60. / 60.

        t1_warmup = (valid_T_data_warmup[:, 0] - valid_T_data_warmup[0, 0]) / 60. / 60.
        t2_warmup = (bluefors_times_warmup - valid_T_data_warmup[0, 0]) / 60. / 60.

        # this plot shows the points selected using only the COOLDOWN data
        plt.figure(figsize = (8,6))
        plt.yscale('log')
        plt.plot(t1_cooldown, valid_T_data_cooldown[:, 1])
        plt.scatter(t2_cooldown, measured_T_cooldown, marker = 'x', color = 'r')
        plt.xlabel('Time [hrs]')
        plt.ylabel('Temperature [K]')
        plt.title('Selected Points: Cooldown')
        plt.grid(color = '.5')
        plt.tight_layout()
        plt.savefig('full_run_and_selected_points_cooldown.jpg', dpi = 150)

        # this plot shows the points selected using only the WARMUP data
        plt.figure(figsize = (8,6))
        plt.yscale('log')
        plt.plot(t1_warmup, valid_T_data_warmup[:, 1])
        plt.scatter(t2_warmup, measured_T_warmup, marker = 'x', color = 'r')
        plt.xlabel('Time [hrs]')
        plt.ylabel('Temperature [K]')
        plt.title('Selected Points: Warmup')
        plt.grid(color = '.5')
        plt.tight_layout()
        plt.savefig('full_run_and_selected_points_warmup.jpg', dpi = 150)

        # this plot compares the calibration file and the measured curve for the standard
        plt.figure(figsize = (8,6))
        plt.xscale('log')
        plt.yscale('log')
        plt.plot(measured_T_all, measured_R_all, color = 'b', linewidth = 1, label = 'measurement')
        plt.plot(standard_T_all, standard_R_all, color = 'r', linewidth = 4, label = 'calibration', alpha = .3)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Resistance [$\Omega$]')
        plt.title('Calibration vs Measured Data for Standard')
        plt.legend()
        plt.grid(color = '.5')
        plt.savefig('calibration_file_vs_measured_data.jpg', dpi = 150)

        # this plot shows both the relative R discrepancy and absolute T discrepancy between the
        # calibration file and the measured data using the entire dataset

        # ENTIRE RUN
        plt.figure(figsize= (14,6))
        plt.subplot(121)
        plt.xscale('log')
        plt.plot(standard_T_all, R_diff_all/measured_R_all, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Fractional Discrepancy, $\Delta$R/R')
        plt.title('Fractional Discrepancy to Calibrated Resistances: Entire Run')
        plt.grid(color = '.5')
        plt.subplot(122)
        plt.xscale('log')
        plt.plot(standard_T_all, T_diff_all, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Discrepancy, $\Delta$K [K]')
        plt.title('Proximity to Calibrated Temperatures : Entire Run')
        plt.grid(color = '.5')
        plt.savefig('relative_R_and_T_discrepancy_all.jpg', dpi = 150)

        # COOLDOWN
        plt.figure(figsize= (14,6))
        plt.subplot(121)
        plt.xscale('log')
        plt.plot(standard_T_cooldown, R_diff_cooldown/measured_R_cooldown, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Fractional Discrepancy, $\Delta$R/R')
        plt.title('Fractional Discrepancy to Calibrated Resistances: Cooldown')
        plt.grid(color = '.5')
        plt.subplot(122)
        plt.xscale('log')
        plt.plot(standard_T_cooldown, T_diff_cooldown, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Discrepancy, $\Delta$K [K]')
        plt.title('Proximity to Calibrated Temperatures: Cooldown')
        plt.grid(color = '.5')
        plt.savefig('relative_R_and_T_discrepancy_cooldown.jpg', dpi = 150)

        # WARMUP
        plt.figure(figsize= (14,6))
        plt.subplot(121)
        plt.xscale('log')
        plt.plot(standard_T_warmup, R_diff_warmup/measured_R_warmup, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Fractional Discrepancy, $\Delta$R/R')
        plt.title('Relative Discrepancy to Calibrated Resistances: Warmup')
        plt.grid(color = '.5')
        plt.subplot(122)
        plt.xscale('log')
        plt.plot(standard_T_warmup, T_diff_warmup, linewidth = 2)
        plt.xlabel('Temperature [K]')
        plt.ylabel('Discrepancy, $\Delta$K [K]')
        plt.title('Proximity to Calibrated Temperatures: Warmup')
        plt.grid(color = '.5')
        plt.savefig('relative_R_and_T_discrepancy_warmup.jpg', dpi = 150)

        plt.figure(figsize = (14,6))
        plt.subplot(121)
        plt.plot(measured_T_all[:-1], dTdt_all)
        plt.xscale('log')
        plt.xlabel('Temperature [K]')
        plt.ylabel('$\dot{T}$ [K/s]')
        plt.title('$\dot{T}$: Entire Run')
        plt.grid(color ='.5')
        plt.subplot(122)
        plt.plot(measured_T_all[:-1], dRdt_all)
        plt.xscale('log')
        plt.xlabel('Resistance [$\Omega$]')
        plt.ylabel('$\dot{R}$ [$\Omega$/s]')
        plt.title('$\dot{R}$: Entire Run')
        plt.grid(color ='.5')
        plt.tight_layout()

        # now load the SRS data which contains the uncalibrated sensor data
        srs_data = np.loadtxt(srs_datafile_fullpath_fullpath, delimiter =  ',', skiprows = 5)

        # this assumes you were smart enough to setup the SRS so that the column headers are the serial
        # numbers of the uncalibrated sensors...
        srs_sensor_names = lc.getline(srs_datafile_fullpath_fullpath, 4).rstrip()
        srs_sensor_names = np.array(srs_sensor_names.split(','))[1:]

        # now we need to find where the SRS timestamp coincides with the BF timestamp for the data selected
        # for use in creating the calibration curves for the uncalibrated sensors. then we can just grab the
        # R data at those points

        # ENTIRE RUN
        minindices_all = []

        for i in range(len(bluefors_times_all)):

            diff_all = np.abs(srs_data[:, 0] - bluefors_times_all[i])
            indices_all = np.where(diff_all == np.min(diff_all))[0][0]
            minindices_all.append(indices_all)

        srs_times_all = np.array(srs_data[minindices_all, 0])
        uncal_R_all = np.sort(np.array(srs_data[minindices_all, 1:]), axis = 0)

        plt.figure(figsize = (8,6))

        for i in range(len(srs_sensor_names)):

            plt.plot(measured_T_all, uncal_R_all[:, i], label = srs_sensor_names[i])

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Temperature [K]')
        plt.ylabel('Resistance [$\Omega$]')
        plt.title('Output Calibration Curves: Entire Run')
        plt.legend(framealpha = 1)
        plt.grid(color = '.5')
        plt.tight_layout()
        plt.savefig('test_entire.jpg',dpi=150)

        # COOLDOWN
        minindices_cooldown = []

        for i in range(len(bluefors_times_cooldown)):

            diff_cooldown = np.abs(srs_data[:, 0] - bluefors_times_cooldown[i])
            indices_cooldown = np.where(diff_cooldown == np.min(diff_cooldown))[0][0]
            minindices_cooldown.append(indices_cooldown)

        srs_times_cooldown = np.array(srs_data[minindices_cooldown, 0])
        uncal_R_cooldown = np.sort(np.array(srs_data[minindices_cooldown, 1:]), axis = 0)

        plt.figure(figsize = (8,6))

        for i in range(len(srs_sensor_names)):

            plt.plot(measured_T_cooldown, uncal_R_cooldown[:, i], label = srs_sensor_names[i])

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Temperature [K]')
        plt.ylabel('Resistance [$\Omega$]')
        plt.title('Output Calibration Curves: Cooldown')
        plt.legend(framealpha = 1)
        plt.grid(color = '.5')
        plt.tight_layout()
        plt.savefig('test_cooldown.jpg',dpi=150)

        # WARMUP
        minindices_warmup = []

        for i in range(len(bluefors_times_warmup)):

            diff_warmup = np.abs(srs_data[:, 0] - bluefors_times_warmup[i])
            indices_warmup = np.where(diff_warmup == np.min(diff_warmup))[0][0]
            minindices_warmup.append(indices_warmup)

        srs_times_warmup = np.array(srs_data[minindices_warmup, 0])
        uncal_R_warmup = np.sort(np.array(srs_data[minindices_warmup, 1:]), axis = 0)

        plt.figure(figsize = (8,6))

        for i in range(len(srs_sensor_names)):

            plt.plot(measured_T_warmup, uncal_R_warmup[:, i], label = srs_sensor_names[i])

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Temperature [K]')
        plt.ylabel('Resistance [$\Omega$]')
        plt.title('Output Calibration Curves: Warmup')
        plt.legend(framealpha = 1)
        plt.grid(color = '.5')
        plt.tight_layout()
        plt.savefig('test_warmup.jpg',dpi=150)

        # pack up the data
        data_all = {'valid_T': valid_T_data_all,
                    'valid_R': valid_R_data_all,
                    'uncal_R': uncal_R_all,
                    'uncal_T': measured_T_all,
                    'standard_R': standard_R_all,
                    'standard_T': standard_T_all,
                    'srs_times': srs_times_all,
                    'bluefors_times': bluefors_times_all,
                    'srs_sensor_names': srs_sensor_names}

        data_cooldown = {'valid_T': valid_T_data_cooldown,
                         'valid_R': valid_R_data_cooldown,
                         'uncal_R': uncal_R_cooldown,
                         'uncal_T': measured_T_cooldown,
                         'standard_R': standard_R_cooldown,
                         'standard_T': standard_T_cooldown,
                         'srs_times': srs_times_cooldown,
                         'bluefors_times': bluefors_times_cooldown,
                         'srs_sensor_names': srs_sensor_names}

        data_warmup = {'valid_T': valid_T_data_warmup,
                       'valid_R': valid_R_data_warmup,
                       'uncal_R': uncal_R_warmup,
                       'uncal_T': measured_T_warmup,
                       'standard_R': standard_R_warmup,
                       'standard_T': standard_T_warmup,
                       'srs_times': srs_times_warmup,
                       'bluefors_times': bluefors_times_warmup,
                       'srs_sensor_names': srs_sensor_names}


        aligned_data = {'all': data_all,
                        'cooldown': data_cooldown,
                        'warmup': data_warmup}

        return aligned_data

################################################################################
################################################################################
################################################################################
    def create_cal_file(self,aligned_data, data_subset, smooth_data = True, filter_box = 21, filter_order = 2, plot_cal_curves = True):
        '''
        - this uses the data from 'align_standard_and_uncal_data' to create the calibration file
        - 'data_subset' can take values 'all', 'cooldown', or 'warmup', to  specify which slicing you want
        - if 'smooth_data = True' this applies a Savitzky-Golay filter of width 'filter_box' (must be odd)
          and order 'filter_order'
        '''


        self.data_subset = data_subset
        self.aligned_data = aligned_data

        data = aligned_data[data_subset]
        sensor_names = data['srs_sensor_names']

        cal_data = {}

        for i in range(len(sensor_names)):

            cal_data[sensor_names[i]] = {}

            if smooth_data:

                new_R_cal = savgol_filter(data['uncal_R'][:, i], filter_box, filter_order)
                cal_data[sensor_names[i]]['R'] = new_R_cal

            else:

                new_R_cal = data['uncal_R'][:, i]
                cal_data[sensor_names[i]]['R'] = new_R_cal

            cal_data[sensor_names[i]]['T'] = data['uncal_T']

            plt.figure(figsize = (8,6))
            plt.xscale('log')
            plt.yscale('log')
            plt.plot(data['uncal_T'], data['uncal_R'][:, i], label = 'raw data', linewidth = 2)

            if smooth_data:

                plt.plot(data['uncal_T'], new_R_cal, label = 'smoothed data', linewidth = 2)

            plt.xlabel('Temperature [K]')
            plt.ylabel('Resistance [$\Omega$]')
            plt.title('{} Calibration Curve'.format(sensor_names[i]))
            plt.legend(framealpha = 1)
            plt.grid(color = '.5')
            plt.tight_layout()
            #plt.savefig(now()[:9] + '_{}_cal_curve.jpg'.format(sensor_names[i]), dpi = 150)
            plt.savefig('{}_cal_curve.jpg'.format(sensor_names[i]), dpi = 150)

            #header = sensor_names[i] + ' calibration file, created ' + now() + '\nTemperature\tResistance\n\t\t[K]\t\t\t\t[Ohms]\n'
            #new_cal_data = np.flipud(np.transpose(np.array([data['uncal_T'], new_R_cal])))
            #np.savetxt(now()[:9] + '_{}_cal.txt'.format(sensor_names[i]), new_cal_data, header = header, fmt = '%.8e')
            #np.savetxt('test_cal.txt', new_cal_data, header = header, fmt = '%.8e')


        return cal_data
