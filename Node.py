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
import time

from http.server import BaseHTTPRequestHandler, HTTPServer

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
        connection = None  
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
            if connection:
                connection.close()

# gRPC
class SearchsuccService(service_pb2_grpc.SearchsuccServicer):
    def __init__(self, node):
        self.node = node
    def LookupID(self, request, context):
        print("LookupID request received")
        keyID = request.idNode

        print(f"keyID: {keyID}")
        print(f"self.id: {self.node.id}")
        print(f"self.succID: {self.node.succID}")
        print(f"self.predID: {self.node.predID}")
        print(f"self.succ: {self.node.succ}")
        print(f"self.pred: {self.node.pred}")
        print(f"self.finger_table: {self.node.finger_table}")
        
        if self.node.id == keyID:
            print("Caso 0: Si el ID coincide con el ID del nodo actual")
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.succID == self.node.id:
            print("Caso 1: Si solo hay un nodo")
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.id > keyID:
            print("Caso 2: Si el ID es menor, consultar el predecesor")
            if self.node.predID < keyID:
                result = False
                address = f"{self.node.ip}:{self.node.port}"
            if self.node.predID == self.node.id:
                result = False
                address = f"{self.node.id[0]}:{self.node.id[1]}"
            else:
                result = True
                address = f"{self.node.pred[0]}:{self.node.pred[1]}"
        else:
            print("Caso 3: Si el ID es mayor, consultar la tabla de dedos")
            if self.node.id > self.node.succID:
                print("Caso 3.1: Si el ID es mayor que el sucesor")
                result = False
                address = f"{self.node.succ[0]}:{self.node.succ[1]}"
            else:
                print("Caso 3.2: Si el ID es menor que el sucesor")
                value = ()
                for key, value in self.node.finger_table.items():
                    if key >= keyID:
                        break
                value = self.node.succ
                result = True
                address = f"{value[0]}:{value[1]}"


        print(f"Result: {result}, Address: {address}")
    
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

        def post_response_operations():
            time.sleep(0.1)
            self.node.update_finger_table()
            self.node.update_others_finger_table()

        threading.Thread(target=post_response_operations).start()

        # respondo con el predecesor actual
        return response

class TableService(service_pb2_grpc.UpdatetableServicer):
    def __init__(self, node):
        self.node = node

    def UpdateTable(self, request, context):
        print("UpdateTable request received")
        
        # Actualizar la tabla de enrutamiento (Finger Table)
        self.node.update_finger_table()
        
        # Retornar el sucesor como parte de la respuesta
        return service_pb2.UpdateTableResponse(address=str(self.node.succ[0]) + ":" + str(self.node.succ[1]))

# Node class to handle all the functionalities of a node in the Chord network

IP = "127.0.0.1"
PORT = 2000

MAX_BITS = 10
MAX_NODES = 2 ** MAX_BITS

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
        if connectionType == 2:
            # Handle ping
            pass
        elif connectionType == 4:
            self.update_successor(ip, port)
        elif connectionType == 5:
            self.update_predecessor(ip, port)

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

    # Send join request to the node like a client to connect to the network # (CLIENT SIDE)
    def send_join_request(self, ip, port): 
        #obtain the id of the node to connect
        address = self.getSuccessor(ip, port, self.id)
        print(f"Successor found: {address}")
        #send the join request to the node
            # Enviando la solicitud de unión al nodo existente
        with grpc.insecure_channel(f'{ip}:{port + 1}') as channel:
            stub = service_pb2_grpc.JoinnodeStub(channel)
            request = service_pb2.JoinRequest(address=f"{self.ip}:{self.port}")
            response = stub.JoinNode(request)
        
        print(f"My new predecessor: {response.address}")
        # Actualiza el predecesor y sucesor de acuerdo a la respuesta
        pred_ip, pred_port = response.address.split(":")
        self.update_predecessor(pred_ip, int(pred_port))
    
        succ_ip, succ_port = address.split(":")
        self.update_successor(succ_ip, int(succ_port))
    
        # Actualiza el sucesor del predecesor
        print("Updating predecessor's successor")
        self.http_client.send_request('/connect', self.pred[0], self.pred[1], json.dumps({"ip": self.ip, "port": self.port, "connectionType": 4}))

    # Get the successor of the node # (CLIENT SIDE)
    def getSuccessor(self, ip, port, keyID):
        searchNode = True
        while searchNode:
            with grpc.insecure_channel(f'{ip}:{port + 1}') as channel:
                stub = service_pb2_grpc.SearchsuccStub(channel)
                request = service_pb2.LookupIDRequest(idNode=keyID)
                response = stub.LookupID(request)
                searchNode = response.result
                print(f"SearchNode: {searchNode} type; {type(searchNode)}")
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
        print(f"Successor    N.ID: {self.succID} / {self.succ[0]}:{self.succ[1]}")
    
    def update_finger_table(self):
        print("Updating finger table")
        for i in range(MAX_BITS):
            entryId = (self.id + (2 ** i)) % MAX_NODES
            # If only one node in network
            if self.succ == self.address:
                print("Only one node in network")
                self.finger_table[entryId] = (self.id, self.address)
                continue
            # If multiple nodes in network, we find succ for each entryID
            address = self.getSuccessor(self.succ[0],self.succ[1], entryId)
            print(f"Successor for {entryId}: {address}")
            recvId = getHash(address)
            address = address.split(":")
            self.finger_table[entryId] = (recvId, address)

        print(f"Update Finger table: {self.finger_table}")


    def update_others_finger_table(self):
        print("Updating others finger table")
        here = self.succ  
        while True:
            if here == self.address:
                break
            try:
                with grpc.insecure_channel(f'{here[0]}:{here[1] + 1}') as channel:
                    stub = service_pb2_grpc.UpdatetableStub(channel)
                    request = service_pb2.UpdateTableRequest()
                    response = stub.UpdateTable(request)
                    pred_ip, pred_port = response.address.split(":")
                    here = (pred_ip, int(pred_port))
                    if here == self.address:
                        break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def print_finger_table(self):
        print("Finger Table:")
        for i, (start, entry) in enumerate(self.finger_table.items()):
            print(f"Index {i} (start {start}): Node {entry}")

    def show_menu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
        print("5. Print Finger Table\n6. Print my predecessor and successor")

    def start_grpc_server(self):
        self.grpc_server = grpc.server(ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_SearchsuccServicer_to_server(SearchsuccService(self), self.grpc_server)
        service_pb2_grpc.add_JoinnodeServicer_to_server(JoinnodeService(self),  self.grpc_server)
        service_pb2_grpc.add_UpdatetableServicer_to_server(TableService(self), self.grpc_server)
        self.grpc_server.add_insecure_port(f'{self.ip}:{self.port + 1}')
        self.grpc_server.start()
        print(f"gRPC server running on {self.ip}:{self.port + 1}")
        self.grpc_server.wait_for_termination()

    def start(self):
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
