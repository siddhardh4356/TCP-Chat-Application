import socket
import threading
import time
import csv

class ChatClient:
    def _init_(self):
        self.server_ip = '192.168.129.129'  # Server IP address
        self.server_port = 5555
        self.primary_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secondary_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response_times = []  # To store response times for performance metrics
        self.start_time = None  # To track the start time for calculating latency
        self.csv_file = 'response_times.csv'  # CSV file to store response times

    def receive_messages(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Disconnected from the primary server.")
                    break
                
                # Measure response time
                if self.start_time is not None:
                    response_time = time.time() - self.start_time
                    self.response_times.append(response_time)
                    print(f"Response Time: {response_time:.2f} seconds")

                print(message)
                
                if "You have been kicked" in message or "You have left the chat." in message:
                    break
                
            except Exception as e:
                print(f"Error receiving messages: {e}")
                break

    def receive_secondary_messages(self, secondary_socket):
        while True:
            try:
                message = secondary_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Disconnected from the secondary server.")
                    break
                
                print(message)
                
            except Exception as e:
                print(f"Error receiving messages from secondary socket: {e}")
                break

    def send_messages(self, client_socket):
        while True:
            message = input()
            
            if message.lower() == "/exit":
                try:
                    client_socket.send("/exit".encode('utf-8'))
                    
                    if self.secondary_client_socket:  # Check if secondary socket exists before sending exit command.
                        self.secondary_client_socket.send("/exit".encode('utf-8'))  
                        
                    print("You have left the chat.")
                    
                except Exception as e:
                    print(f"Error sending exit command: {e}")
                    
                finally:
                    break
                    
            else:
                try:
                    # Set start time before sending a message
                    self.start_time = time.time()
                    
                    client_socket.send(message.encode('utf-8'))
                    
                except Exception as e:
                    print(f"Unable to send message. You might have been disconnected: {e}")
                    break

    def save_to_csv(self):
        # Save the response times to a CSV file
        try:
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Request', 'Response Time (s)'])
                for i, response_time in enumerate(self.response_times):
                    writer.writerow([i + 1, response_time])
            print(f"Response times saved to {self.csv_file}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

    def calculate_performance_metrics(self):
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)

            print("\nPerformance Metrics:")
            print(f"Average Response Time: {avg_response_time:.2f} seconds")
            print(f"Minimum Response Time: {min_response_time:.2f} seconds")
            print(f"Maximum Response Time: {max_response_time:.2f} seconds")

            # Save response times to CSV after calculating metrics
            self.save_to_csv()
        else:
            print("No response times recorded.")

    def run(self):
        try:
            self.primary_client_socket.connect((self.server_ip, self.server_port))
            self.secondary_client_socket.connect((self.server_ip, self.server_port))  # Connect second socket
            
        except ConnectionRefusedError as e:
            print("Unable to connect to the server.")
            return

        nickname = input("Enter your nickname: ")
        self.primary_client_socket.send(nickname.encode('utf-8'))

        receive_thread_primary = threading.Thread(target=self.receive_messages, args=(self.primary_client_socket,))
        receive_thread_primary.start()

        receive_thread_secondary = threading.Thread(target=self.receive_secondary_messages, args=(self.secondary_client_socket,))
        receive_thread_secondary.start()

        send_thread_primary = threading.Thread(target=self.send_messages, args=(self.primary_client_socket,))
        send_thread_primary.start()

        send_thread_primary.join()  # Wait for sending thread to finish
        
        # Calculate and display performance metrics before closing sockets
        self.calculate_performance_metrics()

        self.primary_client_socket.close()
        
        if self.secondary_client_socket:  
            self.secondary_client_socket.close()  # Close secondary connection after exiting

if __name__ == "_main_":
    client = ChatClient()
    client.run()