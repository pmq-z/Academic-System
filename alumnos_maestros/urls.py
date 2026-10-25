##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Vampire_Killer as Vk


#	=== PATHS ===	#
urlpatterns = [
    path('', Vk.Circle_Of_The_Moon, name='Circle_Of_The_Moon'),

    path('alumnos/', Vk.Nathan_And_Hugh, name='Nathan_And_Hugh'),
    path('alumnos/nuevo/', Vk.Morris_Takes_An_Apprentice, name='Morris_Takes_An_Apprentice'),
    path('alumnos/<int:pk>/editar/', Vk.Nathan_Levels_Up, name='Nathan_Levels_Up'),
    path('alumnos/<int:pk>/desactivar/', Vk.Hugh_Goes_His_Own_Way, name='Hugh_Goes_His_Own_Way'),

    path('maestros/', Vk.Morris_Baldwin, name='Morris_Baldwin'),
    path('maestros/nuevo/', Vk.Morris_Recruits, name='Morris_Recruits'),
    path('maestros/<int:pk>/editar/', Vk.Morris_Revises, name='Morris_Revises'),
    path('maestros/<int:pk>/desactivar/', Vk.Julius_Retires, name='Julius_Retires'),

    path('materias/', Vk.Charlotte_Spellbook, name='Charlotte_Spellbook'),
    path('materias/nueva/', Vk.Charlotte_Learns_A_Spell, name='Charlotte_Learns_A_Spell'),
    path('materias/<int:pk>/editar/', Vk.Charlotte_Rewrites_A_Spell, name='Charlotte_Rewrites_A_Spell'),
    path('materias/<int:pk>/desactivar/', Vk.Charlotte_Seals_A_Spell, name='Charlotte_Seals_A_Spell'),

    path('inscripciones/', Vk.Order_Of_Ecclesia, name='Order_Of_Ecclesia'),
    path('inscripciones/nueva/', Vk.Join_The_Order, name='Join_The_Order'),
    path('inscripciones/<int:pk>/desactivar/', Vk.Leave_The_Order, name='Leave_The_Order'),
]
