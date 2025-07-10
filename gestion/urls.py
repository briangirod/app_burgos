from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Vista inicial (redirige según rol)
    path('doctor/', views.panel_doctor, name='panel_doctor'),
    path('caja/', views.panel_caja, name='panel_caja'),
    path('historial/', views.historial_caja, name='historial'),
    path('historial/descargar-excel/', views.descargar_historial_excel, name='descargar_historial_excel'),
    path('doctor/historial/', views.historial_doctor, name='historial_doctor'),
    path('caja/panel_ajax/', views.caja_panel_ajax, name='caja_panel_ajax'),
    path('recepcion/', views.panel_recepcion, name='panel_recepcion'),
    path('recepcion/estado/', views.estado_pacientes_ajax, name='estado_pacientes_ajax'),
    path('recepcion/ingresar/', views.ingresar_paciente_ajax, name='ingresar_paciente_ajax'),
    path('recepcion/eliminar/<int:id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='password_change'),
    # URL COMENTADA PARA VERSIÓN FUTURA - Estado del doctor
    # path('doctor/actualizar_estado/', views.actualizar_estado_doctor, name='actualizar_estado_doctor'),



]
