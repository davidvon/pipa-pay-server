#encoding=utf-8
from qiniu import conf, rsf, io, rs

ACCESS_KEY = '_t2VNt_Z765EiBWXkeSTjZoTwtG-ybvllh8Xe-Q7'
SECRET_KEY = '1-2EFiCilWs-M6SRC_s30exHkg60V2vvu0B7HvX8'
BUCKET_KEY = 'laundry'
BUCKET_HOST = 'http://7xjzhm.com1.z0.glb.clouddn.com/'
IMG_SHOW_PARAM = '?imageView2/1/w/900/h/500/q/60'


class QiniuStorage(object):

    def __init__(self, access_key=ACCESS_KEY, secret_key=SECRET_KEY):
        self.access_key = access_key
        self.secret_key = secret_key
        conf.ACCESS_KEY = access_key
        conf.SECRET_KEY = secret_key

    def put_file(self, name, content):
        bucket = BUCKET_KEY
        policy = rs.PutPolicy(bucket)
        token = policy.token()
        ret, err = io.put(token, name, content)
        if err is not None:
            raise IOError("QiniuStorageError: %s", err)
        return self.img_url(name)

    def remove_file(self, name):
        if self._exists(name):
            self._delete(name)

    @staticmethod
    def img_list():
        bucket = BUCKET_KEY
        ret, err = rsf.Client().list_prefix(bucket, prefix=None, limit=None, marker=None)
        if err and err != 'EOF':
            raise IOError("QiniuStorageError: %s", err)
        return ret

    def img_url(self, img_name):
        return BUCKET_HOST + img_name + IMG_SHOW_PARAM

    def _delete(self, name):
        bucket = BUCKET_KEY
        ret, err = rs.Client().delete(bucket, name)
        if err:
            raise IOError('QiniuStorageError %s', err)
        return ret

    def _exists(self, name):
        bucket = BUCKET_KEY
        ret, err = rs.Client().stat(bucket, name)
        return ret is not None

