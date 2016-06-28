from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62

p = ISO8583_BIT62()
p.setBit(1, "123")
p.setBit(2, "456")
p.setBit(3, 4897)
p.setBit(6, 'F')
p.setBit(7, '2F')
p.setBit(11, 'A1000234')
p.setBit(88, 'A123')
r = p.getRawIso()
print r

q = ISO8583_BIT62(r)
assert( q.getBit(1) == "00000123")
assert( q.getBit(2) == "0000000456")
assert( q.getBit(3) == '4897')
assert( q.getBit(6) == 'F')
assert( q.getBit(7) == '2F')
assert( q.getBit(11) == 'A1000234')
assert( q.getBit(88) == 'A123')
