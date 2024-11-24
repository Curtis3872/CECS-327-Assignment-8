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
            message = input("Enter your message (or 'exit' to close):\n")
            if message.lower() == 'exit':
                print("Closing connection.")
                break

            # Send message to server
            client.send(message.encode())

            # Receive server response
            from_server = client.recv(4096)
            print(f"Server replied: {from_server.decode()}")

    except (socket.error, socket.timeout) as e:
        print(f"Failed to connect: {e}")

    finally:
        client.close()
        print("Connection closed.")
        break
