import socket
import threading

HOST = 'localhost'
PORT = 8080

clients = []

def broadcast(data, exclude_socked = None):
    for client in clients:
        if client != exclude_socked:
            try:
                client.sendall(data.encode())
            except:
                pass

def handline_client(connect):
    while True:
        try:
            data = connect.recv(4096).decode()
            if not data:
                break
            broadcast(data, exclude_socked=connect)
        except:
            break
    if connect in clients:
        clients.remove(connect)
    connect.close

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))

    server_socket.listen(5)
    print("Очікуємо клієнта...")

    while True:
        connect, adress = server_socket.accept()
        print("Клієнт доєднався")
        clients.append(connect)
        threading.Thread(target=handline_client, args=(connect,)).start()

if __name__ == '__main__':
    main()


