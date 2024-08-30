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
from http.server import ThreadingHTTPServer
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
        # print(f'LookupID request received: {request.idNode}')
        keyID = request.idNode
        '''
        print(f"keyID: {keyID}")
        print(f"self.id: {self.node.id}")
        print(f"self.succID: {self.node.succID}")
        print(f"self.predID: {self.node.predID}")
        print(f"self.succ: {self.node.succ}")
        print(f"self.pred: {self.node.pred}")
        print(f"self.finger_table: {self.node.finger_table}")
        '''

        if self.node.id == keyID:
            # print("Caso 0: Si el ID coincide con el ID del nodo actual")
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.succID == self.node.id:
            # print("Caso 1: Si solo hay un nodo")
            result = False
            address = f"{self.node.ip}:{self.node.port}"
        elif self.node.id > keyID:
            # print("Caso 2: Si el ID es menor, consultar el predecesor")
            if self.node.predID < keyID:
                result = False
                address = f"{self.node.ip}:{self.node.port}"
            elif self.node.predID > self.node.id:
                result = False
                address = f"{self.node.ip}:{self.node.port}"
            else:
                result = True
                address = f"{self.node.pred[0]}:{self.node.pred[1]}"
        else:
            # print("Caso 3: Si el ID es mayor, consultar la tabla de dedos")
            if self.node.id > self.node.succID:
                # print("Caso 3.1: Si el ID es mayor que el sucesor")
                result = False
                address = f"{self.node.succ[0]}:{self.node.succ[1]}"
            else:
                # print("Caso 3.2: Si el ID es menor que el sucesor")
                value = ()
                for key, value in self.node.finger_table.items():
                    if key >= keyID:
                        break
                value = self.node.succ
                result = True
                address = f"{value[0]}:{value[1]}"

        # print(f"Result: {result}, Address: {address}")

        return service_pb2.LookupIDResponse(result=result, address=address)

class JoinnodeService(service_pb2_grpc.JoinnodeServicer):
    def __init__(self, node):
        self.node = node

    def JoinNode(self, request, context):
        ip, port = request.address.split(":")
        print("Connection with:", ip, ":", port)
        print("JoinNode request received")
        keyID = getHash(ip + ":" + port)
        Oldpred = self.node.pred
        self.node.pred = (ip, port)
        self.node.predID = keyID
        response = service_pb2.JoinResponse(address=f"{Oldpred[0]}:{Oldpred[1]}")

        def post_response_operations():
            time.sleep(2)
            print("Updating F Table in Join Node")
            self.node.update_finger_table()
            print("Updating other F Tables in Join Node")
            self.node.update_others_finger_table()

        threading.Thread(target=post_response_operations).start()

        # respondo con el predecesor actual
        return response

class TableService(service_pb2_grpc.UpdatetableServicer):
    def __init__(self, node):
        self.node = node

    def UpdateTable(self, request, context):
        print("Sending my succ to update finger table")
        self.node.update_finger_table()
        # Retornar el sucesor como parte de la respuesta
        return service_pb2.UpdateTableResponse(address=str(self.node.succ[0]) + ":" + str(self.node.succ[1]))

class MessageService(service_pb2_grpc.UploadMessageServicer):
    def __init__(self, node):
        self.node = node

    def UploadMessage(self, request, context):
        print("Upload message request received")
        message = request.message
        message_name = request.message_name
        self.node.messages[message_name] = message
        print(f"Message uploaded: {message_name}")
        return service_pb2.UploadMessageResponse(saved=True)
    
