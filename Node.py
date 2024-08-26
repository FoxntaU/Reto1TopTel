import hashlib
import threading
from http.server import HTTPServer
import json
import sys
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict


import grpc # pip install grpcio
import service_pb2_grpc # pip install protobuf
import service_pb2 # pip install protobuf



from http.server import BaseHTTPRequestHandler, HTTPServer

# Classes to handle API REST, gRPC, and MOM requests

# REST API

# RequestHandler class to handle all the requests received by the server
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
            dataforprocces = data.get('data', None)
            threading.Thread(target=self.node.connection_thread, args=(ip, port, connectionType, dataforprocces)).start()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())

        elif self.path == '/update_finger_table':

            # Handler for finger table update requests
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            node_id = data['node_id']
            ip = data['ip']
            port = data['port']
            finger_index = data['finger_index']

            # Update the finger table with the new node
            self.node.update_finger_table(Node(ip, port), finger_index)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "finger_table_updated"}).encode())

        else:
            # Unrecognized route
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "not found"}).encode())

import http.client
import json

# HTTPClient class to send requests to other nodes in the network
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

class SearchsuccService(service_pb2_grpc.SearchsuccServicer):
    def __init__(self, node):
        self.node = node

    def LookupID(self, request, context):
        print("LookupID request received")
        keyID = request.idNode
        if self.node.id == keyID:  # Si el ID coincide con el ID del nodo actual
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.succID == self.node.id:  # Si solo hay un nodo
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.id > keyID:  # Si el ID es menor, consultar el predecesor
            if self.node.predID < keyID:
                result = False
                address = f"{self.node.ip}:{self.node.port}"
            elif self.node.predID > self.node.id:
                result = False
                address = f"{self.node.ip}:{self.node.port}"
            else:
                result = True
                address = f"{self.node.pred[0]}:{self.node.pred[1]}"
        else:  # Si el ID es mayor, consultar la tabla de dedos
            if self.node.id > self.node.succID:
                result = False
                address = f"{self.node.succ[0]}:{self.node.succ[1]}"
            else:
                for key, value in self.node.finger_table.items():
                    if key >= keyID:
                        result = True
                        address = f"{value[0]}:{value[1]}"
                        break
                else:
                    result = False
                    address = f"{self.node.succ[0]}:{self.node.succ[1]}"

        return service_pb2.LookupIDResponse(result=result, address=address)

