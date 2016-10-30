# -*- coding: utf-8 -*-

# Flask-security
from app import app

security_config = {
    'LOGIN_MESSAGE': None,
    'SECURITY_PASSWORD_HASH': 'pbkdf2_sha256',
    'SECURITY_PASSWORD_SALT': 'so-salty',
    'SECURITY_EMAIL_SENDER': 'ztecore@163.com',
    'SECURITY_CHANGEABLE': True,
    'SECURITY_RECOVERABLE': True,
    'SECURITY_REGISTERABLE': True,
    'SECURITY_FLASH_MESSAGES': True,
    'SECURITY_EMAIL_SUBJECT_PASSWORD_RESET':'密码重设介绍',
    'SECURITY_SEND_REGISTER_EMAIL': False,
    'SECURITY_SEND_PASSWORD_CHANGE_EMAIL': False,
    'SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL': False,
}


i18n_messages = {
    'UNAUTHORIZED': ('没有权限访问此页面.', 'error'),
    'CONFIRM_REGISTRATION': ('谢谢，认证邮件已发送至 %(email)s.', 'success'),
    'EMAIL_CONFIRMED': ('非常感谢. 您的邮箱认证通过.', 'success'),
    'ALREADY_CONFIRMED': ('您的邮箱已获得认证.', 'info'),
    'INVALID_CONFIRMATION_TOKEN': ('邮箱认证令牌已失效.', 'error'),
    'EMAIL_ALREADY_ASSOCIATED': ('%(email)s 邮箱已注册', 'error'),
    'PASSWORD_MISMATCH': ('密码不匹配', 'error'),
    'RETYPE_PASSWORD_MISMATCH': ('重新输入的密码不匹配', 'error'),
    'INVALID_REDIRECT': ('Redirections outside the domain are forbidden', 'error'),
    'PASSWORD_RESET_REQUEST': ('重置密码邮件已发送', 'info'),
    'PASSWORD_RESET_EXPIRED': (
        'You did not reset your password within %(within)s. New instructions have been sent to %(email)s.', 'error'),
    'INVALID_RESET_PASSWORD_TOKEN': ('Invalid reset password token.', 'error'),
    'CONFIRMATION_REQUIRED': ('帐号未激活，请登录邮箱激活帐号', 'error'),
    'CONFIRMATION_REQUEST': ('Confirmation instructions have been sent to %(email)s.', 'info'),
    'CONFIRMATION_EXPIRED': (
        'You did not confirm your email within %(within)s. New instructions to confirm your email have been sent to %(email)s.',
        'error'),
    'LOGIN_EXPIRED': (
        'You did not login within %(within)s. New instructions to login have been sent to %(email)s.', 'error'),
    'LOGIN_EMAIL_SENT': ('Instructions to login have been sent to %(email)s.', 'success'),
    'INVALID_LOGIN_TOKEN': ('非法登录令牌.', 'error'),
    'DISABLED_ACCOUNT': ('帐户未激活.', 'error'),
    'EMAIL_NOT_PROVIDED': ('邮箱没有输入', 'error'),
    'INVALID_EMAIL_ADDRESS': ('邮箱地址非法', 'error'),
    'PASSWORD_NOT_PROVIDED': ('密码没有输入', 'error'),
    'PASSWORD_INVALID_LENGTH': ('密码必须至少6位字符', 'error'),
    'USER_DOES_NOT_EXIST': ('指定的用户不存在', 'error'),
    'INVALID_PASSWORD': ('密码不正确', 'error'),
    'PASSWORDLESS_LOGIN_SUCCESSFUL': ('登录成功.', 'success'),
    'PASSWORD_RESET': ('密码已重设，并自动登录.', 'success'),
    'PASSWORD_CHANGE': ('密码修改已成功.', 'success'),
    'LOGIN': ('请输入用户名和密码.', 'info'),
    'REFRESH': ('请重新登录来访问此页面.', 'info'),
    'NICKNAME_NOT_PROVIDED': ('请输入用户名.', 'error'),
    'NICKNAME_INVALID_LENGTH': ('用户名5~25个字符.', 'error'),
}


for key, value in i18n_messages.items():
    app.config.__setitem__('SECURITY_MSG_' + key, value)

for key, value in security_config.items():
    app.config.__setitem__(key, value)
