from opcua import Client
import time

url = "opc.tcp://192.168.0.115:4840"


def main():
    client = Client(url)
    client.connect()
    
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path

        #Temperature = root.get_child(["0:Objects", "2:Parameters", "2:Temperature"])
        #Pressure = root.get_child(["0:Objects", "2:Parameters", "2:Pressure"])
        #Time = root.get_child(["0:Objects", "2:Parameters", "2:Time"])

        #obj = root.get_child(["0:Objects", "2:Parameters"])
        #print(Temperature.get_value(), Pressure.get_value(), Time.get_value())


        # Stacked myvar access
        # print("myvar is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value())
        var_TEMP_1 = client.get_node("ns=4;i=3")
        var_TEMP_2 = client.get_node("ns=4;i=4")
        var_TEMP_3 = client.get_node("ns=4;i=5")
        var_START_CA = client.get_node("ns=4;i=6")
        var_clock_1hz = client.get_node("ns=4;i=7")
        var_clock_byte = client.get_node("ns=4;i=8")
        #root.get_child(["0:Objects", "3:ServerInterfaces"]).get_children()[0].get_children()

    finally:
        client.disconnect()

if __name__ == "__main__":
    main()

"""while True:
    temp = client.get_node("ns=2;i=2")
    press = client.get_node("ns=2;i=3")
    temperature = temp.get_value()
    pressure = press.get_value()
    print(temperature, pressure)
    time.sleep(2)"""