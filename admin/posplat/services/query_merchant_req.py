# coding=utf-8
from posplat.ISO8583.ISO8583 import ISO8583
from posplat.services import PosRequest
from posplat.services.query_merchant_service import QueryMerchantService


class QueryMerchantRequest(PosRequest):
    def __init__(self, service, sys_trace_id='', merchant_type='', acquire_institute_code='', forward_institute_code='',
                 term_id='', merchant_id='', mac=''):
        super(QueryMerchantRequest, self).__init__('1000', '100000', service, sys_trace_id, merchant_type,
                                                   acquire_institute_code, forward_institute_code, term_id,
                                                   merchant_id, mac)

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
        iso.setBit(62, self.service.to_str())
        iso.setBit(128, self.mac)
        data = iso.getRawIso()
        return data


def query_merchant_request(sys_trace_id, merchant_type, acquire_institute_code, forward_institute_code,
                           term_id, merchant_id, mac, merchant_name, merchant_logo, merchant_address):
    service = QueryMerchantService(merchant_name, merchant_logo, merchant_address)
    request = QueryMerchantRequest(service, sys_trace_id, merchant_type, acquire_institute_code, forward_institute_code,
                                   term_id, merchant_id, mac)
    data = request.to_str()
    print data
