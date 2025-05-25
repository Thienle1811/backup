"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.db import connection
import os

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
    except Exception as e:
        db_status = f"Error: {str(e)}"

    # Check environment
    env = os.environ.get('DJANGO_ENV', 'Not set')
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')

    return JsonResponse({
        "status": "OK",
        "database": db_status,
        "environment": env,
        "settings_module": settings_module
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("patients/", include("apps.patients.urls")),
    path("medical-records/", include("apps.medical_records.urls")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("labtests/", include("apps.labtests.urls")),
    path("reports/", include("apps.reports.urls", namespace="reports")), 
    path("", include("apps.landing.urls", namespace="landing")),
    path("health/", health_check, name="health_check"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
