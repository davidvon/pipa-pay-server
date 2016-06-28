from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62
from posplat.services import PosService


class QueryTransSummaryService(PosService):
    def __init__(self, amount_today='', amount_month=''):
        super(QueryTransSummaryService, self).__init__()
        self.amount_today = amount_today
        self.amount_month = amount_month

    def to_str(self):
        iso = ISO8583_BIT62()
        iso.setBit(0xc1, self.amount_today)
        iso.setBit(0xc2, self.amount_month)
        return iso.getRawIso()

    def load(self, data):
        iso = ISO8583_BIT62(data)
        self.amount_today = iso.getBit(0xc1)
        self.amount_month = iso.getBit(0xc2)
