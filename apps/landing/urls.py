from django.urls import path
from . import views

app_name = "landing"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("news/", views.news, name="news"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_redirect, name="login"),
] 