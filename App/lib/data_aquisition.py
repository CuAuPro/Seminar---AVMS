from opcua import Client
import json
import datetime
import lib.settings as settings

url = "opc.tcp://192.168.0.115:4840"

class DataAcqusitionModule():

    def __init__(self, IP=None, PORT=4840):

        self.IP = "192.168.0.115"
        self.PORT = PORT
        if IP is not None:
            self.IP = IP

        self.vars_node = settings.config["var"]

        self.vars = dict()


        
        self.url = "opc.tcp://"+self.IP+":"+str(self.PORT)

        self.client = Client(self.url)

        self.acquired_data = 0


    def connect(self):
        try:
            self.acquired_data = 0
            self.client.connect()

            for var_node in self.vars_node.keys():
                self.vars[var_node] = self.client.get_node(self.vars_node[var_node])
            return 1
        except:
            print("Cannot connect to server.")
            return 0


    def disconnect(self):
        try:
            self.client.disconnect()
            return 1
        except:
            print("Cannot disconnect from server.")
            return 0

    def get_data(self):

        ret = dict()
        ts = datetime.datetime.now()
        ret['ts'] = ts.isoformat()
        for var_name in self.vars.keys():
            ret[var_name] = self.vars[var_name].get_value()

        self.acquired_data += 1
        ret['nr_acq_data'] = self.acquired_data

        return ret
