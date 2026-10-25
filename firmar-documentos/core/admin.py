from django.contrib import admin
from .models import Documento, Firma

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'usuario', 'estado', 'fecha_creacion')
    search_fields = ('titulo', 'usuario__username')
    list_filter = ('estado', 'fecha_creacion')


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'documento', 'usuario', 'fecha_firma')
    search_fields = ('documento__titulo', 'usuario__username')
    list_filter = ('fecha_firma',)