import socket
import threading

# избавимся от магических цифр, сделаем размер буфера, хост и порт константами
# размер буфера теперь можно оперативно изменять 
HOST = '127.0.0.1'
PORT = 55555
BUFFER_SIZE = 1024

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# создадим отдельный объект блокировки потоков для управления
# доступом к общему ресурсу несколькими потоками
lock = threading.Lock()

# Sending Messages To All Connected Clients
# будем использовать lock c менеджером контекста и добавим обработку исключений 
def broadcast(message, sender=None):
    with lock:
        for client in clients:
            if client != sender:
                try:
                    client.send(message)
                except:
                    remove_client(client)

# оптимизируем управление потоками и добавим метод удаления клиентов
# сообщения можно будет отправлять и на кириллице, используем кодировку utf-8
def remove_client(client):
    with lock:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        client.close()
        broadcast(f'{nickname} left the chat!'.encode('utf-8'))

# Handling Messages From Clients
# будем использовать наш метод remove_client для удаления клиента
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(BUFFER_SIZE)
            if not message:
                break
            broadcast(message, client)                
        except:
            remove_client(client)
            break                   
     
# Receiving / Listening Function
# теперь можно будет использовать и кириллицу,
#  используем f-строки для более наглядного форматирования
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f"Connected with {address}")

        # Request And Store Nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(BUFFER_SIZE).decode('utf-8')
        with lock:
            nicknames.append(nickname)
            clients.append(client)
        # Print And Broadcast Nickname
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'), client)
        client.send('Connected to server!'.encode('utf-8'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    # Starting Server
    # запуск сервера лучше будем делать отдельно, чтобы можно было использовать
    # наши методы и в других скриптах
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server if listening...")
    receive()
