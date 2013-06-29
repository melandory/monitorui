import random
import socket
from sys import exit
from datetime import datetime
import time

#send random packet each SEC seconds
SEC=5
#socket setup
HOST = "localhost"
PORT=1111
#how many random packets should be generated
PACK_COUNT=1000
TAGS = 2

def gen_random_packet(id):
    RDR = "45"
    IP_PREF = "00:11:C5:"
    #PING PACKET ID=631 TIME=2013-06-29 13:49:41.465531 TAG=00:11:C5:48 RDR=00:11:C5:45 T=25.95 Input=00 Lqi= 63
    template = "PING PACKET ID=%(id)s TIME=%(time)s TAG=%(ip_pref)s%(tag)s RDR=%(ip_pref)s%(rdr)s T=%(t)s Input=00 Lqi=%(lqi)s"
    return template % {"id":id,\
                       "time": datetime.now(),\
                       "ip_pref":IP_PREF,\
                       "tag":random.randint(0, TAGS),\
                       "rdr": RDR, 
                       "t":random.uniform(15, 30),\
                        "lqi":int(random.uniform(0, 255))}

if __name__ == "__main__":
    for id in range(PACK_COUNT):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print "Socket creation has failed. Reason:{0}".format(msg)
            exit()
        s.connect((HOST, PORT))

        message = gen_random_packet(id)
        try :
            s.send(message)
            print "SEND", message
        except socket.error:
            print 'Send failed'
            exit()
        s.close()
        time.sleep(SEC)
