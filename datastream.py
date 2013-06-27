import re
import SocketServer
import multiprocessing
HOST="localhost"
PORT=1111

class DataStream(SocketServer.TCPServer):
    def __init__(self, q, server_address, RequestHandlerClass, bind_and_activate):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.q = q
    def process_request(self, request, client_address):
         recieved_data = request.recv(1024).strip()
         m = re.match("PING PACKET TIME=(?P<TIME>.*) ID=(?P<ID>.*) TAG=(?P<TAG>.*) RDR=(?P<RDR>.*) T=(?P<T>.*) Lqi=(?P<LQI>.*)", recieved_data)
         if m:
            self.q.put(m.groupdict())
            print "RECIEVE:", recieved_data

if __name__ == "__main__":
    server = DataStream((HOST, PORT), None, True)
    server.serve_forever()
