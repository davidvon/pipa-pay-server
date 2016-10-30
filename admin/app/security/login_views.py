# -*- coding: utf-8 -*-
__author__ = 'novrain'

from app import app, user_datastore, db
from flask.ext.security import user_registered


@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    try:
        version_role = user_datastore.find_role('ADMIN')
        user_datastore.add_role_to_user(user, version_role)
        db.session.commit()
    except:
        return
