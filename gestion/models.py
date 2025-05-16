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
