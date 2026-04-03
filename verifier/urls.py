from django.urls import path
from . import views

# 🛑 SWAGGER IMPORTS 🛑
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 🛑 SWAGGER SETUP 🛑
schema_view = get_schema_view(
   openapi.Info(
      title="University Smart Gateway API",
      default_version='v1',
      description="APIs for Distributed Cloud Facial Recognition System",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register'),
    path('verify-qr/', views.verify_qr, name='verify_qr'),
    path('verify/', views.verify_face, name='verify'),
    path('verify-fingerprint/', views.verify_fingerprint, name='ver_fp'),
    path('login/', views.login_student, name='login'), # Login ke liye
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'), # Dashboard ka URL
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    path('approve/<int:entity_id>/', views.approve_entity, name='approve_entity'), # Approve action
    path('reject/<int:entity_id>/', views.reject_entity, name='reject_entity'),
    # urls.py mein urlpatterns list ke andar yeh 3 lines add karein:
    path('api/update-location/', views.update_location, name='update_location'),
    path('api/get-location/', views.get_location, name='get_location'),
    path('track-bus/', views.track_bus_page, name='track_bus'),
    # 🚀 NAYE ENTERPRISE URLs 🚀
    path('regenerate-qrs/', views.regenerate_all_qrs, name='regenerate_qrs'), # Purane QR codes update karne ka VIP tool
    path('verify-id/', views.verify_id, name='verify_id'), # Manual ID / Roll No verify karne ke liye
    path('rename-photos/', views.rename_old_photos, name='rename_old_photos'),
    path('fast-live-attendance/', views.fast_live_attendance, name='fast_live_attendance'),
    
    # 🛑 SWAGGER URL 🛑
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]