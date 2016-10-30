# -*- coding: utf-8 -*-
from flask.ext.login import current_user, login_required
from flask import render_template
from wtforms import SelectField

from app import app, config
from app.view import admin, BaseModelView


@app.route('/shop')
@login_required
def firm_index(type=None, search=None, page=None):
    is_firm = not current_user.has_role(config.ROLE_ADMIN)
    data = [0, 0, 0]
    return render_template('/admin/index.html', is_staff_user=is_firm, admin_view=admin.index_view,
                           customers=data[0], groupons=data[1],
                           user=current_user, todos=data[2])


@app.route('/admin/setting/account')
@login_required
def setting_account():
    return render_template('/setting/account.html')


class ServiceView(BaseModelView):
    column_filters = ('title', 'service_category.name', 'service_category.main_category.name', 'flat_price', 'price',
                      "award_score")
    column_searchable_list = ('title', 'flat_price', 'price', 'service_category.name',
                              'service_category.main_category.name', "award_score")
    column_exclude_list = ('detail', 'content', 'properties', 'thumb_image', 'services', 'sub_title', 'create_time',
                           'price_unit', 'status')
    form_excluded_columns = ('services', 'images')
    column_labels = {'shop': '洗衣店', 'service_category': '服务类别',
                     'flat_price': u'价格上限', 'price': u'价格下限', 'title': '标题', 'detail': '介绍内容',
                     'properties': '参数属性', 'thumb_image': '缩略图', 'images': '图片', 'series': '系列',
                     'award_score': '积分', 'tags': '标签', 'top': '置顶', 'status': '状态',
                     'create_time': '创建时间', 'sub_title': '副标题', 'price_unit': '价格单位',
                     'service_category.name': '服务小类', 'service_category.main_category.name': '服务大类'}
    column_sortable_list = ('title', 'flat_price', 'price', 'award_score')
    form_overrides = dict(status=SelectField, top=SelectField)
    form_args = dict(
        status=dict(choices=[('1', u'销售中'), ('2', u'已下架')]),
        top=dict(choices=[('0', u'否'), ('1', u'是')])
    )

    def status_fmt(self, context, model, name):
        return '销售中' if model.status == 1 else '已下架'

    column_formatters = dict({"status": status_fmt})


class ShopView(BaseModelView):
    column_filters = ('city.city_name', 'phone', 'name', 'phone')
    column_labels = {'city': u'城市', 'city.city_name': '城市名称', 'name': u'洗衣店名称', 'zone': '区域',
                     'address': u'地址', 'longitude': '经度', 'latitude': '纬度', 'phone': '联系电话',
                     'logo': '商标'}


class ServiceMainCategoryView(BaseModelView):
    column_filters = ('name', )
    column_labels = {'name': u'服务大类', 'thumb_image': u'省略图'}
    form_excluded_columns = ('categories', )


class ServiceCategoryView(BaseModelView):
    column_filters = ('name', )
    column_labels = {'name': u'产品类别', 'main_category': '主类', 'thumb_image': u'省略图'}
    form_excluded_columns = ('services', 'categories')
    column_exclude_list = ('categories', )
    column_searchable_list = ('name', 'main_category.name')


class ProductTagView(BaseModelView):
    column_labels = {'name': u'标签', 'service_category': '产品类别', 'services': '产品列表'}
    form_excluded_columns = ('services', )


class ServiceImagesView(BaseModelView):
    column_labels = {'service': u'产品', 'image': '图片'}
    column_exclude_list = ('service_images', )
    form_excluded_columns = ('service_images', )


