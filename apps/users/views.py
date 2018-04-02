from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend #通过邮箱登陆
from django.db.models import Q
from django.views import View
from django.contrib.auth.hashers import make_password #把明文密码加密
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json
import requests


from .models import User
from .forms import LoginForm,RegisterForm


# Create your views here.
class CustomBackend(ModelBackend):  #通过邮箱登陆
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'users/login.html', {'msg': '用户未激活!'})
            else:
                return render(request, 'users/login.html', {'msg': '用户名或密码错误!'})
        else:
            return render(request, 'users/login.html', {'login_form': login_form})


class RegisterView(View):

    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'users/register.html', locals())

    def post(self, request):
        register_form = RegisterForm(request.POST)       
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if User.objects.filter(email=user_name):
                return render(request, 'users/register.html', {
                    'register_form': register_form,
                    'msg': '用户已经存在'
                })

            pwd1 = request.POST.get('password', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return render(request, 'users/register.html', {
                    'register_form': register_form,
                    'msg': '密码不一样'
                })

            user = User()
            user.username = user_name
            user.email = user_name
            user.is_active = False
            user.password = make_password(pwd1)
            user.save()
            
            # send_type_email.delay(user_name, 'register')
            return render(request, 'users/login.html')
        else:
            return render(request, 'users/register.html', {'register_form': register_form})


# 用户登录
# class LoginView(View):
#     def get(self, request):
#         return render(request, 'users/login.html', {})
#
#     def post(self, request):
#         login_form = LoginForm(request.POST)
#         if login_form.is_valid():
#             user_name = request.POST.get('username', '')
#             pass_word = request.POST.get('password', '')
#             user_params = {'username':user_name,'password':pass_word}
#             trustie_url = 'https://www.trustie.net/account/codepedia_login'
#             response = requests.get(trustie_url, params=user_params)
#             response = json.loads(response.text)
#             status = response['status']
#             if status == 1:
#                 user_message = response['user']['user']
#                 email = user_message['mail']
#                 exist_records = User.objects.filter(email=email).first()
#                 if not exist_records:
#                     user = User()
#                     user.username = user_name
#                     user.password = make_password(pass_word)
#                     user.email = email
#                     if 'lastname' in user_message:
#                         user.nick_name = user_message['lastname']
#                     elif 'nickname' in user_message:
#                         user.nick_name = user_message['nickname']
#                     else:
#                         user.nick_name = user_message['firstname']
#                     user.is_active = True
#                     user.save()
#                 user = authenticate(username=user_name, password=pass_word)
#                 if user is not None:
#                     login(request, user)
#                     return HttpResponseRedirect(reverse('index'))
#             else:
#                 return render(request, 'users/login.html', {'msg': '用户名或密码错误!'})
#         else:
#             return render(request, 'users/login.html', {'login_form': login_form})

class IndexView(View):
    def get(self,request):

        return render(request, 'index.html', {

        })


class LogoutView(View):
    """
    用户注销
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))
