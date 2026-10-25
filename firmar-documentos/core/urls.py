from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('documentos/', views.documentos, name='documentos'),
    path('usuario/', views.usuario, name='usuario'),
    path('firma/', views.firma, name='firma'),
    path('logout/', views.logout_view, name='logout'),
]