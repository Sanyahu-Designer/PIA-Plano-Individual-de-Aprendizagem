from django.contrib import admin
from django.utils.html import format_html
from .models import Agendamento


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = [
        'get_profissional', 'get_paciente', 'data_hora_inicio', 
        'duracao_real', 'get_status_badge', 'criado_em'
    ]
    list_filter = ['status', 'profissional', 'data_hora_inicio', 'criado_em']
    search_fields = [
        'profissional__user__first_name', 'profissional__user__last_name',
        'neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome', 'descricao', 'observacoes'
    ]
    autocomplete_fields = ['neurodivergente', 'profissional']
    date_hierarchy = 'data_hora_inicio'
    ordering = ['-data_hora_inicio', '-criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('profissional', 'neurodivergente', 'status')
        }),
        ('Data e Duração', {
            'fields': ('data_hora_inicio', 'duracao_minutos', 'duracao_personalizada')
        }),
        ('Descrição', {
            'fields': ('descricao', 'observacoes')
        }),
        ('Configurações', {
            'fields': ('recorrencia', 'enviar_copia_gestor')
        }),
        ('Controle', {
            'fields': ('criado_por',),
            'classes': ('collapse',)
        })
    )
    
    def get_profissional(self, obj):
        return obj.profissional.user.get_full_name() or obj.profissional.user.username
    get_profissional.short_description = 'Profissional'
    
    def get_paciente(self, obj):
        if obj.neurodivergente:
            return obj.neurodivergente.nome_completo
        return '-'
    get_paciente.short_description = 'Paciente/Aluno'
    
    def get_status_badge(self, obj):
        cores = {
            'agendado': '#1A73E8',
            'confirmado': '#4CAF50',
            'realizado': '#2E7D32',
            'cancelado': '#f44335',
            'faltou': '#FF9800',
        }
        cor = cores.get(obj.status, '#1A73E8')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            cor, obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
