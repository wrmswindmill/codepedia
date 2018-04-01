from django import forms
from .models import User
# from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)

class RegisterForm(forms.Form):  # 注册
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    # captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})
