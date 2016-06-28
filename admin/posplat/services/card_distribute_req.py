# coding=utf-8
from posplat.ISO8583.ISO8583 import ISO8583
from posplat.services import PosRequest
from posplat.services.card_distribute_service import CardDistributeService


class CardDistributeRequest(PosRequest):
    def __init__(self, service, sys_trace_id='', merchant_type='', acquire_institute_code='', forward_institute_code='',
                 term_id='', merchant_id='', currency_code='', mac=''):
        super(CardDistributeRequest, self).__init__('1000', '090000', service, sys_trace_id, merchant_type,
                                                    acquire_institute_code, forward_institute_code, term_id,
                                                    merchant_id, mac)
        self.currency_code = currency_code

    def to_str(self):
        iso = ISO8583()
        iso.setMTI(self.mti)
        iso.setBit(3, self.precessing_code)
        iso.setBit(7, self.trans_datetime)
        iso.setBit(11, self.sys_trace_id)
        iso.setBit(12, self.deal_time)
        iso.setBit(13, self.deal_date)
        iso.setBit(18, self.merchant_type)
        iso.setBit(32, self.acquire_institute_code)
        iso.setBit(33, self.forward_institute_code)
        iso.setBit(41, self.term_id)
        iso.setBit(42, self.merchant_id)
        iso.setBit(49, self.currency_code)
        iso.setBit(62, self.service.to_str())
        iso.setBit(128, self.mac)
        data = iso.getRawIso()
        return data


def card_distribute_request(sys_trace_id, merchant_type, acquire_institute_code, forward_institute_code,
                            term_id, merchant_id, currency_code, mac, batch_serial_id, deal_seq, retry_times,
                            order_id, card_no, card_money, card_auth_code):
    service = CardDistributeService(batch_serial_id, deal_seq, retry_times,
                                    order_id, card_no, card_money, card_auth_code)
    request = CardDistributeRequest(service, sys_trace_id, merchant_type, acquire_institute_code, forward_institute_code,
                                    term_id, merchant_id, currency_code, mac)
    data = request.to_str()
    print data
