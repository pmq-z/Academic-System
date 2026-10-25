from django.db import models
from django.contrib.auth.models import User

class Documento(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('firmado', 'Firmado'),
        ('rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=150)
    archivo = models.FileField(upload_to='documentos/', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Firma(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_firma = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Firma de {self.usuario.username} - {self.documento.titulo}"