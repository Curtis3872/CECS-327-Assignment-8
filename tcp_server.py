#Keep import so that it replaces the TCP from the lecture
import socket

#Import the MongoDB client
from pymongo import MongoClient

#Use for 3 hours ago
from datetime import datetime, timedelta
three_hours_ago = datetime.utcnow() - timedelta(hours=3)

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
        
        if from_client == "1":
            #Calculate the Volumetric Moisture Content
            count = 0
            total = 0
            average = 0

            for payl in mycol.find(query):
                if 'payload' in payl:
                    payload = payl['payload']
                    if 'Moister_Meter_SF1' in payload:
                        count += 1
                        total += float(payload['Moister_Meter_SF1'])

                else:
                    print("'payload' not found")
                    #str(total/count) is the Volumetric Water Content (VMC)
            response = (str(round((total/count), 2)))
            conn.send(response.encode())

        elif from_client == "2":
            # 'smart' dishwashers use a max of about 5 gallons/20 liters per cycle with a max of 2 hours
            # For every 1.5hrs/90mins is a cycle, we can do it hrly
            # Water flow sensors have a range of about 1-30L/min
            count = 0
            total = 0
            average = 0

            if 'payload' in payl:
                    payload = payl['payload']
                    if 'WFS_DW' in payload:
                        count += 1
                        total += float(payload['WFS_DW'])
            else:
                print("'payload' not found")
            #total/count = average 
            #total has liters/min, convert for 1 cycle per 120 mins
            response = (str(round((total/count), 2)))
            conn.send(response.encode())

        else:
            print("Not valid")
    conn.close()

    #To do list:
    #1, fix dataniz sensor configs
    #2, complete step 2
    #3, polish
    #4, work on step 3
