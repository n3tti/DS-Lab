import socket
import pickle
import struct 

import requests
from app.repository.models import PDFLink, PDFMetadata, LinkStatusEnum
from store_files.save_file import save_downloaded_file
import pymupdf4llm
import pymupdf
import argparse


class Worker():

    def __init__(self, manager_host, manager_port):
        self.manager_host = manager_host
        self.manager_port = manager_port


    def send_data(self, socket, data):
        print("Send data: ")
        print(data)
        serialized_data = pickle.dumps(data)
        message_length = struct.pack("!I", len(serialized_data))
        socket.sendall(message_length + serialized_data)

    def read_data(self, socket):
        print("Reading data.")
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


    def get_rows(self, socket):
        read_query = ("read", "")
        self.send_data(socket, read_query)
        return self.read_data(socket)


    def update_row(self, socket, id, metadata, md, links, images, dl):            
        id_serialized = pickle.dumps(id)
        metadata_serialized = pickle.dumps(metadata)
        md_serialized = pickle.dumps(md)
        links_serialized = pickle.dumps(links)
        images_serialized = pickle.dumps(images)

        params = (id_serialized, metadata_serialized, md_serialized, links_serialized, images_serialized)
        write_query = ("write", params)
        self.send_data(socket, write_query)
        return self.read_data(socket)

    def process(self, row):
        
        dl = False
        doc = None
        r = requests.get(row.url)
        if r.status_code == 200:
            if row.status != LinkStatusEnum.DOWNLOADED:
                dl = save_downloaded_file(row.id, row.url, "pdf", r.content)
            data = r.content
            doc = pymupdf.Document(stream=data)
            if doc.is_encrypted and doc.needs_pass:
                return None, None, None, None, None, dl
            metadata = doc.metadata
            metadata_obj = PDFMetadata(title = metadata["title"], author =  metadata["author"], \
                        subject = metadata["subject"], keywords = metadata["keywords"],\
                        creationDate = metadata["creationDate"], modDate = metadata["modDate"])

            md_text = pymupdf4llm.to_markdown(doc)
            return row.id, metadata_obj, md_text, None, None, dl
        else:
            return row.id, None, None, None, None, dl
    


    def worker_task(self):
        # Connect to DB manager
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.manager_host, self.manager_port))
        print("Worker connected.")
        # Worker loop
        try :
            while True:
                # Get unprocessed rows
                print("Get row:")
                rows = self.get_rows(client_socket)
                if rows != None:
                    for row in rows:
                        print("Start processing.")
                        id, metadata, md, links, images, dl = self.process(row) # Process PDF
                        print("End processing.")
                        print("Update row.")
                        update = self.update_row(client_socket, id, metadata, md, links, images) # Write to DB
                        if update != "Success":
                            raise Exception("Update failed on manager side.")
                        print("Succes update row.")
        except Exception as e:
            client_socket.close()
            print(f"Worker failed: {e}")

       


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manager-host", required=True, help="Hostname of the manager node")
    parser.add_argument("--manager-port", type=int, default=5000, help="Port of the manager node")
    args = parser.parse_args()

    # Use the provided manager host and port
    worker = Worker(args.manager_host, args.manager_port)
    worker.worker_task()
