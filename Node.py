import hashlib
import threading
from http.server import HTTPServer
import json
import sys
from functools import partial

from http.server import BaseHTTPRequestHandler, HTTPServer



# Classes to handle API REST, gRPC, and MOM requests

# REST API
class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, node, *args, **kwargs):
        self.node = node
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path == '/connect':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            ip = data.get('ip')
            port = data.get('port')
            connectionType = data.get('connectionType')
            threading.Thread(target=self.node.connection_thread, args=(ip, port, connectionType)).start()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())

import http.client
import json

class HTTPClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_request(self, path, ip, port, data):
        try:
            connection = http.client.HTTPConnection(ip, port)
            headers = {'Content-type': 'application/json'}
            connection.request('POST', path, body=data, headers=headers)
            response = connection.getresponse()
            print(f"Response status: {response.status}, reason: {response.reason}")
            response_data = response.read()
            print("Response data:", response_data.decode())
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()

# gRPC

# MOM

# Node class to handle all the functionalities of a node in the Chord network
IP = "127.0.0.1"
PORT = 2000

m = 2
MAX_NODES = 2 ** m

def getHash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES

class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        self.id = getHash(ip + str(port))
        self.files = []
        self.predecessor = None
        self.predecessorAddress = (None, None)
        self.successor = None
        self.successorAddress = (None, None)
        self.finger_table = []
        self.http_client = HTTPClient(ip, port)

    def get_id(self):
        return self.id

    def listen(self):
        print(f"Server is listening on {self.ip}:{self.port}")
        server = HTTPServer((self.ip, self.port), lambda *args, **kwargs: RequestHandler(self, *args, **kwargs))
        server.serve_forever()

    def connection_thread(self, ip, port, connectionType):
        # 5 Types of connections
        # type 0: peer connect
        # type 1: client
        # type 2: ping
        # type 3: lookupID
        # type 4: updateSucc/Pred

        if connectionType == 0:
            print("Connection with:", ip, ":", port)
            print("Join network request received")
            self.join_node((ip, port))

        elif connectionType == 1:
            print("Connection with:", ip, ":", port)
            print("Upload/Download request received")

        elif connectionType == 2:
            # Handle ping
            pass

        elif connectionType == 3:
            # Handle lookup request
            pass

        elif connectionType == 4:
            # Handle predecessor/successor update
            pass

        elif connectionType == 5:
            # Handle update finger table request
            pass

    def asAClientThread(self):
        self.show_menu()
        choice = int(input("Enter your choice: "))
        if choice == 1:
            ip = input("Enter IP to connect: ")
            port = input("Enter port: ")
            self.send_join_request(ip, int(port))
        elif choice == 2:
            self.leave_network()
        elif choice == 3:
            self.upload_file()
        elif choice == 4:
            self.download_file()
        elif choice == 5:
            self.print_finger_table()
        elif choice == 6:
            self.print_predecessor_successor()
        else:
            print("Invalid choice")


    def send_join_request(self, ip, port):
        data = {
            "ip": self.ip,
            "port": self.port,
            "connectionType": 0
        }
        data = json.dumps(data)
        self.http_client.send_request('/connect', ip, port, data)

    def join_node(self, existing_node):
        pass

    def update_predecessor(self):
        pass

    def update_successor(self):
        pass

    def print_predecessor_successor(self):
        pass

    def update_finger_table(self):
        pass

    def update_others_finger_table(self):
        pass

    def print_finger_table(self):
        pass



    def lookup(self, key):
        pass

    def upload_file(self):
        pass

    def download_file(self):
        pass

    def ping(self):
        pass

    def leave_network(self):
        pass

    def show_menu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
        print("5. Print Finger Table\n6. Print my predecessor and successor")

    def start (self):
        threading.Thread(target=self.listen).start()
        while True:
            self.asAClientThread()



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Arguments not supplied (Defaults used)")
    else:
        IP = sys.argv[1]
        PORT = int(sys.argv[2])

    node = Node(IP, PORT)
    print("Node ID:", node.get_id())
    node.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server is shutting down.")

