
import datetime
import glob
import re
import csv

class DataLoggerModule():

    def __init__(self, mode='', format='.csv'):

        """        
        today = datetime.datetime.now().strftime('%Y%m%d')
        logs_today = glob.glob('log/*')

        files_today = 0
        for name in logs_today:
            if re.search(today, name):
                files_today += 1

        self.FILENAME = today + '_' + str(files_today+1)
        """
        self.format = format
        self.filename = "log/" + datetime.datetime.now().strftime('%Y%m%d_%H-%M') + mode + self.format
        self.file = None
        self.logged_data = 0



    def connect(self):
        try:
            self.file = open(self.filename, 'w', newline='')
            self.writer = csv.writer(self.file)
            self.logged_data = 0
            return 1
        except:
            self.file.close()
            print("Cannot connect to DataLogger.")
            return 0


    def disconnect(self):
        try:
            self.file.close()
            return 1
        except:
            print("Cannot disconnect from DataLogger.")
            return 0

    def log_data(self, data):
        try:
            if self.logged_data == 0:        
                self.writer.writerow(data.keys())

            self.writer.writerow(data.values())
            self.logged_data += 1
            return 1
        except:
            print("Cannot log data.")
            return 0
        
        
