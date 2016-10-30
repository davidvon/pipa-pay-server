# -*- coding: utf-8 -*-
import os
from flask import redirect, request, flash
from flask.ext.admin import expose
from flask.ext.admin.form import rules, FileUploadField
from flask.ext.admin.helpers import validate_form_on_submit
from wtforms import SelectField, TextField

from app import db
from models import WechatTextReply, WechatNewsReply, WechatSubscribeReply, WechatUselessWordReply, WechatMenu
from config import MEDIA_TYPE_TEXT, MEDIA_TYPE_URL, LIKE_MATCH, TOTAL_MATCH, MEDIA_TYPE_NEWS
from app.view import admin, BaseModelView


class WeixinAccountModelView(BaseModelView):
    form_excluded_columns = ('sub_menus')
    column_exclude_list = ('url')
    form_overrides = dict(trigger_type=SelectField, message_text=TextField)
    form_args = dict(
        trigger_type=dict(
            choices=[(MEDIA_TYPE_TEXT, u'文本内容'), (MEDIA_TYPE_URL, u'网址链接')]
        ))
    column_labels = {'name': u'菜单', 'menu': u'主菜单', 'trigger_type': u'触发类型', 'parent': u'上级菜单',
                     'message_text': u'消息内容', 'url': 'URL链接', 'account_id': u'微信公共号',
                     'account_name': u'微信公众名称', 'origin_id': u'微信原始ID',
                     'app_id': u'微信APP ID', 'app_secret': u'微信APP私钥', 'seqid': '顺序编号'}


class MenuModelView(WeixinAccountModelView):
    list_template = './models/weixin_menu_list.html'


# ********** text_reply *********
REPLY_NONE = '0'
REPLY_TEXT = '1'
REPLY_NEWS = '2'
REPLY_SYSTEM = '3'


class ReplyModelView(BaseModelView):
    form_overrides = dict(match_type=SelectField, select_type=SelectField)
    form_args = dict(
        match_type=dict(
            choices=[(LIKE_MATCH, u'部分匹配'), (TOTAL_MATCH, u'完全匹配')]
        ),
        select_type=dict(
            choices=[(MEDIA_TYPE_TEXT, u'文字内容'), (MEDIA_TYPE_NEWS, u'图像文字'), (MEDIA_TYPE_URL, u'网址链接')]
        ))
    column_labels = {'keyword': u'关键字', 'match_type': u'匹配类型', 'text': u'文字内容', 'image_news_item': u'图文素材',
                     'title': u'标题', 'image': u'图文', 'description': '描述', 'url': 'URL链接', 'content': '内容',
                     'thumb_image': u'缩小图片', 'image_news': u'图文素材', 'menu': u'菜单链接', 'select_type': u'应答类型',
                     'image_news_id': '图文素材编号', 'menu_id': '目录编号'}


class SubscribeModelView(BaseModelView):
    form_overrides = dict(select_type=SelectField)
    form_args = dict(
        select_type=dict(
            choices=[(MEDIA_TYPE_TEXT, u'文字内容'), (MEDIA_TYPE_NEWS, u'图像文字'), (MEDIA_TYPE_URL, u'网址链接')]
        ))
    column_labels = {'image_news_id': u'图像素材编号', 'menu_id': u'菜单编号', 'select_type': u'应答类型',
                     'text': u'文字内容', 'image_news': u'图文素材', 'menu': u'菜单链接'}
    column_list = ('select_type', 'image_news_id', 'menu_id')


class UselessModelView(SubscribeModelView):
    column_labels = {'image_news_id': u'图像素材编号', 'menu_id': u'菜单编号', 'select_type': u'应答类型',
                     'text': u'文字内容', 'image_news': u'图文素材', 'menu': u'菜单链接'}


class TextModelView(ReplyModelView):
    column_list = ('keyword', 'match_type', 'text')


class NewsModelView(ReplyModelView):
    column_list = ('keyword', 'match_type', 'image_news_id')


admin.add_view(TextModelView(WechatTextReply, db.session, tagid='service-menu', icon='fa-weixin',
                             name=u"文字回复", category=u"微信设置"))
admin.add_view(NewsModelView(WechatNewsReply, db.session, tagid='service-menu', icon='fa-weixin',
                             name=u"图文回复", category=u"微信设置"))
admin.add_view(SubscribeModelView(WechatSubscribeReply, db.session, tagid='service-menu', icon='fa-weixin',
                                  name=u"关注时自动回复", category=u"微信设置"))
admin.add_view(UselessModelView(WechatUselessWordReply, db.session, tagid='service-menu', icon='fa-weixin',
                                name=u"无效词自动回复", category=u"微信设置"))
admin.add_view(MenuModelView(WechatMenu, db.session, tagid='service-menu', icon='fa-weixin',
                             name=u"服务号自定义菜单", category=u"微信设置"))
