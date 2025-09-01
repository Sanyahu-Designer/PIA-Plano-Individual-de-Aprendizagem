from django.urls import path
from . import views

app_name = 'agendamento'

urlpatterns = [
    # Página principal da agenda
    path('calendario/', views.calendario_view, name='calendario'),
    
    # API endpoints para o calendário
    path('api/eventos/', views.eventos_api, name='eventos_api'),
    path('api/criar/', views.criar_agendamento_api, name='criar_api'),
    path('api/editar/<int:agendamento_id>/', views.editar_agendamento_api, name='editar_api'),
    path('api/excluir/<int:agendamento_id>/', views.excluir_agendamento_api, name='excluir_api'),
    
    # Views para busca
    path('api/buscar-pacientes/', views.buscar_pacientes_api, name='buscar_pacientes'),
    path('api/buscar-profissionais/', views.buscar_profissionais_api, name='buscar_profissionais'),
]
