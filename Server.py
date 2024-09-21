import socket
import threading

class ChatServer:
    def _init_(self):
        self.clients = {}  # Dictionary to store client sockets and their corresponding nicknames
        self.chat_history = []  # Store chat history
        self.server_ip = '192.168.129.129'  # Server IP
        self.server_port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.server_ip}:{self.server_port}")

    def broadcast(self, message, exclude_client=None):
        self.chat_history.append(message)
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]  # Limit chat history to the last 10 messages
        for client in list(self.clients.keys()):  # Use list() to avoid runtime modification errors
            if client != exclude_client:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    client.close()
                    del self.clients[client]

    def kick_user(self, nickname):
        for client, username in list(self.clients.items()):  # Use list() to avoid runtime modification errors
            if username == nickname:
                try:
                    client.send("You have been kicked from the server. Goodbye!".encode('utf-8'))
                    client.close()
                    del self.clients[client]
                    self.broadcast(f"User {nickname} has been kicked from the server.")
                except:
                    client.close()
                    del self.clients[client]
                return
        print(f"User {nickname} not found.")

    def private_message(self, sender_socket, recipient_name, message):
        recipient_found = False
        for client, username in self.clients.items():
            if username == recipient_name:
                recipient_found = True
                try:
                    client.send(f"Private from {self.clients[sender_socket]}: {message}".encode('utf-8'))
                    sender_socket.send(f"Private to {recipient_name}: {message}".encode('utf-8'))
                except:
                    sender_socket.send("Failed to send the private message.".encode('utf-8'))
                break
        if not recipient_found:
            sender_socket.send("User not found.".encode('utf-8'))

    def handle_client(self, client_socket, secondary_socket):
        try:
            client_socket.send("Enter your nickname: ".encode('utf-8'))
            nickname = client_socket.recv(1024).decode('utf-8').strip()
            self.clients[client_socket] = nickname

            # Announce user joining the chat
            self.broadcast(f"JOIN: {nickname} has joined the chat.", exclude_client=client_socket)

            # Send chat history to the new user
            client_socket.send("Chat History:\n".encode('utf-8'))
            for message in self.chat_history:
                client_socket.send(f"{message}\n".encode('utf-8'))

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                if message.lower() == "/exit":  # Handle exit command
                    break
                
                if message.startswith("/msg "):  # Private message
                    parts = message.split(' ', 2)
                    if len(parts) == 3:
                        recipient, msg = parts[1], parts[2]
                        self.private_message(client_socket, recipient, msg)
                elif message.startswith("/kick "):  # Admin command to kick user
                    if self.clients[client_socket] == 'admin':  # Only admin can kick
                        parts = message.split(' ', 1)
                        if len(parts) == 2:
                            nickname = parts[1]
                            self.kick_user(nickname)
                elif message.startswith("/nick "):  # Change nickname command
                    new_nickname = message.split(" ")[1]
                    old_nickname = self.clients[client_socket]
                    self.clients[client_socket] = new_nickname
                    self.broadcast(f"{old_nickname} has changed their nickname to {new_nickname}.")
                elif message == "/users":  # Show online users
                    online_users = ', '.join(self.clients.values())
                    client_socket.send(f"Online users: {online_users}".encode('utf-8'))
                elif message == "/history":  # Retrieve chat history
                    history_message = "Chat History:\n" + "\n".join(self.chat_history[-10:])
                    client_socket.send(history_message.encode('utf-8'))
                else:
                    # Check if the client is still in the client list before broadcasting
                    if client_socket in self.clients:
                        self.broadcast(f"{nickname}: {message}")
                    else:
                        client_socket.send("You have been removed from the server.".encode('utf-8'))
                        break

        except Exception as e:
            print(f"Error handling client {nickname}: {e}")
        
        finally:
            # Ensure the client is removed and connection is closed
            if client_socket in self.clients:
                nickname = self.clients[client_socket]
                del self.clients[client_socket]
                self.broadcast(f"LEAVE: {nickname} has left the chat.")
            
            secondary_socket.close()
            client_socket.close()

    def admin_controls(self):
        while True:
            command = input("Enter a command (e.g., /kick [nickname]): ")	
            if command.startswith("/kick "):
                nickname = command.split(" ")[1]
                self.kick_user(nickname)

    def run(self):
        admin_thread = threading.Thread(target=self.admin_controls)
        admin_thread.start()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")

            secondary_socket, _ = self.server_socket.accept()  # Accept second connection

            print(f"New secondary connection from {client_address}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, secondary_socket))
            client_thread.start()

if __name__ == "_main_":
    server = ChatServer()
    server.run()