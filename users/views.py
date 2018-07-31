from django.shortcuts import render, redirect
from users.forms import RegisterForm
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.


def register(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', context={'form': form, 'redirect_to': redirect_to})


def index(request):
    return render(request, 'index.html')


def password_change(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            form.save()
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        form = PasswordChangeForm(request.POST.get('username'))
    return render(request, 'registration/password_change_form.html', context={'form': form, 'redirect_to': redirect_to})
