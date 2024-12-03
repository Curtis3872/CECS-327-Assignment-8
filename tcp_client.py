import socket
import ipaddress

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

while True:
    ip = input("Enter server IP: ")
    port = input("Enter server port: ")

    if not is_valid_ip(ip) or not port.isdigit() or not (0 <= int(port) <= 65535):
        print("Invalid IP or port number. Please try again.")
        continue

    port = int(port)

    # Create the socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Attempt to connect
        client.connect((ip, port))
        print(f"Connected to server {ip}:{port}!")

        while True:
            message = input("Choose a query to find:\n'1': Average moisture inside your kitchen fridge in the past three hours,\n'2': Average water consumption per cycle in your smart dishwasher,\n'3': Which device is consuming more electricity?\nor\n'exit' to close\n:")
            if message.lower() == 'exit':
                print("Closing connection.")
                break
            elif message == "1":
                # Send message to server
                client.send(message.encode())
                
                # Receive server response
                from_server = client.recv(4096)
                print(f"{from_server.decode()}")
                
            elif message == "2":
                # Send message to server
                client.send(message.encode())
                
                # Receive server response
                from_server = client.recv(4096)
                print(f"{from_server.decode()}")

            elif message == "3":
                # Send message to server
                client.send(message.encode())
                
                # Receive server response and output which uses the most
                from_server = client.recv(4096)
                print(f"{from_server.decode()}")

            else:
                print("\nSorry, this query cannot be processed. Please try one of the following: [1, 2, 3].\n")
                
#How to send a message from client to server
# Send message to server
            #client.send(message.encode())

# Receive server response
            #from_server = client.recv(4096)
            #print(f"Server replied: {from_server.decode()}")

    except (socket.error, socket.timeout) as e:
        print(f"Failed to connect: {e}")

    finally:
        client.close()
        print("Connection closed.")
        break
