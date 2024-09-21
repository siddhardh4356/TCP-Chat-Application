Here’s a description you can use for the README file in your GitHub repository for the **TCP Client-Server Chat Application**:

---

# TCP Client-Server Chat Application

This project is a simple TCP-based chat application that allows multiple clients to communicate with each other through a central server. It supports basic messaging features, private messaging, and server-side control by an administrator. The client also tracks performance metrics like response times and saves them for analysis.

## Features

### Server
- Handles multiple client connections using threading.
- Supports chat history storage and broadcasts messages to all connected clients.
- Allows an admin user to:
  - Kick users from the server.
  - View the list of online users.
- Stores chat history and displays it to new users joining the chat.
- Supports private messages between clients.
- Handles multiple connections for primary and secondary sockets.

### Client
- Connects to the server using two TCP sockets (primary and secondary).
- Sends and receives chat messages in real-time.
- Tracks response times for sent messages and logs performance data into a CSV file.
- Calculates performance metrics (average, minimum, and maximum response times).
- Supports private messaging to other users.
- Allows users to exit the chat gracefully.

## Performance Metrics
The client measures the performance of message exchanges by calculating the response time for each sent message. The response times are recorded and saved into a CSV file for further analysis. The following metrics are calculated:
- **Average Response Time**
- **Minimum Response Time**
- **Maximum Response Time**

## Setup

### Requirements
- Python 3.x
- Socket library (standard in Python)
- CSV module (standard in Python)
- Threading module (standard in Python)

### Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/username/repository.git
   cd repository
   ```

2. **Server Setup:**
   - Run the server code:
     ```bash
     python server.py
     ```
   - The server will start listening for client connections on the specified IP and port.

3. **Client Setup:**
   - Run the client code:
     ```bash
     python client.py
     ```
   - Enter a nickname when prompted.
   - Start chatting with other connected clients.

4. **Admin Controls (Server-Side):**
   - As an admin, you can enter commands directly into the server console:
     - **Kick a user**: `/kick <nickname>`
     - **View online users**: `/users`
     - **View chat history**: `/history`

## Usage

- The client can send messages to the chat room or send private messages using `/msg <nickname> <message>`.
- Admin users can control the server via commands in the console (e.g., kicking users).

## Performance Testing
The client measures response times and saves the data to a CSV file. After each session, it calculates performance metrics and stores the results.

## Future Improvements
- Adding support for a graphical user interface (GUI).
- Implementing file sharing between clients.
- Adding encryption for secure messaging.
