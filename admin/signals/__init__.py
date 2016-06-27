__author__ = 'fengguanhua'

from blinker import Namespace
weixin_signals = Namespace()

signal_order_notify = weixin_signals.signal('order_notify')
signal_customer_message_cached_notify = weixin_signals.signal('customer_message_cached_notify')
