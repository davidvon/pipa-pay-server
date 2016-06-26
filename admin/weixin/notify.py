# -*- coding: utf-8 -*-
from app import logger
import config
from models import User
# from signals import signal_order_notify
from weixin.views import weixin
from cache.public import url_from_cache


class OrderNotifyBase(object):
    def __init__(self, status, openid=None):
        self.status = status
        self.openid = openid

    def booking_order_notify(self, args, openid):
        pass

    def order_pay_confirmed_notify(self, args, openid):
        pass

    def order_status_change_notify(self, args, openid):
        pass

    def notify(self, args):
        pass


class CustomerOrderNotify(OrderNotifyBase):
    def booking_order_notify(self, args, openid):
        """
        {{first.DATA}}
        单号：{{keyword1.DATA}}
        姓名：{{keyword2.DATA}}
        电话：{{keyword3.DATA}}
        地址：{{keyword4.DATA}}
        取衣时间：{{keyword5.DATA}}
        {{remark.DATA}}
        """

        template_id = 'XAa3kQ76ruWmEqFKSDfAct3m4dQ6Cp-j1-OZ3PPj50I' if config.ISONLINE else \
            'RKtd74YCSgG5tEmHsG_5ddbRaK8hTzHsyIZHQWTJh2c'
        push_data = dict(first={"value": "您好，您已下单成功", "color": "#173177"},
                         keyword1={"value": args['order_serial'], "color": "#173177"},
                         keyword2={"value": args['name'], "color": "#173177"},
                         keyword3={"value": args['phone'], "color": "#000000"},
                         keyword4={"value": args['address'], "color": "#173177"},
                         keyword5={"value": args['delivery_time'], "color": "#173177"},
                         remark={"value": '洗衣件数：%s\n\n比邻洗衣感谢您的预订，洗衣管家将第一时间与您联系。'% args['sum'], "color": "#173177"})
        order_url = "%smobile/personal/order?tab=0&uid=%s" % (url_from_cache(), openid)
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def order_pay_confirmed_notify(self, args, openid):
        """
        {{first.DATA}}
        订单编号：{{keyword1.DATA}}
        订单内容：{{keyword2.DATA}}
        订单金额：{{keyword3.DATA}}
        订单状态：{{keyword4.DATA}}
        {{remark.DATA}}
        """
        template_id = 'hhhp9z46Ql8xCjhI4cvDEuiUQf2wGBhn-kWjie4K-RY' if config.ISONLINE else \
            'tGBWVmXAUdB7gCnDnYGTVfXkO9rvaej4bm7HmT4V75Y'
        push_data = dict(first={"value": "您的订单已支付", "color": "#173177"},
                         keyword1={"value": args['order_serial'], "color": "#173177"},
                         keyword2={"value": '洗衣%s件' % args['sum'], "color": "#173177"},
                         keyword3={"value": args['price'], "color": "#173177"},
                         keyword4={"value": args['status'], "color": "#173177"},
                         Remark={"value": '详细订单请点击[详情]', "color": "#173177"})
        order_url = "%smobile/personal/order?tab=1&uid=%s" % (url_from_cache(), openid)
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def order_status_change_notify(self, args, openid):
        """
        {{first.DATA}}
        单号：{{keyword1.DATA}}
        商品：{{keyword2.DATA}}
        件数：{{keyword3.DATA}}
        状态：{{keyword4.DATA}}
        {{remark.DATA}}
        """
        template_id = '_HuE97r15jjWl8uxZKmBELLLRTp9oepckLYzNibx-Xo'  if config.ISONLINE else \
            'BUfIMn1xtiD9ikahiDhA90NJwxPB8pXOa_hun8hpqlE'
        status_info = '订单已取消' if self.status == 'cancel' else '订单信息有调整' if self.status == 'update' else '订单状态有新变更'
        remark = '洗衣管家提醒您，您的订单可以微信支付了' if not args['paid'] and args['price'] else ''
        push_data = dict(first={"value": '您的%s' % status_info, "color": "#173177"},
                         keyword1={"value": args.get('order_serial'), "color": "#173177"},
                         keyword2={"value": '预约洗衣\n订单金额：%s\n预约上门收衣时间：%s\n预约上门送衣时间：%s' % (args['price'], args['delivery_time'], args['received_time']), "color": "#000000"},
                         keyword3={"value": args.get('sum'), "color": "#173177"},
                         keyword4={"value": args.get('status'), "color": "#173177"},
                         remark={"value": remark, "color": "#173177"}
                         )
        order_url = "%smobile/personal/order?tab=1&uid=%s" % (url_from_cache(), openid)
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def notify(self, args):
        if self.status == 'booking':
            return self.booking_order_notify(args, self.openid)
        elif self.status == 'pay-confirm':
            return self.order_pay_confirmed_notify(args, self.openid)
        elif self.status == 'cancel':
            return self.order_status_change_notify(args, self.openid)
        elif self.status == 'update':
            return self.order_status_change_notify(args, self.openid)


