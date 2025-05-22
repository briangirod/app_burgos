from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Consultorio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100)

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
    fecha = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='para_abonar')

    def __str__(self):
        return f"{self.nombre_paciente} - {self.fecha}"

class ProductoUtilizado(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
class PacienteRecepcion(models.Model):
    nombre = models.CharField(max_length=100, default="")
    apellido = models.CharField(max_length=100, default="")
    dni = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    estado = models.CharField(max_length=50, default="En espera")
    doctor_asignado = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

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