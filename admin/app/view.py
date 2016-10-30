# -*- coding: utf-8 -*-
from flask.ext.admin import Admin, AdminIndexView, expose, BaseView
from flask.ext.admin.contrib.sqla import ModelView
from flask import render_template, request, flash
from flask.ext.admin.menu import MenuLink
from flask.ext.login import current_user, login_required
from flask import redirect
from app import db, app, config
from utils.util import staff_role_required


@app.route('/')
@login_required
def app_entry():
    return redirect('/admin')


@app.errorhandler(403)
@login_required
def forbidden(error):
    return render_template('base/403.html', admin_base_template='base/_layout.html',
                           admin_view=admin.index_view, user=current_user), 403


@app.errorhandler(404)
@login_required
def not_found(error):
    return render_template('base/404.html', admin_base_template='base/_layout.html',
                           admin_view=admin.index_view, user=current_user), 404


@app.errorhandler(500)
@login_required
def internal_error(error):
    db.session.rollback()
    return render_template('base/500.html', admin_base_template='base/_layout.html',
                           admin_view=admin.index_view, user=current_user), 500


class BaseAdminView(BaseView):
    def __init__(self, name=None, category=None, endpoint=None, url=None,
                 static_folder=None, static_url_path=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None, tagid=None, icon=None):
        super(BaseAdminView, self).__init__(name, category, endpoint, url, static_folder, static_url_path,
                                            menu_class_name, menu_icon_type, menu_icon_value)
        self.tag_id = tagid
        self.icon = icon

    def is_accessible(self):
        return current_user.has_role(config.ROLE_SHOP_STAFF) or current_user.has_role(
            config.ROLE_SHOP_STAFF_READONLY) or current_user.has_role(config.ROLE_ADMIN)


class BaseModelView(ModelView):
    can_push = True
    action_tag = None
    column_hide_backrefs = False

    def __init__(self, model, session, tagid='', icon='', name=None, category=None, endpoint=None, url=None):
        super(BaseModelView, self).__init__(model, session, name, category, endpoint, url)
        self.tag_id = tagid
        self.icon = icon

    list_template = './admin/list.html'
    create_template = './admin/create.html'
    edit_template = './admin/edit.html'

    def is_accessible(self):
        return current_user.has_role(config.ROLE_SHOP_STAFF) or \
               current_user.has_role(config.ROLE_SHOP_STAFF_READONLY) or \
               current_user.has_role(config.ROLE_ADMIN)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or current_user.has_role(config.ROLE_ADMIN):
            return super(BaseModelView, self).create_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or current_user.has_role(config.ROLE_ADMIN):
            return super(BaseModelView, self).edit_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or current_user.has_role(config.ROLE_ADMIN):
            return super(BaseModelView, self).delete_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)


class StaffModelView(BaseModelView):
    def __init__(self, model, session, tagid='', icon='', name=None, category=None, endpoint=None, url=None):
        super(StaffModelView, self).__init__(model, session, tagid, icon, name, category, endpoint, url)

    def is_accessible(self):
        return True

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or \
           current_user.has_role(config.ROLE_ADMIN) or \
           current_user.has_role(config.ROLE_FETCH_STEWARD) or \
           current_user.has_role(config.ROLE_POST_STEWARD):
            return super(BaseModelView, self).create_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or \
           current_user.has_role(config.ROLE_ADMIN) or \
           current_user.has_role(config.ROLE_FETCH_STEWARD) or \
           current_user.has_role(config.ROLE_POST_STEWARD):
            return super(BaseModelView, self).edit_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        if current_user.has_role(config.ROLE_SHOP_STAFF) or \
           current_user.has_role(config.ROLE_ADMIN) or \
           current_user.has_role(config.ROLE_FETCH_STEWARD) or \
           current_user.has_role(config.ROLE_POST_STEWARD):
            return super(BaseModelView, self).delete_view()
        flash('没有权限访问此页面.')
        return redirect(request.referrer)


class BaseMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.has_role(config.ROLE_SHOP_STAFF) or current_user.has_role(
            config.ROLE_SHOP_STAFF_READONLY) or current_user.has_role(config.ROLE_ADMIN)


class IndexView(AdminIndexView):
    @expose('/')
    @staff_role_required
    def index(self):
        args = dict(orders_count=0, customers_today_count=0,
                    customers_total_count=0, visitor_total_count=0,
                    customers_register_top=[], customers_visit_top=[],
                    services_top=[], orders_top=[],
                    sales_money=0, user=current_user.id)
        return self.render('admin/index.html', args=args)


admin = Admin(app, template_mode='bootstrap3', base_template='base/_layout.html', index_view=IndexView())

