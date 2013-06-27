import random
import socket
from sys import exit
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
    #PING PACKET ID=27 TAG=00:11:C5:49 RDR=00:11:C5:45 T=28.02 Lqi=213
    RDR = "45"
    IP_PREF = "00:11:C5:"
    
    template = "PING PACKET TIME=%(time)s ID=%(id)s TAG=%(ip_pref)s%(tag)s RDR=%(ip_pref)s%(rdr)s T=%(t)s Lqi=%(lqi)s"
    return template % {"id":id,\
                       "time": SEC*id,\
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
        s.connect((HOST , PORT))

        message = gen_random_packet(id)
        try :
            s.sendall(message)
            print "SEND", message
        except socket.error:
            print 'Send failed'
            exit()
        s.close()
        time.sleep(1)
