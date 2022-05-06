from hmac import trans_36
from random import randint, sample
from unicodedata import name
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication


import numpy as np
import pandas as pd
import math
from gui import home, calib

import sys
import time
import random
from lib import data_aquisition
import lib.settings as settings
from lib.utils import *
from lib.data_aquisition import DataAcqusitionModule
from lib.datalogger import DataLoggerModule
from lib.repeated_timer import RepeatedTimer

CONFIG_REFERENCE_TEMP = 20.0

def round_to_n(x, n=2):
    if not x: return 0
    power = -int(math.floor(math.log10(abs(x)))) + (n - 1)
    factor = (10 ** power)
    return math.ceil(x * factor) / factor


class TempSensor():
    def __init__(self, sensor_name, tol):
        self.name = sensor_name
        self.raw_val = 0.0
        self.compensate = 0.0

        self.values = [0]
        self.ts = [0]
        self.mean = None
        self.std = None

        self.cal_values = []
        self.uncertainty_values = []
        self.uncertainty = None
        self.cal_ts = [0]
        self.cal_mean = None
        self.cal_std = None

        self.val = 0.0
        self.tol = tol

        self.fault = False

    def reinit(self):
        self.raw_val = 0.0
        self.compensate = 0.0

        self.values = [0]
        self.ts = [0]
        self.mean = None
        self.std = None

        self.cal_values = []
        self.uncertainty_values = []
        self.uncertainty = None
        self.cal_ts = [0]
        self.cal_mean = None
        self.cal_std = None

        self.fault = False

    def set_val(self, val):
        self.val = val - self.compensate


def check_sensors(*sensors):

    vals = []
    for s1 in sensors:
        vals_s1 = []
        for s2 in sensors:
            if s1 != s2:
                if abs(s1.val - s2.val) < s1.tol :
                    vals_s1.append(1)
                else:
                    vals_s1.append(0)
        vals.append(vals_s1) 

    df = pd.DataFrame(vals)
    #faulty sensors
    faults = df.loc[~(df!=0).any(axis=1)].index.values
    #print(faults)

    for i in range(len(sensors)):
        if i in faults:
            sensors[i].fault = True
        else:
            sensors[i].fault = False
    if faults.shape[0] > 0:
        return True
    else:
        return False

