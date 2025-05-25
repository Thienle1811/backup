# ---------------------------------------------------------------------------
# 1️⃣  apps/labtests/urls.py
# ---------------------------------------------------------------------------

from django.urls import path
from . import views

app_name = "labtests"
urlpatterns = [
    # List
    path("", views.labtest_list, name="list"),
    
    # Agent flow
    path("create/", views.select_patient, name="select_patient"),
    path("create/<int:patient_id>/", views.select_category, name="select_category"),
    path("create/<int:patient_id>/<int:category_id>/", views.fill_values, name="fill_values"),

    # Detail & Update
    path("<int:pk>/", views.labtest_detail, name="detail"),
    path("<int:pk>/update/", views.labtest_update, name="update"),
    path("<int:pk>/export-word/", views.export_labtest_word, name="export_word"),
]