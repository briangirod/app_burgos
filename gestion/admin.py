from django.contrib import admin
from .models import Producto, Tratamiento, Consultorio, Registro, ProductoUtilizado

admin.site.register(Producto)
admin.site.register(Tratamiento)
admin.site.register(Consultorio)
admin.site.register(Registro)
admin.site.register(ProductoUtilizado)
