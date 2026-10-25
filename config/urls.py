##	============ ##
##		ROUTES	 ##
##	============ ##

# Las rutas visibles (/libros/, /prestamos/...) no cambian: solo los nombres internos.

#	=== IMPORTS ===	#
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from usuarios.Prologue import Cerberus_Gate

from . import Draculas_Castle


#	=== PATHS ===	#
urlpatterns = [
    path('healthz/', Draculas_Castle.Lisa_Tepes, name='Lisa_Tepes'),

    path('admin/', admin.site.urls),

    path('login/', Cerberus_Gate.as_view(), name='Cerberus_Gate'),
    path('logout/', auth_views.LogoutView.as_view(next_page='Cerberus_Gate'), name='Leave_The_Castle'),

    path('', Draculas_Castle.Greta, name='Greta'),

    path('academico/', include('alumnos_maestros.urls')),
    path('calificaciones/', include('calificaciones.urls')),
    path('horarios/', include('horarios.urls')),
    path('empresas/', include('empresas.urls')),
    path('billetera/', include('billetera.urls')),

    #	=== LIBRARY ===	#
    path('usuarios/', include('usuarios.urls')),
    path('libros/', include('libros.urls')),
    path('prestamos/', include('prestamos.urls')),
]