##################################################
# HOME LAYOUT
##################################################
class Home(QtWidgets.QMainWindow, home.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Home')

        self.calib_window = Calib(self)
        self.pending_log_condition = 0

        self.b_calib.clicked.connect(self.chg_screen_to_calib)
        self.b_back.clicked.connect(self.chg_screen_back)
        #self.b_test.clicked.connect(self.evt_test)
        

        self.b_connect.clicked.connect(self.evt_connect_acq)
        self.b_disconnect.clicked.connect(self.evt_disconnect_acq)
        self.cb_log_main.stateChanged.connect(self.evt_log_cond_changed)

        self.in_fault = False
        self.fault = False


    def evt_log_cond_changed(self):
        if (hasattr(self, 'worker') == False):
            print("Data Acquisition thread module doesn't exist.")
            self.l_home_info.setText("Data Acquisition thread module doesn't exist.")
            self.pending_log_condition = 1
        else:
            if self.cb_log_main.isChecked():
                self.worker.log_condition = 1
            else:
                self.worker.log_condition = 0

    def evt_disconnect_acq(self):
        if (hasattr(self, 'worker') == False):
            print("Data Acquisition thread module doesn't exist.")
            self.l_home_info.setText("Data Acquisition thread module doesn't exist.")
        else:
            if (hasattr(self.worker, 'logger') == True):
                self.worker.logger.disconnect()
            if (hasattr(self.worker, 'acq_module') == True):
                self.worker.acq_module.disconnect()
            
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()
            
            del self.worker
        self.s_main_status.setStyleSheet("background-color: regular gray")

    def evt_connect_acq(self):
        if (hasattr(self, 'worker') == False):
            IP = self.i_IP_acq_module.text()
            if IP == '':
                IP = None

            try:
                s_time = float(self.i_sample_time.text())
            except ValueError:
                print("Sample time is not correct.")
                self.l_home_info.setText("Sample time is not correct.")
                return
            self.l_home_info.setText("Data acquisition started.")
            self.worker = DataAcquisitionThread(IP=IP, sample_time=s_time, log_condition=self.pending_log_condition)


        self.worker.start()
        self.worker.worker_complete.connect(self.evt_data_acqusition_finished)
        self.worker.update_data.connect(self.evt_update_data)

        self.s_main_status.setStyleSheet("background-color: green")

    def evt_data_acqusition_finished(self, dct):
        QtWidgets.QMessageBox.information(self, "Done!","{}".format(dct["status"]))

    def evt_test(self):
        print("Test from Home.")

        #TS1.raw_val -= 20.0

    def evt_update_data(self, dct):
        self.nr_acq_data = dct["nr_acq_data"]
        #print("update_data_from_data_acq {}".format(dct))

        #TODO: remove except in production... Only used in simulations...
        try:
            TS1.set_val(dct["TS1"])
            TS2.set_val(dct["TS2"])
            TS3.set_val(dct["TS3"])
        except:
            print("Writing simulated values for TS.")
            self.l_home_info.setText("Writing simulated values for TS.")
            TS1.set_val(TS1.raw_val + random.random()*random.choice((-1, 1)))
            TS2.set_val(TS2.raw_val + random.random()*random.choice((-1, 1)))
            TS3.set_val(TS3.raw_val + random.random()*random.choice((-1, 1)))

        self.fault = check_sensors(TS1, TS2, TS3)


        if TS1.fault == True:
            self.l_TS1_val.setStyleSheet("background-color: red")
        else:
            self.l_TS1_val.setStyleSheet("background-color: white")
        if TS2.fault == True:
            self.l_TS2_val.setStyleSheet("background-color: red")
        else:
            self.l_TS2_val.setStyleSheet("background-color: white")
        if TS3.fault == True:
            self.l_TS3_val.setStyleSheet("background-color: red")
        else:
            self.l_TS3_val.setStyleSheet("background-color: white")
        

        self.l_TS1_val.setText('{0:.2f} °C'.format(round(TS1.val, 2)))
        self.l_TS2_val.setText('{0:.2f} °C'.format(round(TS2.val, 2)))
        self.l_TS3_val.setText('{0:.2f} °C'.format(round(TS3.val, 2)))


        TS1.ts.append(TS1.ts[-1]+1)
        TS1.values.append(TS1.val)

        TS2.ts.append(TS2.ts[-1]+1)
        TS2.values.append(TS2.val)

        TS3.ts.append(TS3.ts[-1]+1)
        TS3.values.append(TS3.val)

    def chg_screen_to_calib(self):
        print("Switching screen to Calib.")
        self.hide()
        self.calib_window.show()
        
        
        

    def chg_screen_back(self):
        print("Go to previous screen")

##################################################
# CALIBRAITON LAYOUT
##################################################
class Calib(QtWidgets.QMainWindow, calib.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Calib, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Calibration')

        self.home_window = parent
        self.pending_log_condition = 0
        
        self.TS1_mainPlot.canvas.axes.set_title('TS1', y=0.95)
        self.TS2_mainPlot.canvas.axes.set_title('TS2', y=0.95)
        self.TS3_mainPlot.canvas.axes.set_title('TS3', y=0.95)
        

        self.b_home.clicked.connect(self.chg_screen_to_home)
        self.b_start_calib.clicked.connect(self.start_calib)
        #self.b_test.clicked.connect(self.update_graph)
        self.b_back.clicked.connect(self.chg_screen_back)

        self.cb_log_calib.stateChanged.connect(self.evt_log_cond_changed)
        



    def update_graph(self):

        print("Updating graph")


        self.TS1_mainPlot.canvas.axes.clear()
        self.TS2_mainPlot.canvas.axes.clear()
        self.TS3_mainPlot.canvas.axes.clear()


        self.TS1_mainPlot.canvas.axes.plot(TS1.cal_ts, TS1.cal_values, 'b')
        self.TS1_mainPlot.canvas.draw()
        self.TS1_mainPlot.canvas.flush_events()
        self.TS2_mainPlot.canvas.axes.plot(TS2.cal_ts, TS2.cal_values, 'b')
        self.TS2_mainPlot.canvas.draw()
        self.TS2_mainPlot.canvas.flush_events()
        self.TS3_mainPlot.canvas.axes.plot(TS3.cal_ts, TS3.cal_values, 'b')
        self.TS3_mainPlot.canvas.draw()
        self.TS3_mainPlot.canvas.flush_events()

    def chg_screen_to_home(self):
        print("Switching screen to Home.")
        self.hide()
        self.home_window.show()

    def chg_screen_back(self):
        print("Go to previous screen.")

    def evt_log_cond_changed(self):
        if (hasattr(self, 'worker') == False):
            print("Data Acquisition thread module doesn't exist.")
            self.l_calib_info.setText("Data Acquisition thread module doesn't exist.")
            self.pending_log_condition = 1
        else:
            if self.cb_log_calib.isChecked():
                self.worker.log_condition = 1
            else:
                self.worker.log_condition = 0

    def start_calib(self):
        print("Starting calibration.")
        self.l_calib_info.setText("Starting calibration.")
        try:
            nr_samples = int(self.i_calib_nr_samples.text())
        except ValueError:
            print("Number of samples is not correct.")
            self.l_calib_info.setText("Number of samples is not correct.")
            return
        try:
            ref_temp = float(self.i_calib_temp.text())
        except ValueError:
            print("Reference temperature is not correct.")
            self.l_calib_info.setText("Reference temperature is not correct.")
            return 
        
        self.worker = CalibrationThread(nr_samples=nr_samples, ref_temp=ref_temp, log_condition=self.pending_log_condition)
        self.l_calib_info.setText("Calibration started.")
        self.worker.start()
        self.worker.worker_complete.connect(self.evt_worker_finished)
        self.worker.worker_calib_complete.connect(self.evt_worker_calib_finished)

        self.worker.update_progress.connect(self.evt_update_progress)

        self.s_calib_status.setStyleSheet("background-color: green")
        

    def evt_worker_finished(self, dct):
        QtWidgets.QMessageBox.information(self, "Done!","{}".format(dct["status"]))

        self.s_calib_status.setStyleSheet("background-color: regular gray")
        self.update_graph()

        self.l_TS1_mean.setText(str(round(TS1.cal_mean, 2)))
        self.l_TS1_std.setText(str(round(TS1.cal_std, 2)))
        self.l_TS1_samples.setText(str(len(TS1.cal_values)))
        self.l_TS2_mean.setText(str(round(TS2.cal_mean, 2)))
        self.l_TS2_std.setText(str(round(TS2.cal_std, 2)))
        self.l_TS2_samples.setText(str(len(TS2.cal_values)))
        self.l_TS3_mean.setText(str(round(TS3.cal_mean, 2)))
        self.l_TS3_std.setText(str(round(TS3.cal_std, 2)))
        self.l_TS3_samples.setText(str(len(TS3.cal_values)))


        self.worker.quit()
        self.worker.wait()   
    def evt_worker_calib_finished(self,dct):
        QtWidgets.QMessageBox.information(self, "Done!","{}".format(dct["status"]))

        self.s_calib_status.setStyleSheet("background-color: regular gray")
        self.update_graph()

        self.l_TS1_mean.setText(str(round(TS1.cal_mean, 2)))
        self.l_TS1_std.setText(str(round(TS1.cal_std, 2)))
        self.l_TS1_samples.setText(str(len(TS1.cal_values)))
        self.l_TS2_mean.setText(str(round(TS2.cal_mean, 2)))
        self.l_TS2_std.setText(str(round(TS2.cal_std, 2)))
        self.l_TS2_samples.setText(str(len(TS2.cal_values)))
        self.l_TS3_mean.setText(str(round(TS3.cal_mean, 2)))
        self.l_TS3_std.setText(str(round(TS3.cal_std, 2)))
        self.l_TS3_samples.setText(str(len(TS3.cal_values)))

    def evt_update_progress(self, dct):

        #print("update_from_calibration_thread {}".format(val))
        self.l_calib_info.setText("Sample {}:{}.".format(dct['sample'], dct['nr_samples']))

        pass

##################################################
# CALIBRAITON THREAD
##################################################
class CalibrationThread(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(dict)
    worker_complete = QtCore.pyqtSignal(dict)
    worker_calib_complete = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None, nr_samples=10, ref_temp=20.0, log_condition=0):
        super(CalibrationThread, self).__init__(parent)
        
        self.logger = DataLoggerModule(mode='calib')

        self.ref_temperature = ref_temp
        self.log_condition = log_condition
        self.nr_samples = nr_samples

        TS1.reinit()
        TS2.reinit()
        TS3.reinit()

    def run(self):
        print("Calibration started.")

        first_sample = len(TS1.values)
        for nr_sample in range(0, self.nr_samples):
            while(len(TS1.values) == first_sample+nr_sample):
                pass
            dct = dict()
            dct['sample'] = nr_sample+1
            dct['nr_samples'] = self.nr_samples
            self.update_progress.emit(dct)




        TS1.cal_values = TS1.values[first_sample:first_sample+self.nr_samples+1]
        TS2.cal_values = TS2.values[first_sample:first_sample+self.nr_samples+1]
        TS3.cal_values = TS3.values[first_sample:first_sample+self.nr_samples+1]
        TS1.cal_ts = TS1.ts[0:self.nr_samples]
        TS2.cal_ts = TS2.ts[0:self.nr_samples]
        TS3.cal_ts = TS3.ts[0:self.nr_samples]

        TS1.cal_mean = np.array(TS1.cal_values).mean()
        TS1.cal_std = np.array(TS1.cal_values).std()
        TS2.cal_mean = np.array(TS2.cal_values).mean()
        TS2.cal_std = np.array(TS2.cal_values).std()
        TS3.cal_mean = np.array(TS3.cal_values).mean()
        TS3.cal_std = np.array(TS3.cal_values).std()

        #correct sensors discrepancies
        TS1.compensate = TS1.cal_mean - self.ref_temperature
        TS2.compensate = TS2.cal_mean - self.ref_temperature
        TS3.compensate = TS3.cal_mean - self.ref_temperature

        self.worker_calib_complete.emit({"status": "Calibration completed."})  
        time.sleep(2)

        first_sample = len(TS1.values)
        for nr_sample in range(0, self.nr_samples):
            while(len(TS1.values) == first_sample+nr_sample):
                pass
            dct = dict()
            dct['sample'] = nr_sample+1
            dct['nr_samples'] = self.nr_samples
            self.update_progress.emit(dct)

        TS1.uncertainty_values = np.array(TS1.values[first_sample:first_sample+self.nr_samples+1])
        TS2.uncertainty_values = np.array(TS2.values[first_sample:first_sample+self.nr_samples+1])
        TS3.uncertainty_values = np.array(TS3.values[first_sample:first_sample+self.nr_samples+1] ) 

        TS1.uncertainty = 2*round_to_n(np.sqrt(np.sum((TS1.uncertainty_values-self.ref_temperature)**2)/(self.nr_samples*(self.nr_samples-1))))
        TS2.uncertainty = 2*round_to_n(np.sqrt(np.sum((TS2.uncertainty_values-self.ref_temperature)**2)/(self.nr_samples*(self.nr_samples-1))))
        TS3.uncertainty = 2*round_to_n(np.sqrt(np.sum((TS3.uncertainty_values-self.ref_temperature)**2)/(self.nr_samples*(self.nr_samples-1))))

        if(self.log_condition):
            if self.logger.logged_data == 0:
               self.logger.connect()

            for i in range(3):
                sensor_name = 'TS'+str(i+1)
                data = {'TS': sensor_name,
                'mean': getattr(eval(sensor_name), 'cal_mean'), 
                'std': getattr(eval(sensor_name), 'cal_std'),
                'compensate': getattr(eval(sensor_name), 'compensate'),
                'uncertainty': getattr(eval(sensor_name), 'uncertainty'),
                'values': getattr(eval(sensor_name), 'values')}

                self.logger.log_data(data)
            
        self.logger.disconnect()

        TS1.cal_values = TS1.values[first_sample:first_sample+self.nr_samples]
        TS2.cal_values = TS2.values[first_sample:first_sample+self.nr_samples]
        TS3.cal_values = TS3.values[first_sample:first_sample+self.nr_samples]
        TS1.cal_ts = TS1.ts[0:self.nr_samples]
        TS2.cal_ts = TS2.ts[0:self.nr_samples]
        TS3.cal_ts = TS3.ts[0:self.nr_samples]

        TS1.cal_mean = np.array(TS1.cal_values).mean()
        TS1.cal_std = np.array(TS1.cal_values).std()
        TS2.cal_mean = np.array(TS2.cal_values).mean()
        TS2.cal_std = np.array(TS2.cal_values).std()
        TS3.cal_mean = np.array(TS3.cal_values).mean()
        TS3.cal_std = np.array(TS3.cal_values).std()
        self.worker_complete.emit({"status": "Calibration completed."})  

        

##################################################
# DATA ACQUISITION THREAD
##################################################
class DataAcquisitionThread(QtCore.QThread):

    update_progress = QtCore.pyqtSignal(int)
    update_data = QtCore.pyqtSignal(dict)

    worker_complete = QtCore.pyqtSignal(dict)


    def __init__(self, parent=None, IP=None, PORT=4840, sample_time=0.01, log_condition=0):
        super(DataAcquisitionThread, self).__init__(parent)

        
        self.sample_time = sample_time
        self.acq_module = DataAcqusitionModule(IP, PORT)
        self.logger = DataLoggerModule()

        self.run_condition = 1
        self.log_condition = log_condition

    def run(self):

        #comment out when simulating
        self.acq_module.connect()
        self.rt = RepeatedTimer(self.sample_time, self.acquire_data) # it auto-starts, no need of rt.start()


    def acquire_data(self):
        if self.run_condition:
            data = self.acq_module.get_data()
            #data = {"nr_acq_data": 21, "TS1": 1, "TS2": 2, "TS3":3}

            self.update_data.emit(data)

            if(self.log_condition):
                if self.logger.logged_data == 0:
                   self.logger.connect()
                self.logger.log_data(data)
        else:
            self.logger.disconnect()
            #self.acq_module.disconnect()
            self.rt.stop() # better in a try/finally block to make sure the program ends!

        
    def stop(self):
        self.run_condition = 0
        self.worker_complete.emit({"status": "Data Acquisition stopped."})  

##################################################
# DATA LOGGING THREAD
##################################################
class DataLoggingThread(QtCore.QThread):

    update_progress = QtCore.pyqtSignal(int)
    update_data = QtCore.pyqtSignal(dict)
    worker_complete = QtCore.pyqtSignal(dict)


    def __init__(self, parent=None, sample_time=0.01):
        super(DataAcquisitionThread, self).__init__(parent)

        self.sample_time = sample_time
        self.acq_module = DataAcqusitionModule()

        self.run_condition = 1

    def run(self):

        #must be connected at main menu
        #self.acq_module.connect()

        while(self.run_condition):
            
            data = self.acq_module.get_data()
            self.update_data.emit(data)
            time.sleep(self.sample_time)

        self.acq_module.disconnect()
        self.worker_complete.emit({"status": "Data Logging ended."})  


##################################################
# GLOBAL VARIABLES -- not optimal for production...
##################################################
TS1 = TempSensor('TS1', tol=1.5)
#TS1.raw_val = 20.0
TS2 = TempSensor('TS2', tol=1.5)
TS3 = TempSensor('TS3', tol=1.5)



##################################################
# MAIN
##################################################
def main():

    settings.init()
    importConfig("config.json")
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    app.exec_()
    

if __name__ == '__main__':
    main()

