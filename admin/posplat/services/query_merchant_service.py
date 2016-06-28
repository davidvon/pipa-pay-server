from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62
from posplat.services import PosService


class QueryMerchantService(PosService):
    def __init__(self, name='', logo='', address=''):
        super(QueryMerchantService, self).__init__()
        self.name = name
        self.logo = logo
        self.address = address

    def to_str(self):
        iso = ISO8583_BIT62()
        iso.setBit(0xa6, self.name)
        iso.setBit(0xa7, self.logo)
        iso.setBit(0xc0, self.address)
        return iso.getRawIso()

    def load(self, data):
        iso = ISO8583_BIT62(data)
        self.name = iso.getBit(0xa6)
        self.logo = iso.getBit(0xa7)
        self.address = iso.getBit(0xc0)
