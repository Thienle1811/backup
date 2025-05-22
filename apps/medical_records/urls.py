from django.urls import path
from . import views

app_name = "medical_records"
urlpatterns = [
    path("", views.record_list, name="list"),
    path("create/", views.select_patient, name="select_patient"),
    path("create/<int:patient_id>/", views.record_create, name="create"),
    path("<int:pk>/", views.record_detail, name="detail"),
    path("<int:pk>/edit/", views.record_edit, name="edit"),
    path("<int:pk>/attach-labtests/", views.attach_labtests, name="attach_labtests"),
    path(
        "<int:pk>/detach-labtest/<int:labtest_id>/",
        views.detach_labtest,
        name="detach_labtest",
    ),
    path("<int:pk>/word/", views.record_word, name="record_word"),
]
