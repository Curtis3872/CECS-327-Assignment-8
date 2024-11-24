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
        from_client = data.decode('utf8')
        print(f"From client: {from_client}")
        # Uppercases? Find how to set initial message for this?
        response = from_client.upper()
        conn.send(response.encode())
    conn.close()
