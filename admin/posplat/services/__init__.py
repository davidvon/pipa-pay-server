import datetime


class PosRequest(object):
    def __init__(self, mti, precessing_code, service, sys_trace_id='', merchant_type='', acquire_institute_code='',
                 forward_institute_code='', term_id='', merchant_id='', mac=''):
        self.mti = mti
        self.precessing_code = precessing_code
        self.trans_datetime = datetime.datetime.now().strftime('%m%d%H%M%S')
        self.deal_time = datetime.datetime.now().strftime('%H%M%S')
        self.deal_date = datetime.datetime.now().strftime('%m%d')
        self.sys_trace_id = sys_trace_id
        self.merchant_type = merchant_type
        self.acquire_institute_code = acquire_institute_code
        self.forward_institute_code = forward_institute_code
        self.term_id = term_id
        self.merchant_id = merchant_id
        self.mac = mac
        self.service = service

    def to_str(self):
        pass


class PosResponse(object):
    def __init__(self, msg):
        self.msg = msg
        self.precessing_code = ''
        self.mti = ''

    def load(self):
        pass


class PosService(object):
    def __init__(self):
        pass

    def to_str(self):
        pass

    def load(self, data):
        pass
