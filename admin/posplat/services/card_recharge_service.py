from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62
from posplat.services import PosService


class CardRechargeService(PosService):
    def __init__(self, amount='', batch_serial_id='', deal_seq='', retry_times='', order_id='', card_no='',
                 service_type=''):
        super(CardRechargeService, self).__init__()
        self.amount = amount
        self.batch_serial_id = batch_serial_id
        self.deal_seq = deal_seq
        self.retry_times = retry_times
        self.order_id = order_id
        self.card_no = card_no
        self.service_type = service_type

    def to_str(self):
        iso = ISO8583_BIT62()
        iso.setBit(0x9,  self.amount)
        iso.setBit(0x11, self.batch_serial_id)
        iso.setBit(0x12, self.deal_seq)
        iso.setBit(0x15, self.retry_times)
        iso.setBit(0x42, self.order_id)
        iso.setBit(0xa0, self.card_no)
        iso.setBit(0xb2, self.service_type)
        return iso.getRawIso()

    def load(self, data):
        iso = ISO8583_BIT62(data)
        self.batch_serial_id = iso.getBit(0x11)
        self.deal_seq = iso.getBit(0x12)
        self.retry_times = iso.getBit(0x15)
        self.order_id = iso.getBit(0x42)