class MessageDService(service_pb2_grpc.DownloadMessageServicer):
    def __init__(self, node):
        self.node = node

    def DownloadMessage(self, request, context):
        print("Download message request received")
        message_name = request.message_name
        message = self.node.messages[message_name] if message_name in self.node.messages else None
        if message:
            print(f"Message found: {message_name}")
            return service_pb2.DownloadMessageResponse(message=message)
        else:
            print(f"Message not found: {message_name}")
            return service_pb2.DownloadMessageResponse(message="Not found")

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
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        self.id = getHash(ip + ":" + str(port))
        self.pred = (self.ip, self.port)
        self.predID = self.id
        self.succ = (self.ip, self.port)
        self.succID = self.id
        self.finger_table = OrderedDict()
        self.messages = {}
        self.http_client = HTTPClient(ip, port)
        self.grpc_server = None

    def get_id(self):
        return self.id

    def listen(self):
        print(f"Server is listening on {self.ip}:{self.port}")
        server = ThreadingHTTPServer((self.ip, self.port), lambda *args, **kwargs: RequestHandler(self, *args, **kwargs))
        server.serve_forever()

    def connection_thread(self, ip, port, connectionType, dataforprocces):
        if connectionType == 4:
            self.update_successor(ip, int(port))
        
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
            message_name = input("Enter message name: ")
            message = input("Enter message: ")
            message_id = getHash(message_name)
            addres = self.getSuccessor(self.address[0], self.address[1], message_id)
            ip, port = addres.split(":")
            self.upload_message(ip, int(port), message_name, message)
        elif choice == 4:
            message_name = input("Enter message name: ")
            message_id = getHash(message_name)
            addres = self.getSuccessor(self.address[0], self.address[1], message_id)
            ip, port = addres.split(":")
            self.download_message(ip, int(port), message_name)
        elif choice == 5:
            self.print_finger_table()
        elif choice == 6:
            self.print_predecessor_successor()
        elif choice == 7:
            for key, value in self.messages.items():
                print(f"Message name: {key}, Message: {value}, Message ID: {getHash(key)}")
        else:
            print("Invalid choice")

    def upload_message(self, ip, port, message_name, message):
        print("Uploading message")
        with grpc.insecure_channel(f'{ip}:{int(port) + 1}') as channel:
            stub = service_pb2_grpc.UploadMessageStub(channel)
            request = service_pb2.UploadMessageRequest(message=message, message_name=message_name)
            response = stub.UploadMessage(request)
            print("Upload status: " + str(response.saved))

    def download_message(self, ip, port, message_name):
        print("Downloading message")
        with grpc.insecure_channel(f'{ip}:{int(port) + 1}') as channel:
            stub = service_pb2_grpc.DownloadMessageStub(channel)
            request = service_pb2.DownloadMessageRequest(message_name=message_name)
            response = stub.DownloadMessage(request)
            print("Message:", response.message)

    def send_join_request(self, ip, port): 
        succ = self.getSuccessor(ip, port, self.id)
        succ_ip, succ_port = succ.split(":")
        print(f"Successor found: {succ}")
        with grpc.insecure_channel(f'{succ_ip}:{int(succ_port) + 1}') as channel:
            stub = service_pb2_grpc.JoinnodeStub(channel)
            request = service_pb2.JoinRequest(address=f"{self.ip}:{self.port}")
            response = stub.JoinNode(request)
        
        print(f"My new predecessor: {response.address}")
        # Actualiza el predecesor y sucesor de acuerdo a la respuesta
        pred_ip, pred_port = response.address.split(":")
        self.update_predecessor(pred_ip, int(pred_port))
        self.update_successor(succ_ip, int(succ_port))
    
        # Actualiza el sucesor del predecesor
        print("Updating predecessor's successor")
        self.http_client.send_request('/connect', self.pred[0], self.pred[1], json.dumps({"ip": self.ip, "port": self.port, "connectionType": 4}))

    # Get the successor of the node # (CLIENT SIDE)
    def getSuccessor(self, ip, port, keyID):
        ipsearch = ip
        portsearch = port
        searchNode = True
        while searchNode:
            with grpc.insecure_channel(f'{ipsearch}:{int(portsearch) + 1}') as channel:
                stub = service_pb2_grpc.SearchsuccStub(channel)
                # print(f"sending sDataList [3, {keyID}]")
                request = service_pb2.LookupIDRequest(idNode=keyID)
                response = stub.LookupID(request)
                ipsearch, portsearch = response.address.split(":")
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
        print(f"Successor    N.ID: {self.succID} / {self.succ[0]}:{self.succ[1]}")
    
    def update_finger_table(self):
        print("Updating F Table")
        for i in range(MAX_BITS):
            entryId = (self.id + (2 ** i)) % MAX_NODES
            # If only one node in network
            if self.succ == self.address:
                print("Only one node in network")
                self.finger_table[entryId] = (self.id, self.address)
                continue
            # If multiple nodes in network, we find succ for each entryID
            address = self.getSuccessor(self.succ[0],self.succ[1],entryId)
            recvId = getHash(address)
            ipres, portres = address.split(":")
            address = (ipres, int(portres))
            self.finger_table[entryId] = (recvId, address)



    def update_others_finger_table(self):
        print("Updating other F Tables")
        here = self.succ  
        while True:
            if here == self.address:
                break
            try:
                with grpc.insecure_channel(f'{here[0]}:{here[1] + 1}') as channel:
                    stub = service_pb2_grpc.UpdatetableStub(channel)
                    request = service_pb2.UpdateTableRequest()
                    response = stub.UpdateTable(request)
                    succ_ip, succ_port = response.address.split(":")
                    here = (succ_ip, int(succ_port))
                    if here == self.succ:
                        break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def print_finger_table(self):
        print("Printing F Table")
        for key, value in self.finger_table.items(): 
            print("KeyID:", key, "Value", value)

    def show_menu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload Message\n4. Download Messages\n5. Print Finger Table\n6. Print my predecessor and successor\n6. Print my messages\n")

    def start_grpc_server(self):
        self.grpc_server = grpc.server(ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_SearchsuccServicer_to_server(SearchsuccService(self), self.grpc_server)
        service_pb2_grpc.add_JoinnodeServicer_to_server(JoinnodeService(self),  self.grpc_server)
        service_pb2_grpc.add_UpdatetableServicer_to_server(TableService(self), self.grpc_server)
        service_pb2_grpc.add_UploadMessageServicer_to_server(MessageService(self), self.grpc_server)
        service_pb2_grpc.add_DownloadMessageServicer_to_server(MessageDService(self), self.grpc_server)
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