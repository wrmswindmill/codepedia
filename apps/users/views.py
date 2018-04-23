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


from .models import User, EmailVerifyRecord
from .forms import LoginForm,RegisterForm
import utils.scanner_project as scanner


# Create your views here.
class CustomBackend(ModelBackend): #通过邮箱登陆
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
                    return render(request, 'users/login.html', {'msg': '用户未激活!请到邮箱激活后,再登录'})
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

            from .tasks import send_type_email
            send_type_email(user_name,'register')
            # send_type_email.delay(user_name, 'register')
            
            return render(request, 'users/login.html')
        else:
            return render(request, 'users/register.html', {'register_form': register_form})

#用户激活
class ActiveView(View):
    def get(self, request, active_code):
        print(1111)
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'shared/active_fail.html')
        return render(request, 'users/login.html')


class UserInfoView(View):
    """
    用户个人信息
    """

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        return render(request, 'users/user_info.html', {'user': user})

    # def post(self, request):
    #     user_info_form = UserInfoForm(request.POST, instance=request.user)
    #     if user_info_form.is_valid():
    #         user_info_form.save()
    #         return HttpResponse('{"status":"success"}', content_type='application/json')
    #     else:
    #         return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


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
        scanner.get_anno_issue_summary("/opt/opengrok/source/Notes",1)
        return render(request, 'index.html', {})


class LogoutView(View):
    """
    用户注销
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))
