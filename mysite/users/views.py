from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth.hashers import make_password
# Create your views here.
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm
from .models import EmailVerifyRecord, UserProfile
from utils.email_send import send_register_email
from django.contrib.auth.decorators import login_required

class MyBackend(ModelBackend):
    """邮箱登录注册"""
    def authenticate(self, request, username=None, password=None,):
        try:
            user = User.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):   # 加密明文密码
                return user
        except Exception as e:
            return None

def active_user(request, active_code):
    """修改用户状态，比对验证码"""
    all_records = EmailVerifyRecord.objects.filter(code= active_code)
    if all_records:
        for record in all_records:
            email = record.email
            user = User.objects.get(email=email)
            user.is_staff = True
            user.save

    else:
        return HttpResponse('链接有误')
    return redirect('users:login')



def login_view(request):

    if request.method != 'POST':
        form = LoginForm()
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # 登陆成功跳转到指定页面(个人中心)
                return redirect('users:user_profile')
            else:
                # 验证不通过提示！
                return HttpResponse("账号或者密码错误！")


    #print(username, password)   #验证前端的表单数据，能不能传到后端

    context = {'form':form} #上下文
    return render(request, 'users/login.html', context)


def register(request):
    """注册视图"""
    if request.method != 'POST':
        form = RegisterForm()
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data.get('password'))
            new_user.username = form.cleaned_data.get('email')
            new_user.save()

            #发送邮件
            send_register_email(form.cleaned_data.get('email'),'register')
            
            return HttpResponse('注册成功')

    context = {'form':form}

    return render(request, 'users/register.html', context)


def forget_pwd(request):
    """ 找回密码 """
    if request.method == 'GET':
        form = ForgetPwdForm()
    elif request.method == 'POST':
        form = ForgetPwdForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            exists = User.objects.filter(email=email).exists()
            if exists:
                # 发送邮件
                send_register_email(email, 'forget')
                return HttpResponse('邮件已经发送请查收！')
            else:
                return HttpResponse('邮箱还未注册，请前往注册！')

    return render(request, 'users/forget_pwd.html', {'form': form})


def forget_pwd_url(request, active_code):
    if request.method != 'POST':
        form = ModifyPwdForm()
    else:
        form = ModifyPwdForm(request.POST)
        if form.is_valid():
            record = EmailVerifyRecord.objects.get(code=active_code)
            email = record.email
            user = User.objects.get(email=email)
            user.username = email
            user.password = make_password(form.cleaned_data.get('password')) # 转成哈希值
            user.save()
            return HttpResponse('修改成功')
        else:
            return HttpResponse('修改失败')

    return render(request, 'users/reset_pwd.html', {'form': form})


@login_required(login_url='users:login')
def user_profile(request):
    user = User.objects.get(username=request.user)
    return render(request, 'users/user_profile.html', {'user':user})
