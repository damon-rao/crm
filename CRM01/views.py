from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# Create your views here.



errors={}
def login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=auth.authenticate(username=username,password=password)

        if user:
            auth.login(request, user)
            next_url=request.GET.get('next','/index')#获取要跳到的下个页面
            return redirect(next_url)
        else:
            errors['error']='账号或密码错误'


    return render(request, 'login.html', {'errors':errors})

def logout(request):
    auth.logout(request)
    return redirect('/login')

def index(request):
    return render(request,'index.html')