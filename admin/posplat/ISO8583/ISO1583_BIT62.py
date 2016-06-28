import binascii

from ISOErrors import ValueToLarge


class ISO8583_BIT62:
    _BIT_DEFAULT_VALUE = 0
    _BIT62_VALUE_TYPE = {
        0x01: ['0x01', 'FactoryCode', 'N', 8, 'n'],
        0x02: ['0x02', 'APPSequence', 'N', 10, 'n'],
        0x03: ['0x03', 'Random', 'B', 4, 'b'],
        0x04: ['0x04', 'KeyIndex', 'N', 1, 'n'],
        0x05: ['0x05', 'AlgIndex', 'N', 1, 'n'],
        0x06: ['0x06', 'KeyVersion', 'B', 1, 'b'],
        0x07: ['0x07', 'OnlineCount', 'B', 2, 'b'],
        0x08: ['0x08', 'Balance', 'B', 4, 'b'],
        0x09: ['0x09', 'Amount', 'B', 4, 'b'],
        0x0A: ['0x0A', 'TradeType', 'N', 1, 'n'],
        0X0B: ['0X0B', 'TermCode', 'ANS', 8, 'ans'],
        0x0C: ['0x0C', 'MAC1', 'B', 4, 'b'],
        0x0D: ['0x0D', 'MAC2', 'B', 4, 'b'],
        0x0E: ['0x0E', 'TAC', 'B', 4, 'b'],
        0x0F: ['0x0F', 'CountryCode', 'B', 1, 'b'],
        0x10: ['0x10', 'PSAMSequence', 'N', 10, 'n'],
        0x11: ['0x11', 'BatchNO', 'N', 4, 'n'],
        0x12: ['0x12', 'SerialNO', 'N', 9, 'n'],
        0x13: ['0x13', 'TOPUPKey', 'B', 28, 'b'],
        0x14: ['0x14', 'OPResult', 'B', 1, 'b'],
        0x15: ['0x15', 'RepeatCount', 'B', 1, 'b'],
        0x16: ['0x16', 'UserPassword', 'B', 32, 'b'],
        0x17: ['0x17', 'HostDate', 'N', 4, 'n'],
        0x18: ['0x18', 'HostTime', 'N', 3, 'n'],
        0x19: ['0x19', 'AID', 'N', 16, 'n'],
        0x1A: ['0x1A', 'Ori_MerchantID', 'ANS', 15, 'ans'],
        0x1B: ['0x1B', 'Ori_TerminalID', 'ANS', 8, 'ans'],
        0x1C: ['0x1C', 'Ori_TransDate', 'N', 4, 'n'],
        0x1D: ['0x1D', 'Ori_TransTime', 'N', 3, 'n'],
        0x1E: ['0x1E', 'Ori_BatchNO', 'N', 4, 'n'],
        0x1F: ['0x1F', 'Ori_SerialNO', 'N', 3, 'n'],
        0x20: ['0x20', 'POS_SWVersion', 'N', 5, 'n'],
        0x21: ['0x21', 'PF_STVersion', 'N', 5, 'n'],
        0x22: ['0x22', 'POS_ParaVersion', 'N', 8, 'n'],
        0x23: ['0x23', 'PF_ParaVersion', 'N', 8, 'n'],
        0x24: ['0x24', 'POS_BLVersion', 'N', 5, 'n'],
        0x25: ['0x25', 'PF_BLVersion', 'N', 5, 'n'],
        0x26: ['0x26', 'SW_Size', 'B', 4, 'b'],
        0x27: ['0x27', 'SW_PageCount', 'B', 4, 'b'],
        0x28: ['0x28', 'BL_Count', 'B', 4, 'b'],
        0x29: ['0x29', 'POSKey', 'B', 40, 'b'],
        0x2A: ['0x2A', 'Ask_BLPage', 'N', 2, 'n'],
        0x30: ['0x30', 'POSPhyCode', 'ANS', 32, 'ans'],
        0x31: ['0x31', 'add money type', 'B', 1, 'b'],
        0x32: ['0x32', 'Sum_TradeCount', 'N', 2, 'n'],
        0x33: ['0x33', 'Sum_TradeAmount', 'N', 6, 'n'],
        0x34: ['0x34', 'Mobile_Number', 'N', 15, 'n'],
        0x35: ['0x35', 'Mobile_AccBAL', 'B', 4, 'b'],
        0x36: ['0x36', 'Merchant_AccBAL', 'B', 4, 'b'],
        0x37: ['0x37', 'Commission_Fee', 'B', 4, 'b'],
        0x38: ['0x38', 'OneCode_Withdraw', 'N', 8, 'n'],
        0x40: ['0x40', 'weixin_openid', 'ANS', 32, 'ans'],
        0x41: ['0x41', 'discount_amount', 'B', 4, 'b'],
        0x42: ['0x42', 'Order_no', 'N', 16, 'n'],
        0x43: ['0x43', 'Input_accounttype', 'ANS', 8, 'ans'],
        0x44: ['0x44', 'Input_accountno', 'ANS', 40, 'ans'],
        0x45: ['0x45', 'Batchdata_totalnum', 'B', 4, 'b'],
        0x46: ['0x46', 'Batchdata_downnum', 'B', 4, 'b'],
        0x47: ['0x47', 'Groupon_No', 'ANS', 20, 'ans'],
        0x48: ['0x48', 'Groupon_num', 'B', 4, 'b'],
        0x49: ['0x49', 'Stat_Date', 'ANS', 5, 'ans'],
        0x50: ['0x50', 'CBA token', 'ANS', 64, 'ans'],
        0x51: ['0x51', 'Name', 'ANS', 128, 'ans'],
        0x52: ['0x52', 'ID', 'ANS', 128, 'n'],
        0x53: ['0x53', 'UserPassward', 'ANS', 32, 'ans'],
        0x54: ['0x54', 'PayPassward', 'ANS', 32, 'ans'],
        0x55: ['0x55', 'OTP', 'ANS', 6, 'n'],
        0x56: ['0x56', 'Integral', 'N', 8, 'n'],
        0x57: ['0x57', 'Wallet type', 'B', 1, 'b'],
        0x58: ['0x58', 'Qr code', 'LLL', 512, 'n'],
        0x59: ['0x59', 'Bar code', 'LLL', 128, 'n'],
        0x60: ['0x60', 'Order status', 'B', 2, 'b'],
        0x61: ['0x61', 'Order subject', 'LLL', 256, 'n'],
        0x62: ['0x62', 'Orderid', 'ANS', 16, 'ans'],
        0x63: ['0x63', 'Userid', 'ANS', 64, 'ans'],
        0x64: ['0x64', 'Points', 'N', 4, 'n'],
        0x65: ['0x65', 'Redeem points', 'N', 4, 'n'],
        0X66: ['0X66', 'Accrual points', 'N', 4, 'n'],
        0x67: ['0x67', 'token', 'ANS', 128, 'ans'],
        0x68: ['0x68', 'checkin', 'B', 1, 'b'],
        0x69: ['0x69', 'First name', 'ANS', 128, 'ans'],
        0x70: ['0x70', 'Last name', 'ANS', 128, 'ans'],
        0x71: ['0x71', 'Start time', 'ANS', 20, 'ans'],
        0x72: ['0x72', 'End time', 'ANS', 20, 'n'],
        0x73: ['0x73', 'Issuer  number', 'ANS', 6, 'ans'],
        0x74: ['0x74', 'Issuer  name', 'ANS', 32, 'ans'],
        0x75: ['0x75', 'Card number', 'ANS', 32, 'ans'],
        0x76: ['0x76', 'ordertype', 'B', 1, 'b'],
        0x77: ['0x77', 'Order_no', 'N', 32, 'n'],
        0x78: ['0x78', 'yes_no', 'B', 1, 'b'],
        0xa0: ['0xa0', 'Card id', 'ANS', 32, 'ans'],
        0xa1: ['0xa1', 'card_type', 'B', 1, 'b'],
        0xa2: ['0xa2', 'title', 'ANS', 32, 'ans'],
        0xa3: ['0xa3', 'discount', 'B', 1, 'b'],
        0xa4: ['0xa4', 'least_cost', 'B', 4, 'b'],
        0xa5: ['0xa5', 'reduce_cost', 'B', 4, 'b'],
        0xa6: ['0xa6', 'brand_name', 'ANS', 32, 'ans'],
        0xa7: ['0xa7', 'logo_url', 'ANS', 256, 'ans'],
        0xa8: ['0xa8', 'can_consume', 'B', 1, 'b'],
        0xa9: ['0xa9', 'Time_limit', 'ANS', 256, 'ans'],
        0xb0: ['0xb0', 'cardprice', 'B', 4, 'b'],
        0xb1: ['0xb1', 'cardnum', 'B', 4, 'b'],
        0xb2: ['0xb2', 'cardbustype', 'B', 1, 'b'],
        0xb3: ['0xb3', 'authid', 'ANS', 8, 'ans'],
        0xc0: ['0xc0', 'address', 'ANS', 200, 'ans'],
        0xc1: ['0xc1', 'amounttoday', 'B', 4, 'b'],
        0xc2: ['0xc2', 'amountthismonth', 'B', 4, 'b']
    }

    # Default constructor of the ISO8583 BIT62 Object
    def __init__(self, iso=""):
        self.BITMAP_VALUES = {}
        self.__inicializeBitmapValues()
        if iso != "":
            self.__setIsoContent(iso)

    def __inicializeBitmapValues(self):
        for item in self._BIT62_VALUE_TYPE:
            self.BITMAP_VALUES[item] = self._BIT_DEFAULT_VALUE

    @staticmethod
    def __get_param(iso, offset):
        len = 1
        ch = iso[offset:offset + len]
        val = int(binascii.hexlify(ch), 16)
        if val & 0x80 == 0x80:
            len += 1
            val = int(binascii.hexlify(iso[offset:offset + len]) & 0x7FFF, 16)
        offset += len
        return val, offset

    def __getSubBitVlaue(self, iso, offset):
        _offset = offset
        t, _offset = self.__get_param(iso, _offset)
        l, _offset = self.__get_param(iso, _offset)
        v = iso[_offset:_offset + int(l)]
        offset = _offset + int(l)
        return t, l, v, offset

    def __setIsoContent(self, iso):
        self.BITMAP_VALUES = {}
        offset = 0
        while len(iso) > offset:
            t, l, v, offset = self.__getSubBitVlaue(iso, offset)
            if self.getBitType(t) == 'LL':
                if int(l) > self.getBitLimit(t):
                    raise ValueToLarge("This bit is larger than the especification!")
                self.BITMAP_VALUES[t] = v[2::]
            if self.getBitType(t) == 'LLL':
                if int(l) > self.getBitLimit(t):
                    raise ValueToLarge("This bit is larger than the especification!")
                self.BITMAP_VALUES[t] = v[3::]
            if self.getBitType(t) == 'N' or self.getBitType(t) == 'A' or self.getBitType(
                    t) == 'ANS' or self.getBitType(t) == 'B' or self.getBitType(t) == 'AN':
                self.BITMAP_VALUES[t] = v

    ################################################################################################
    # Return bit type
    def getBitType(self, bit):
        return self._BIT62_VALUE_TYPE[bit][2]

    # Return bit limit
    def getBitLimit(self, bit):
        return self._BIT62_VALUE_TYPE[bit][3]

    # Return bit value type
    def getBitValueType(self, bit):
        return self._BIT62_VALUE_TYPE[bit][4]

    # Return large bit name
    def getLargeBitName(self, bit):
        return self._BIT62_VALUE_TYPE[bit][1]

    # Set a value to a bit
    def setBit(self, bit, value):
        if self.getBitType(bit) == 'LL':
            self.__setBitTypeLL(bit, value)

        if self.getBitType(bit) == 'LLL':
            self.__setBitTypeLLL(bit, value)

        if self.getBitType(bit) == 'N':
            self.__setBitTypeN(bit, value)

        if self.getBitType(bit) == 'A':
            self.__setBitTypeA(bit, value)

        if self.getBitType(bit) == 'ANS':
            self.__setBitTypeANS(bit, value)

        if self.getBitType(bit) == 'B':
            self.__setBitTypeB(bit, value)
        return True

    # Set of type LL
    def __setBitTypeLL(self, bit, value):
        value = "%s" % value

        if len(value) > 99:
            # value = value[0:99]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))
        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        size = "%s" % len(value)

        self.BITMAP_VALUES[bit] = "%s%s" % (size.zfill(2), value)

    # Set of type LLL
    def __setBitTypeLLL(self, bit, value):
        value = "%s" % value

        if len(value) > 999:
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))
        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        size = "%s" % len(value)

        self.BITMAP_VALUES[bit] = "%s%s" % (size.zfill(3), value)

    # Set of type N,
    def __setBitTypeN(self, bit, value):
        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit))

    # Set of type A
    def __setBitTypeA(self, bit, value):
        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit))

    # Set of type B
    def __setBitTypeB(self, bit, value):
        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit))

    # Set of type ANS
    def __setBitTypeANS(self, bit, value):
        value = "%s" % value

        if len(value) > self.getBitLimit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getBitType(bit), self.getBitLimit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.getBitLimit(bit))

    def getRawIso(self):
        resp = ""
        for index in self._BIT62_VALUE_TYPE:
            item_val = self.BITMAP_VALUES[index]
            if item_val == self._BIT_DEFAULT_VALUE:
                continue
            t_val = "%02X" % index if index <= 0x7F else \
                "%04X" % (len(index) | 0x8000)
            t = binascii.a2b_hex(t_val)
            l_val = "%02X" % len(item_val) if len(item_val) <= 0x7F else \
                "%04X" % (len(item_val) | 0x8000)
            l = binascii.a2b_hex(l_val)
            resp = "%s%s%s%s" % (resp, t, l, item_val)
        return resp

    def getBit(self, bit):
        return self.BITMAP_VALUES.get(bit)


if __name__ == '__main__':
    index = 0x9F33
    val = '333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333'
    t_val = "%02X" % index if index <= 0xFF else "%04X" % index
    t = binascii.a2b_hex(t_val)
    l_val = "%02X" % len(val) if len(val) <= 0x7F else \
        "%04X" % (len(val) | 0x8000)
    l = binascii.a2b_hex(l_val)
    print t, l