class JoinnodeService(service_pb2_grpc.JoinnodeServicer):
    def __init__(self, node):
        self.node = node

    def JoinNode(self, request, context):
        print("JoinNode request received")
        ip, port = request.address.split(":")
        keyID = getHash(ip + ":" + port)
        Oldpred = self.node.pred
        self.node.pred = (ip, port)
        self.node.predID = keyID
        response = service_pb2.JoinResponse(address=f"{Oldpred[0]}:{Oldpred[1]}")
        #falta actualizar tablas de dedos
        return response

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
        self.filenameList = []
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        self.id = getHash(ip + ":" + str(port))
        self.pred = (self.ip, self.port)
        self.predID = self.id
        self.succ = (self.ip, self.port)
        self.succID = self.id
        self.finger_table = OrderedDict()
        self.http_client = HTTPClient(ip, port)
        self.grpc_server = None

    def get_id(self):
        return self.id

    def listen(self):
        print(f"Server is listening on {self.ip}:{self.port}")
        server = HTTPServer((self.ip, self.port), lambda *args, **kwargs: RequestHandler(self, *args, **kwargs))
        server.serve_forever()

    def connection_thread(self, ip, port, connectionType, dataforprocces):
        # 5 Types of connections
        # type 0: peer connect
        # type 1: client
        # type 2: ping
        # type 3: lookupID
        # type 4: updateSucc
        # type 5: updatePred


        if connectionType == 1:
            print("Connection with:", ip, ":", port)
            print("Upload/Download request received")

        elif connectionType == 2:
            # Handle ping
            pass
        
        # Handle update successor request
        elif connectionType == 4:
            # Handle update successor request
            self.update_successor(ip, port)

        # Handle update predecessor request
        elif connectionType == 5:
            self.update_predecessor(ip, port)

        elif connectionType == 6:
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

    def join_node(self, address):
        ipnewnode, portnewnode = address
        idnewnode = getHash(ipnewnode + str(portnewnode))
        print(f"Joining network at {ipnewnode}:{portnewnode}")

        #findind successor of new node
        if self.succID is None:
            self.succID = idnewnode
            self.succ = (ipnewnode, portnewnode)
            print(f"Successor found: {self.succID} at {self.succ}")
        #if only one node in the network
        else:
            result, address = self.getSuccessor(ipnewnode, portnewnode)
            if result:
                ip_succ, port_succ = address.split(':')
                self.update_successor(ip_succ, int(port_succ))

        #update finger table of new node
        self.update_finger_table()

        #update finger table of other nodes
        self.update_others_finger_table()


    # Send join request to the node like a client to connect to the network # (CLIENT SIDE)
    def send_join_request(self, ip, port): 
        #obtain the id of the node to connect
        address = self.getSuccessor(ip, port)
        print(f"Successor found: {address}")
        #send the join request to the node
            # Enviando la solicitud de unión al nodo existente
        with grpc.insecure_channel(f'{ip}:{port + 1}') as channel:
            stub = service_pb2_grpc.JoinnodeStub(channel)  # Cambia a JoinnodeStub
            request = service_pb2.JoinRequest(address=f"{self.ip}:{self.port}")
            response = stub.JoinNode(request)
        
        print(f"My new predecessor: {response.address}")
        #update the predecessor of the node
        self.update_predecessor(response.address.split(":")[0], int(response.address.split(":")[1]))
        #update the successor of the node
        self.update_successor(address.split(":")[0], int(address.split(":")[1]))
        #update successor of the predecessor
        self.http_client.send_request('/connect', self.pred[0], self.pred[1], json.dumps({"ip": self.ip, "port": self.port, "connectionType": 4}))


    # Get the successor of the node # (CLIENT SIDE)
    def getSuccessor(self, ip, port):
        searchNode = True
        keyID = self.id
        while searchNode:
            with grpc.insecure_channel(f'{ip}:{port + 1}') as channel:
                stub = service_pb2_grpc.SearchsuccStub(channel)
                request = service_pb2.LookupIDRequest(idNode=keyID)
                response = stub.LookupID(request)
                searchNode = response.result
        return response.address

    
    def update_successor(self, ip, port):
        self.succID = getHash(ip + ":" + str(port))
        self.succ = (ip, port)
        
    def update_predecessor(self, ip, port):
        self.predID = getHash(ip + ":" + str(port))
        self.pred = (ip, port)

    def print_predecessor_successor(self):
        print(f"Me           N.ID: {self.id} / {self.ip}:{self.port}")
        print(f"Predecessor  N.ID: {self.predID} / {self.pred[0]}:{self.pred[1]}")
        print(f"Successor    N.ID: {self.predID} / {self.succ[0]}:{self.succ[1]}")

    def update_finger_table(self):

        for i in range(m):
            start = (self.id + 2**i) % MAX_NODES
            result, address = self.find_successor(start)
            if result:
                self.finger_table[start] = address
        print(f"Finger table updated: {self.finger_table}")

    def update_others_finger_table(self):

        for i in range(m):
            pred_result, pred_address = self.find_predecessor((self.id - 2**i + MAX_NODES) % MAX_NODES)
            if pred_result:
                ip, port = pred_address.split(':')
                self.send_update_finger_request(ip, port, self, i)

    def send_update_finger_request(self, ip, port, s, i):
        #Send a request to update the finger table of another node
        data = {
            'node_id': s.id,
            'ip': s.ip,
            'port': s.port,
            'finger_index': i
        }
        self.http_client.send_request('/update_finger_table', ip, port, json.dumps(data))

    def print_finger_table(self):
        print("Finger Table:")
        for i, entry in enumerate(self.finger_table):
            print(f"Index {i}: {entry}")

    def upload_file(self):
        pass

    def download_file(self):
        pass

    def ping(self):
        pass

    def leave_network(self):

        # Notify other nodes to update their finger tables
        self.notify_others_on_leave()

        # Perform any necessary cleanup here
        print(f"Node {self.ip}:{self.port} leaving the network.")

        # Close the gRPC server
        if self.grpc_server:
            self.grpc_server.stop(0)

    def notify_others_on_leave(self):

        for i in range(m):
            pred_result, pred_address = self.find_predecessor((self.id - 2**i + MAX_NODES) % MAX_NODES)
            if pred_result:
                ip, port = pred_address.split(':')
                data = {
                    'node_id': self.succID,
                    'ip': self.succ[0],
                    'port': self.succ[1],
                    'finger_index': i
                }
                self.http_client.send_request('/update_finger_table', ip, int(port), json.dumps(data))

    def show_menu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
        print("5. Print Finger Table\n6. Print my predecessor and successor")

    def start_grpc_server(self):
        self.grpc_server = grpc.server(ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_SearchsuccServicer_to_server(SearchsuccService(self), self.grpc_server)
        service_pb2_grpc.add_JoinnodeServicer_to_server(JoinnodeService(self),  self.grpc_server)
        self.grpc_server.add_insecure_port(f'{self.ip}:{self.port + 1}')
        self.grpc_server.start()
        print(f"gRPC server running on {self.ip}:{self.port + 1}")
        self.grpc_server.wait_for_termination()

    def start (self):
        threading.Thread(target=self.listen).start()
        threading.Thread(target=self.start_grpc_server).start()
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
