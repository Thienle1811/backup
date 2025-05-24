from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

def home(request):
    return render(request, "landing/home.html")

def about(request):
    return render(request, "landing/about.html")

def services(request):
    return render(request, "landing/services.html")

def news(request):
    return render(request, "landing/news.html")

def contact(request):
    return render(request, "landing/contact.html")

def login_redirect(request):
    return redirect(reverse("accounts:login"))