class FirmOrderNotify(OrderNotifyBase):
    def booking_order_notify(self, args, openid):
        """新订单通知:
        {{first.DATA}}

        提交时间：{{tradeDateTime.DATA}}
        订单类型：{{orderType.DATA}}
        客户信息：{{customerInfo.DATA}}
        {{orderItemName.DATA}}：{{orderItemData.DATA}}
        {{remark.DATA}}
        """
        template_id = 'QszmWrX38Y0kp0IP2sYS5jxbkUKCx8vbjceXI6vI4jM' if config.IS_ONLINE else \
            'EZBgH4qX_ZWXU_o6ksYscvIKjz8gGJA9PtCT_27lp28'
        push_data = dict(first={"value": "您收到了一条新的订单", "color": "#173177"},
                         tradeDateTime={"value": args['order_time'], "color": "#173177"},
                         orderType={"value": '预约洗衣%s件' % args['sum'], "color": "#173177"},
                         customerInfo={"value": "%s %s" % (args['name'], args['phone']), "color": "#173177"},
                         orderItemName={"value": '预约上门收衣时间', "color": "#000000"},
                         orderItemData={"value": args['delivery_time'], "color": "#173177"},
                         remark={"value": '预约上门地址：%s \n\n请尽快确认价格及订单详情' % args['address'], "color": "#000000"})
        order_url = "%smobile/firm/orders?tab=0&uid=%s" % (url_from_cache(), openid)
        logger.info('[WEIXIN] order time:%s url:%s' % (args['order_time'], order_url))
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def order_pay_confirmed_notify(self, args, openid):
        """
        {{first.DATA}}
        订单编号：{{keyword1.DATA}}
        订单内容：{{keyword2.DATA}}
        订单金额：{{keyword3.DATA}}
        订单状态：{{keyword4.DATA}}
        {{remark.DATA}}
        """
        template_id = 'hhhp9z46Ql8xCjhI4cvDEuiUQf2wGBhn-kWjie4K-RY' if config.ISONLINE else \
            'tGBWVmXAUdB7gCnDnYGTVfXkO9rvaej4bm7HmT4V75Y'
        push_data = dict(first={"value": "客户（%s）订单支付已完成" % args['name'], "color": "#173177"},
                         keyword1={"value": args['order_serial'], "color": "#173177"},
                         keyword2={"value": '洗衣%s件' % args['sum'], "color": "#173177"},
                         keyword3={"value": args['price'], "color": "#173177"},
                         keyword4={"value": args['status'], "color": "#173177"},
                         Remark={"value": '详细订单请点击[详情]', "color": "#173177"})
        order_url = "%smobile/firm/orders?tab=1&uid=%s" % (url_from_cache(), openid)
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def order_status_change_notify(self, args, openid):
        """
        {{first.DATA}}
        单号：{{keyword1.DATA}}
        商品：{{keyword2.DATA}}
        件数：{{keyword3.DATA}}
        状态：{{keyword4.DATA}}
        {{remark.DATA}}
        """
        template_id = '_HuE97r15jjWl8uxZKmBELLLRTp9oepckLYzNibx-Xo'  if config.ISONLINE else \
            'BUfIMn1xtiD9ikahiDhA90NJwxPB8pXOa_hun8hpqlE'
        status_info = '订单已取消' if self.status == 'cancel' else '订单信息有调整' if self.status == 'update' else '订单状态有新变更'
        push_data = dict(first={"value": "客户（%s）%s" % (args['name'], status_info), "color": "#173177"},
                         keyword1={"value": args.get('order_serial'), "color": "#173177"},
                         keyword2={"value": '预约洗衣\n预约上门收衣时间：%s\n预约上门送衣时间：%s' % (args['delivery_time'], args['received_time']), "color": "#000000"},
                         keyword3={"value": args.get('sum'), "color": "#173177"},
                         keyword4={"value": args.get('status'), "color": "#173177"},
                         remark={"value": '', "color": "#173177"}
                         )
        order_url = "%smobile/firm/orders?tab=1&uid=%s" % (url_from_cache(), openid)
        weixin.weixin_helper.push_template_message(openid, template_id, push_data, order_url)

    def notify(self, args):
        assistants = User.query.filter_by(shop_id=args['shop_id'], active=1).all()
        # cash, create, pay-confirm, done
        for assistant in assistants:
            if not assistant.customer:
                continue
            if self.status == 'booking':
                return self.booking_order_notify(args, assistant.customer.openid)
            elif self.status == 'pay-confirm':
                return self.order_pay_confirmed_notify(args, assistant.customer.openid)
            elif self.status == 'cancel':
                return self.order_status_change_notify(args, assistant.customer.openid)
            elif self.status == 'update':
                return self.order_status_change_notify(args, assistant.customer.openid)


def order_notify(sender, **extra):
    args = extra['args']
    status = extra['status']  # booking, pay-confirm, done
    logger.info('[WEIXIN] order notify starting: [order.id:%s, status:%s] ...' % (args['order_serial'], status))
    customer_notify = CustomerOrderNotify(status, args['openid'])
    customer_notify.notify(args)
    firm_notify = FirmOrderNotify(status)
    firm_notify.notify(args)
    logger.info('[WEIXIN] sync order notify done: [id:%s,status:%s] ...' % (args['order_serial'], status))


# signal_order_notify.connect(order_notify)