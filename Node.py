import hashlib
import threading
from http.server import HTTPServer
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading


# Classes to handle API REST, gRPC, and MOM requests
class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, node, *args, **kwargs):
        self.node = node
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path == '/connect':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            address = data.get('address')
            connectionType = data.get('connectionType')
            threading.Thread(target=self.node.connection_thread, args=(None, address, connectionType)).start()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())



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
        self.predecessors = None
        self.successors = None
        self.finger_table = []

    def get_id(self):
        return self.id

    def listen(self):
        server = HTTPServer((self.ip, self.port), lambda *args, **kwargs: RequestHandler(self, *args, **kwargs))
        print(f"Server is listening on {self.ip}:{self.port}")
        server.serve_forever()

    def connection_thread(self, connection, address, connectionType):
        # 5 Types of connections
        # type 0: peer connect
        # type 1: client
        # type 2: ping
        # type 3: lookupID
        # type 4: updateSucc/Pred

        if connectionType == 0:
            print("Connection with:", address[0], ":", address[1])
            print("Join network request received")

        elif connectionType == 1:
            print("Connection with:", address[0], ":", address[1])
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


    def join_new_node(self, existing_node):
        pass

    def join_node(self, existing_node):
        pass

    def update_predecessor(self):
        pass

    def update_successor(self):
        pass

    def update_finger_table(self):
        pass

    def update_others_finger_table(self):
        pass

    def lookup(self, key):
        pass

    def process_message(self, message):
        pass

    def send_message(self, message, target_node):
        pass

    def receive_message(self):
        pass

    def ping(self):
        pass

    def show_menu(self):
        pass

    def start (self):
        threading.Thread(target=self.listen).start()

if __name__ == "__main__":
    node0 = Node(IP, PORT)
    node0.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server is shutting down.")

