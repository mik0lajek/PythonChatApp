import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Rozłączono z serwerem.")
                break
            print(message)
        except:
            print("Rozłączono z serwerem.")
            break

def main():
    server_address = ('localhost', 5678)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    username = input("Podaj nazwę użytkownika: ")
    client_socket.send(username.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        message = input()
        if message.lower() == "/disconnect":
            client_socket.send("/disconnect".encode('utf-8'))
            break
        client_socket.send(message.encode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    main()
