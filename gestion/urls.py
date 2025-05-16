from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Vista inicial (redirige según rol)
    path('doctor/', views.panel_doctor, name='panel_doctor'),
    path('caja/', views.panel_caja, name='panel_caja'),
    path('historial/', views.historial_caja, name='historial'),
    path('doctor/historial/', views.historial_doctor, name='historial_doctor'),
]
