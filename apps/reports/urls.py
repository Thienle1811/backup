from django.urls import path
from . import views

app_name = "reports"  # this line defines the namespace
urlpatterns = [
    path("record/<int:pk>/pdf/", views.record_pdf, name="record_pdf"),
]
