import re
import socket
import thread
from multiprocessing import Queue

HOST="localhost"
PORT=1111

def process_request(recieved_data, q):
         #PING PACKET ID=631 TIME=2013-06-29 13:49:41.465531 TAG=00:11:C5:48 RDR=00:11:C5:45 T=25.95 Input=00 Lqi= 63
         m = re.match("PING PACKET ID=(?P<ID>.*) TIME=(?P<TIME>.*) TAG=(?P<TAG>.*) RDR=(?P<RDR>.*) T=(?P<T>.*) Input=(?P<I>.*) Lqi=(?P<LQI>.*)", recieved_data)
         if m:
            q.put(m.groupdict())
            print "RECIEVE:", recieved_data

class DataStream():
    def __init__(self, q, host, port):
        self.q = q
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print host, port
        self.s.bind((host, port))
        self.s.listen(5)
    def serve(self):
        while True:
            try:
                c, addr = self.s.accept()
                data = c.recv(1024)
            except:
                pass
            else:
                thread.start_new_thread(process_request, (data, self.q))
    def __del__(self):
        self.s.close()

if __name__ == "__main__":
    queue = Queue()
    server = DataStream(queue, HOST, PORT)
    server.serve()
