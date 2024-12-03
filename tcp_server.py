#Keep import so that it replaces the TCP from the lecture
import socket

#Import the MongoDB client
from pymongo import MongoClient

#Use for 1-3 hours ago
from datetime import datetime, timedelta 
three_hours_ago = datetime.utcnow() - timedelta(hours=3) 
two_hours_ago = datetime.utcnow() - timedelta(hours=2)   
one_hour_ago = datetime.utcnow() - timedelta(hours=1)    

#MongoDB URL
client = MongoClient("mongodb+srv://peksonmichael:EgGiNZRLzTN581tP@cluster0.y9w6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

#Get the database directly and put into dataset_1
data = client["test"]
mycol= data["Dataset_1_virtual"]

# Query the collection in the last three hours
query = {"time": {"$gte": three_hours_ago}}                        #3 hours ago
query2 = {"time": {"$gte": one_hour_ago}}                          #1 hour ago
query3 = {"time": {"$gte": two_hours_ago, "$lt": one_hour_ago}}    #one hour from now and two hours ago
query4 = {"time": {"$gte": three_hours_ago, "$lt": two_hours_ago}} #3 hours ago and 2 hours later

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
            count1 = 0
            count2 = 0
            total = 0
            curr_moisture = 0
            total_RH = 0

            #Step 1: Get Moisture Average(Volumetric Moisture Content) from MongoDB - > convert to percentage as if 0.xxxx
            for payl in mycol.find(query): #'query' is for the parameter of 3 hours ago
                if 'payload' in payl:
                    payload = payl['payload']
                    if 'mm_sf1' in payload:
                        count1 += 1
                        curr_moisture = float(payload['mm_sf1'])*0.01
                        print(curr_moisture)
                        total += curr_moisture
                        
            #Step 2: To find the Relative Humidity, we need: 
                    if 'temp_sf1' in payload:
                        F = float(payload['temp_sf1'])#1. temperature
                        #convert F to C
                        T = (F-32) * (5/9)
                        count2 +=1
                        
                        #2. Saturated Vapour Pressure using Tentens formula'
                        SVP = 0.61121 ** ((18.678 - (T/234.5)) * (T / (257.14+T)))
                        #3. Actual Vapor Pressure is the Volumetric Water Content (g/m^3)
                        #4. Relative humidity with correct decimal points for incoming calculations and averages
                        RH = round((((curr_moisture)/SVP)*100), 2) #Formula originally (VWC/SVP)*100
                        total_RH += RH
                        
                else:
                    print("'payload' not found")
            
            #Step 2: Convert response to output and send it back to client
            #Notes (1. VWC is given correct decimal and average is calcualted) (2. Relative Humidity is rounded after average is  calcualed for better desired outputs.) 
            response = "\nAverage moisture since 3 hours ago: "
            response += (str(round(((total)/count1)*100, 2))) + "% VMC & " 
            response+= str(round(total_RH/count2, 2)) + "% Relative Humidity\n"
            
            conn.send(response.encode())

        #Q2: "What is the average water consumption per cycle in my smart dishwasher?"
        elif from_client == "2":
            # 'smart' dishwashers use a max of about 5 gallons/20 liters per cycle with a max of 2 hours
            # Every hr is one cycle
            
            #3 seperate cycles going through about 1 hour intervals within 3 intervals to find average for 3 cycles spanning 3 hours
            count1 = 0
            count2 = 0
            count3 = 0
            total1 = 0
            total2 = 0
            total3 = 0
            average1 = 0
            average2 = 0
            average3 = 0
            total_average_cycle = 0
            
            #Get the water flow values(convert from mL -> L)
            #Each cycle(average1-3), shows the average amount of waterflow in each cycle
            
            #Cycle 1
            for payl in mycol.find(query2):
                if 'payload' in payl:
                        payload = payl['payload']
                        if 'WFS_DW' in payload:
                            count1 += 1
                            total1 += float(payload['WFS_DW'])
                            print("TOTAL1: ", total1)
                else:
                    print("'payload' not found")
            
            #Cycle 2
            for payl in mycol.find(query3):
                if 'payload' in payl:
                        payload = payl['payload']
                        if 'WFS_DW' in payload:
                            count2 += 1
                            total2 += float(payload['WFS_DW'])
                else:
                    print("'payload' not found")
            
            #Cycle 3
            for payl in mycol.find(query4):
                if 'payload' in payl:
                        payload = payl['payload']
                        if 'WFS_DW' in payload:
                            count3 += 1
                            total3 += float(payload['WFS_DW'])
                else:
                    print("'payload' not found")
            
            #Cycles + conversion of HL to L 
            total_average_cycle = ((total1+total2+total3)/3)*0.01
            
            response = "\nDishwasher's average water consumption per cycle: " + str(round(total_average_cycle, 2)) + " L\n"
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
                    elif 'Ammeter_sf2' in payload:
                        sf2_ammeter_total += (int(float(payload['Ammeter_sf2'])))
                    elif 'Ammeter_dw' in payload:
                        sdw_ammeter_total += (int(float(payload['Ammeter_dw'])))
                    else:
                        response = ("There is no Ammeter sensor here...")
                
            #Calculate which gives maximum and produce response
            if max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sdw_ammeter_total:
                response = "\nThe Smart Dish Washer is using the most electricity!\n"
            elif max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sf1_ammeter_total:
                response = "\nSmart Fridge 1 is using the most electricity!\n"
            elif max(sf1_ammeter_total, sf2_ammeter_total, sdw_ammeter_total) == sf2_ammeter_total:
                response = "\nSmart Fridge 2 is using the most electricity!\n"
            else:
                response = "\nAll three devices have an equal amount of AMPs!\n"

            #Send response
            conn.send(response.encode())

        else:
            print("Not valid")
    conn.close()