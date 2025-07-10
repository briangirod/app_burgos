from django.contrib import admin
from .models import Producto, Tratamiento, Consultorio, Registro, ProductoUtilizado, Sector, PerfilUsuario

admin.site.register(Producto)
admin.site.register(Tratamiento)
admin.site.register(Consultorio)
admin.site.register(Registro)
admin.site.register(ProductoUtilizado)
admin.site.register(Sector)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'sector']
    list_filter = ['sector']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name']
