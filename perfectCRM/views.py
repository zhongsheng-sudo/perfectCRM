#_author: hasee
#date: 2019/9/7
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
def acc_login(request):
    errors=[]
    if request.method=='POST':
        _email=request.POST.get('email')
        _password = request.POST.get('password')
        user=authenticate(username=_email,password=_password)
        if user:
            next_url=request.GET.get('next','/')
            return redirect(next_url)
        else:
            errors['error']='Wrong username or password!'

    return render(request,'login.html',{'errors':errors})

def acc_logout(request):
    return redirect('/account/login/')

def index(request):
    return render(request,'index.html')