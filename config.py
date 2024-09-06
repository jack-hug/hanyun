import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    HY_ADMIN_EMAIL = os.getenv('HY_ADMIN', 'karen@hanyunmold.com')
    HY_PRODUCT_PER_PAGE = 12
    HY_PHOTO_PER_PAGE = 12
    HY_MESSAGE_PER_PAGE = 15
    HY_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    if not os.path.exists(HY_UPLOAD_PATH):
        os.mkdir(HY_UPLOAD_PATH)

    SECRET_KEY = os.getenv('SECRET_KEY', 'hanyunmoldandhaiyananduppmold@1234565987556')
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    MAIL_SERVER = os.getenv('MAIL_SERVER' or 'smtphz.qiye.163.com')
    MAIL_USER_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME' or 'karen@hanyunmold.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD' or '!k-#s7U976KaAxB')
    MAIL_DEFAULT_SENDER = ('Hanyun Admin', MAIL_USERNAME or 'karen@hanyunmold.com')


    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_PKG_TYPE = 'standard'
    CKEDITOR_HEIGHT = 200
    CKEDITOR_FILE_UPLOADER = 'upload'  # ckeditor上传图片的函数

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
class DevelopmentConfig(BaseConfig):
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'


class ProductionConfig(BaseConfig):
    WTF_CSRF_ENABLED = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
