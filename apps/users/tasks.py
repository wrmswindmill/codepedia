from .models import EmailVerifyRecord
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
# from CodePedia2.celery import app

def random_str(randomlength=0):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars)-1

    from random import Random
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


# @shared_task
def send_type_email(email,send_type='register'):
    email_record = EmailVerifyRecord()
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)

    #保存邮件信息
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
   
    if send_type == 'register':
        email_title = 'CodePedia注册激活链接'
        url = '请点击下面的链接激活你的账号:'+settings.DOMAIN_URL+'/users/active/{0}'
        email_body = url.format(code)
        print(email_body)
        send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
    elif send_type == 'forget':
        email_title = 'CodePedia密码重置链接'
        url = '请点击下面的链接激活你的账号:'+settings.DOMAIN_URL+'/users/reset/{0}'
        email_body = url.format(code)       
        send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
    elif send_type == 'update_email':
        email_title = 'CodePedia邮箱修改链接'
        email_body = '你的邮箱验证码为{0}'.format(code)
        send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
