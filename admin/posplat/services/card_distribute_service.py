from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62
from posplat.services import PosService


class CardDistributeService(PosService):
    def __init__(self, batch_serial_id='', deal_seq='', retry_times='', order_id='', card_no='',
                 card_face_value='', card_auth_code=''):
        super(CardDistributeService, self).__init__()
        self.batch_serial_id = batch_serial_id
        self.deal_seq = deal_seq
        self.retry_times = retry_times
        self.order_id = order_id
        self.card_no = card_no
        self.card_face_value = card_face_value
        self.card_auth_code = card_auth_code

    def to_str(self):
        iso = ISO8583_BIT62()
        iso.setBit(0x11, self.batch_serial_id)
        iso.setBit(0x12, self.deal_seq)
        iso.setBit(0x15, self.retry_times)
        iso.setBit(0x42, self.order_id)
        iso.setBit(0xa0, self.card_no)
        iso.setBit(0xb0, self.card_face_value)
        iso.setBit(0xb3, self.card_auth_code)
        return iso.getRawIso()

    def load(self, data):
        iso = ISO8583_BIT62(data)
        self.batch_serial_id = iso.getBit(0x11)
        self.deal_seq = iso.getBit(0x12)
        self.retry_times = iso.getBit(0x15)
        self.order_id = iso.getBit(0x42)
        self.card_no = iso.getBit(0xa0)
        self.card_face_value = iso.getBit(0xb0)
        self.card_auth_code = iso.getBit(0xb3)