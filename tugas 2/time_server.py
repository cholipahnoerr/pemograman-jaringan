import socket
import threading
import logging
from datetime import datetime

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.running = True

    def run(self):
        try:
            while self.running:
                data = self.connection.recv(1024)
                if not data:
                    break
                
                # Decode data ke string
                message = data.decode('utf-8').strip()
                logging.info(f"Received from {self.address}: {repr(message)}")

                if message == "TIME":
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    response = f"JAM {current_time}\r\n"
                    self.connection.sendall(response.encode('utf-8'))

                elif message == "QUIT":
                    self.running = False
                    logging.info(f"Client {self.address} requested to quit.")
                    break

                else:
                    self.connection.sendall(b"Invalid request\r\n")

        except Exception as e:
            logging.error(f"Error with client {self.address}: {e}")
        finally:
            self.connection.close()
            logging.info(f"Connection closed with {self.address}")

class Server(threading.Thread):
    def __init__(self, port=45000):
        threading.Thread.__init__(self)
        self.server_address = ('0.0.0.0', port)
        self.clients = []

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.server_address)
            s.listen(5)
            logging.info(f"Server running on port {self.server_address[1]}")

            while True:
                connection, address = s.accept()
                logging.info(f"Connection from {address}")
                client_thread = ProcessTheClient(connection, address)
                client_thread.start()
                self.clients.append(client_thread)

def main():
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
