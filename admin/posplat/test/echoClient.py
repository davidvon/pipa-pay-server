from posplat.ISO8583.ISO8583 import ISO8583
from posplat.ISO8583.ISOErrors import *
import socket
import sys
import time

serverIP = "192.168.200.105"
serverPort = 8583

s = None
res_list = socket.getaddrinfo(serverIP, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM)
for res in res_list:
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error, msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error, msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print ('Could not connect :(')
    sys.exit(1)

iso = ISO8583()
iso.setMTI('0800')
iso.setBit(3, '300000')
iso.setBit(24, '045')
iso.setBit(41, '11111111')
iso.setBit(42, '222222222222222')
iso.setBit(63, 'This is a Test Message')
try:
    message = iso.getNetworkISO()
    s.send(message)
    print ('Sending ... %s' % message)
    ans = s.recv(204800)
    print ("\nInput ASCII |%s|" % ans)
    isoAns = ISO8583()
    isoAns.setNetworkISO(ans)
    v1 = isoAns.getBitsAndValues()
    for v in v1:
        print ('Bit %s of type %s with value = %s' % (v['bit'], v['type'], v['value']))

    if isoAns.getMTI() == '0810':
        print ("\tThat's great !!! The server understand my message !!!")
    else:
        print ("The server dosen't understand my message!")

except InvalidIso8583, ii:
    print ii

time.sleep(0.5)

print ('Closing...')
s.close()		
