#!flask/bin/python

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'site-packages'))

from app import app as application, logger

from wexin.views import weixin_module
application.register_blueprint(weixin_module, url_prefix='/weixin')
logger.info('initial done')

if __name__ == '__main__':
    application.run(debug=True, threaded=True)
