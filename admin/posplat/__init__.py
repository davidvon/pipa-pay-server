import traceback
from app import logger
from config import POS_PLAT_SERVER_PORT, POS_PLAT_SERVER_IP
from posplat.ISO8583.ISO8583 import ISO8583
from posplat.ISO8583.ISOErrors import *
import socket


def sync_call(request_msg):
    logger.debug('IN::>>> [%s]' % request_msg)
    s = None
    res_list = socket.getaddrinfo(POS_PLAT_SERVER_IP, POS_PLAT_SERVER_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
    for res in res_list:
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error:
            s.close()
            s = None
            continue
        break
    if s is None:
        logger.error('EXCEPT[%x]:: could not connect POS platform server !!!' % id(s))
        return

    try:
        s.send(request_msg)
        logger.info('REQ[%x]::>>> [%s]' % (id(s), request_msg))
        ans = s.recv(204800)
        logger.info('ACK[%x]::<<< [%s]' % (id(s), ans))
        return ans
    except Exception as e:
        logger.error(traceback.print_exc())
        logger.error('EXCEPT[%x]:: %s' % (id(s), e.message))
    finally:
        s.close()
