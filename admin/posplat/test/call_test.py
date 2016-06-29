from ISO8583.ISO8583 import ISO8583
from posplat import sync_call

__author__ = 'fengguanhua'


iso = ISO8583()
iso.setMTI('0800')
iso.setBit(3, '300000')
iso.setBit(24, '045')
iso.setBit(41, '11111111')
iso.setBit(42, '222222222222222')
iso.setBit(63, 'This is a Test Message')
message = iso.getNetworkISO()
print message

echo = sync_call(message)
print echo
assert(len(echo) > 0)

isoAns = ISO8583()
isoAns.setNetworkISO(echo)
v1 = isoAns.getBitsAndValues()
for v in v1:
    print ('bit[%s] type[%s] value[%s]' % (v['bit'], v['type'], v['value']))
assert(isoAns.getMTI() == '0810')
