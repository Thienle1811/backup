from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# import your custom form
from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    # use LoginForm instead of AuthenticationForm
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard:home")
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu!")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")
