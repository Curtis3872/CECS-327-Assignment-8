#Keep import so that it replaces the TCP from the lecture
import socket

#Import the MongoDB client
from pymongo import MongoClient

#Use for 3 hours ago
from datetime import datetime, timedelta
three_hours_ago = datetime.utcnow() - timedelta(hours=3)
cycles = datetime - timedelta(hours=2)

#MongoDB URL
client = MongoClient("mongodb+srv://peksonmichael:EgGiNZRLzTN581tP@cluster0.y9w6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

#Get the database directly and put into dataset_1
dataset_1 = client["test"]
mycol= dataset_1["Dataset_1_virtual"]

# Query the collection in the last three hours
query = {"time": {"$gte": three_hours_ago}}

#Find the way to change to use sockets in a certain way, have prints for IP and port number and remembr the inputs for it too.
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = input("Enter the IP address to bind ('0.0.0.0' to listen to all): ")
port = int(input("Enter the port number to bind: "))
serv.bind((ip, port))
serv.listen(5)
print(f"Server listening on {ip}:{port}...")

#Make sure its valid
while True:
    conn, addr = serv.accept()
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(4096)
        if not data:
            print(f"Client {addr} disconnected.")
            break
        
        #recieved data
        from_client = data.decode('utf8')
        
        #Q1: What is the average moisture inside my kitchen fridge in the past three hours?
        #Calculate the Volumetric Moisture Content
        if from_client == "1":
            #Prior to step 1: Initialize
            count = 0
            total = 0
            average = 0

            #Step 1: Get Moisture Average(Volumetric Moisture Content) from MongoDB
            for payl in mycol.find(query): #'query' is for the parameter of 3 hours ago
                if 'payload' in payl:
                    payload = payl['payload']
                    if 'Moister_Meter_SF1' in payload:
                        count += 1
                        total += float(payload['Moister_Meter_SF1'])
                else:
                    print("'payload' not found")
            
            #Step 2: Convert response to output and send it back to client
            response = (str(round((total/count), 2)))
            conn.send(response.encode())

        #Q2: "What is the average water consumption per cycle in my smart dishwasher?"
        elif from_client == "2":
            # 'smart' dishwashers use a max of about 5 gallons/20 liters per cycle with a max of 2 hours
            # For every 1.5hrs/90mins is a cycle, we can do it hrly
            # Water flow sensors have a range of about 1-30L/min
            
            count = 0
            total = 0
            average = 0
            #Get the water flow values(mililiters)
            for payl in mycol.ind(cycles):
                if 'payload' in payl:
                        payload = payl['payload']
                        if 'WFS_DW' in payload:
                            count += 1
                            total += float(payload['WFS_DW'])
                else:
                    print("'payload' not found")
                    
            #Convert to mililiters -> liters (total) and get the cycle average within one 'normal' cycle
            total = (total*0.001)//count
            
            response = (str(total))
            conn.send(response.encode())

        #Q3: Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?
        elif from_client == "3":

            sf1_ammeter_total = 0
            sf2_ammeter_total = 0
            sdw_ammeter_total = 0

            #Get Ammeter values in milliAMPs
            for payl in mycol.find():    
                if 'payload' in payl:
                    payload = payl['payload']
                    if 'Ammeter_SF1' in payload:
                        sf1_ammeter_total += (int(float(payload['Ammeter_SF1'])))
                    elif 'Ammeter_SF2' in payload:
                        sf2_ammeter_total += (int(float(payload['Ammeter_SF2'])))
                    elif 'Ammeter_DW' in payload:
                        sdw_ammeter_total += (int(float(payload['Ammeter_DW'])))
                    else:
                        response = ("There is no Ammeter sensor here...")
                
                #Calculate which gives maximum and produce response
                if max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sdw_ammeter_total:
                    response = "1"
                elif max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sf1_ammeter_total:
                    response = "2"
                elif max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sf2_ammeter_total:
                    response = "3"
                else:
                    response = "5"

                #Send the response for Query2
                conn.send(response.encode())

        else:
            print("Not valid")
    conn.close()

    #To do list:
    #1, fix dataniz sensor configs
    #2, complete step 2
    #3, polish
    #4, work on step 3

#Notes
#1. AMPs, average amps in a fridge and dishwasher is about 10 AMPs (9-11)