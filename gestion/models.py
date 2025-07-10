from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Sector(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Consultorio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Registro(models.Model):
    ESTADO_CHOICES = [
        ('para_abonar', 'Para Abonar'),
        ('abonado', 'Abonado'),
    ]

    nombre_paciente = models.CharField(max_length=200)
    productos = models.ManyToManyField(Producto, through='ProductoUtilizado')
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now, db_index=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='para_abonar', db_index=True)
    caja_destino = models.ForeignKey(Sector, on_delete=models.CASCADE, verbose_name="Caja Destino", default=1)

    class Meta:
        indexes = [
            models.Index(fields=['caja_destino', 'fecha', 'estado'], name='idx_registro_caja_optimized'),
            models.Index(fields=['doctor', 'fecha'], name='idx_registro_doctor_optimized'),
            models.Index(fields=['-fecha', 'estado'], name='idx_registro_recent'),
        ]
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f"{self.nombre_paciente} - {self.fecha} - {self.caja_destino}"

class ProductoUtilizado(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
class PacienteRecepcion(models.Model):
    nombre = models.CharField(max_length=100, default="")
    apellido = models.CharField(max_length=100, default="")
    dni = models.CharField(max_length=20, blank=True, db_index=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    estado = models.CharField(max_length=50, default="En espera")
    doctor_asignado = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_ingreso = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['-fecha_ingreso', 'estado'], name='idx_paciente_ingreso_estado'),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.estado}"


class EstadoDoctor(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('ausente', 'Ausente'),
        ('con_paciente', 'Con paciente'),
        ('desconectado', 'Desconectado'),
    ]

    doctor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estado_doctor')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='desconectado')

    def __str__(self):
        return f"{self.doctor.username} - {self.get_estado_display()}"

    def estado_display(self):
        return dict(self.ESTADOS).get(self.estado, "Desconocido")

    def estado_clase(self):
        return f"estado-{self.estado}"

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, blank=True)
    apellido = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.sector.nombre}"
    
    def nombre_completo(self):
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        elif self.apellido:
            return self.apellido
        else:
            return self.usuario.username