import numpy as np
import pandas as pd

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

    for i in faults:
        sensors[i].fault = True
    
    if faults.shape[0] == 0:
        return True
    else:
        return False



class TempSensor():
    def __init__(self, sensor_name, tol=1.0):
        self.name = sensor_name
        self.raw_val = 0.0
        self.compensate = 0.0

        self.values = [0]
        self.ts = [0]
        self.mean = None
        self.std = None

        self.val = 0.0

        self.tol = tol

        self.fault = False


TS1 = TempSensor('TS1')
TS2 = TempSensor('TS2')
TS3 = TempSensor('TS3')

TS1.val = 17.5
TS2.val = 20.2
TS3.val = 20.25


check_sensors(TS1, TS2, TS3)



print(getattr("TS1", 'cal_mean'))
data = {'TS': 'TS'+str(i+1), 'mean': TS1.cal_mean, 'std': TS1.cal_std, 'compensate': TS1.compensate, 'values': TS1.cal_values}
self.logger.log_data(data)
