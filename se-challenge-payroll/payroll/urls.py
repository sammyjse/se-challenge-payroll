from django.urls import path, include, re_path
from django.contrib import admin
from django.urls import path
from app.views import UploadCSVView, TimekeepingView, EmployeeReportsView, ReportsView
from rest_framework import routers

router = routers.DefaultRouter()

# setting up the basic api for timekeeping and reports models
router.register(r'timekeeping', TimekeepingView, 'timekeeping')
router.register(r'reports', ReportsView, 'reports')

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('upload/', UploadCSVView.as_view(), name='upload'),
    path('employee-reports/', EmployeeReportsView.as_view(), name='employee-reports'),
    path('api/', include(router.urls)),
]
