"""
Django settings for Codepedia2 project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import sys
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-v3mo%rerbbh%7xez9^jg^htsn53e4v-)ij-xa5c7gku%8o%p)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
COMPRESS_ENABLED = True
ALLOWED_HOSTS = []

AUTH_USER_MODEL= 'users.User'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自己开发的app
    'users',
    'projects',
    'actions',
    'operations',
    # xadmin
    'xadmin',
    'crispy_forms',
    'reversion',
    # 静态文件压缩插件
    "compressor",
    # 第三方登陆
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 验证码
    'captcha',
    # 微信登陆
    'allauth.socialaccount.providers.weixin',
    # 微博登陆
    'allauth.socialaccount.providers.weibo',
    # github登陆
    'allauth.socialaccount.providers.github',
    # debug_toolbar
    'debug_toolbar',
    # 扩展插件
    'django_extensions',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'Codepedia2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # allauth
                'django.template.context_processors.request',

            ],
        },
    },

]

WSGI_APPLICATION = 'Codepedia2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codepedia',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': '127.0.0.1'
    }
}

AUTHENTICATION_BACKENDS = (

    # django admin所使用的用户登录与django-allauth无关
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

)



SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 数据库存储使用时间，True时间会被存为UTC的时间
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),

]
STATIC_ROOT="/Users/yujie/Downloads/static/"


# 处理静态压缩文件
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'compressor.finders.CompressorFinder',
)

# 配置邮件发送
EMAIL_HOST = 'smtp.yeah.net'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'alexkie@yeah.net'
EMAIL_HOST_PASSWORD = 'Mr8023Mr'
EMAIL_USE_TLS = False
EMAIL_FROM = 'alexkie@yeah.net'


# 设置我们上传文件的路径

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = ('127.0.0.1', )


# 工程路径
SOURCEPATH = '/opt/opengrok/source/'

# OpenGrok
OPENGROK_BASE = 'http://localhost:8080/myopengrok/'
OPENGROK_XREF_URL = OPENGROK_BASE+'myxref/'
OPENGROK_NAVIGATION_URL = OPENGROK_BASE+'navigation/'
OPENGROK_SEARCH_URL = OPENGROK_BASE+'mysearch?'

# # logging日志配置
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {  # 日志格式
#         'standard': {
#             'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
#     },
#     'filters': {  # 过滤器
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         }
#     },
#     'handlers': {  # 处理器
#         'null': {
#             'level': 'DEBUG',
#             'class': 'logging.NullHandler',
#         },
#         'mail_admins': {  # 发送邮件通知管理员
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['require_debug_false'],  # 仅当 DEBUG = False 时才发送邮件
#             'include_html': True,
#         },
#         'debug': {  # 记录到日志文件(需要创建对应的目录，否则会出错)
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(BASE_DIR, "log", 'debug.log'),  # 日志输出文件
#             'maxBytes': 1024 * 1024 * 5,  # 文件大小
#             'backupCount': 5,  # 备份份数
#             'formatter': 'standard',  # 使用哪种formatters日志格式
#         },
#         'console': {  # 输出到控制台
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#         },
#     },
#     'loggers': {  # logging管理器
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False
#         },
#         'django.request': {
#             'handlers': ['debug', 'mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         # 对于不在 ALLOWED_HOSTS 中的请求不发送报错邮件
#         'django.security.DisallowedHost': {
#             'handlers': ['null'],
#             'propagate': False,
#         },
#     }
# }
