import socket
import threading
import pickle 
from app.repository.db import db
import struct

WORKER_NODES = 2
ROW_PER_READ = 10


class Manager():

    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def send_data(self, socket, data):
        serialized_data = pickle.dumps(data)
        message_length = struct.pack("!I", len(serialized_data))
        socket.sendall(message_length + serialized_data)
        print("Data sent.")

    def read_data(self, socket):
        print("Read data.")
        raw_length = socket.recv(4)
        if not raw_length:
            return None
        message_length = struct.unpack("!I", raw_length)[0]
        data = b""
        while len(data) < message_length:
            chunk = socket.recv(min(4096, message_length - len(data)))
            if not chunk:
                raise ConnectionError("Connection closed before receiving full message")
            data += chunk
        print("Data is ")
        print(pickle.loads(data))
        return pickle.loads(data)
    


    def manager_task(self):
        """Central database manager process."""

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(WORKER_NODES + 10)
        print(f"Database Manager listening on {self.host}:{self.port}...")

        def handle_client(client_socket):
            while True:
                try:
                    # Receive query from the client
                    query = self.read_data(client_socket)
                    if not query:
                        break

                    operation, params = query
                    if operation == "read":
                        print("Query is read.")
                        rows = db.get_unprocessed_pdf(ROW_PER_READ)
                        print("Rows collected, sending rows.")
                        self.send_data(client_socket, rows)
                    elif operation == "write":
                        id_serialized, metadata_serialized, md_serialized, links_serialized, images_serialized = params
                        db.add_pdf_md(pickle.loads(id_serialized), pickle.loads(metadata_serialized),\
                                                pickle.loads(md_serialized), pickle.loads(links_serialized), pickle.loads(images_serialized))
                        self.send_data(client_socket, "Success")
                except Exception as e:
                    client_socket.send(pickle.dumps(f"Error: {e}"))
            client_socket.close()

        while True:
            client_socket, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    manager = Manager("127.0.0.1", 5000)
    manager.manager_task()