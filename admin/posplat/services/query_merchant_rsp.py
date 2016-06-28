# coding=utf-8
from posplat.ISO8583.ISO8583 import ISO8583
from posplat.services import PosResponse
from posplat.services.query_merchant_service import QueryMerchantService


class QueryMerchantResponse(PosResponse):
    def __init__(self, msg):
        super(QueryMerchantResponse, self).__init__(msg)
        self.service = QueryMerchantService()
        self.trans_datetime = ''
        self.deal_time = ''
        self.deal_date = ''
        self.sys_trace_id = ''
        self.merchant_type = ''
        self.acquire_institute_code = ''
        self.forward_institute_code = ''
        self.ack_code = ''
        self.term_id = ''
        self.merchant_id = ''
        self.mac = ''

    def load(self):
        iso = ISO8583(iso=self.msg)
        self.mti = iso.getMTI()
        self.precessing_code = iso.getBit(3)
        self.trans_datetime = iso.getBit(7)
        self.sys_trace_id = iso.getBit(11)
        self.deal_time = iso.getBit(12)
        self.deal_date = iso.getBit(13)
        self.merchant_type = iso.getBit(18)
        self.acquire_institute_code = iso.getBit(32)
        self.forward_institute_code = iso.getBit(33)
        self.ack_code = iso.getBit(39)
        self.term_id = iso.getBit(41)
        self.merchant_id = iso.getBit(42)
        service_data = iso.getBit(62)
        self.service.load(service_data)
        self.mac = iso.getBit(128)


def query_merchant_response(msg):
    response = QueryMerchantResponse(msg)
    response.load()
    return response
