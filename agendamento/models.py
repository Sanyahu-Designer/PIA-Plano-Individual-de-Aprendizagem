from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_multitenant.mixins import TenantModelMixin
from neurodivergentes.models import Neurodivergente
from profissionais_app.models import Profissional


class Agendamento(TenantModelMixin, models.Model):
    """
    Modelo para agendamentos de profissionais com alunos/pacientes.
    Todos os campos são opcionais para máxima flexibilidade.
    """
    
    tenant_id = models.CharField(max_length=255, default='default')
    
    class TenantMeta:
        tenant_field_name = 'tenant_id'
    
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado'),
        ('faltou', 'Faltou'),
    ]
    
    RECORRENCIA_CHOICES = [
        ('', 'Sem recorrência'),
        ('semanal', 'Semanal'),
        ('quinzenal', 'Quinzenal'),
        ('mensal', 'Mensal'),
    ]
    
    DURACAO_CHOICES = [
        (15, '15 minutos'),
        (30, '30 minutos'),
        (45, '45 minutos'),
        (60, '1 hora'),
        (90, '1h30'),
        (120, '2 horas'),
        (480, 'Dia inteiro'),
        (0, 'Personalizado'),
    ]
    
    # Campos obrigatórios
    profissional = models.ForeignKey(
        Profissional, 
        on_delete=models.CASCADE,
        verbose_name="Profissional"
    )
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )
    
    # Campos opcionais
    neurodivergente = models.ForeignKey(
        Neurodivergente, 
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
        verbose_name="Paciente/Aluno"
    )
    data_hora_inicio = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Data e Hora"
    )
    duracao_minutos = models.IntegerField(
        choices=DURACAO_CHOICES,
        default=45, 
        blank=True, 
        null=True,
        verbose_name="Duração"
    )
    duracao_personalizada = models.IntegerField(
        blank=True, 
        null=True,
        verbose_name="Duração personalizada (minutos)",
        help_text="Usado quando duração = 'Personalizado'"
    )
    descricao = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Descrição curta"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default='agendado',
        blank=True,
        verbose_name="Status"
    )
    recorrencia = models.CharField(
        max_length=20,
        choices=RECORRENCIA_CHOICES, 
        blank=True,
        verbose_name="Recorrência"
    )
    enviar_copia_gestor = models.BooleanField(
        default=False,
        verbose_name="Enviar cópia ao gestor"
    )
    
    # Campos de controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-data_hora_inicio', '-criado_em']
        permissions = [
            ('can_manage_all_schedules', 'Pode gerenciar agendas de todos os profissionais'),
        ]
    
    def __str__(self):
        if self.neurodivergente and self.data_hora_inicio:
            return f"{self.profissional.user.get_full_name()} - {self.neurodivergente.nome_completo} - {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
        elif self.neurodivergente:
            return f"{self.profissional.user.get_full_name()} - {self.neurodivergente.nome_completo}"
        elif self.data_hora_inicio:
            return f"{self.profissional.user.get_full_name()} - {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
        else:
            return f"{self.profissional.user.get_full_name()} - {self.descricao or 'Agendamento'}"
    
    @property
    def duracao_real(self):
        """Retorna a duração real em minutos"""
        if self.duracao_minutos == 0:  # Personalizado
            return self.duracao_personalizada or 45
        return self.duracao_minutos or 45
    
    @property
    def data_hora_fim(self):
        """Calcula a data/hora de fim baseada na duração"""
        if self.data_hora_inicio:
            from datetime import timedelta
            return self.data_hora_inicio + timedelta(minutes=self.duracao_real)
        return None
    
    def get_cor_status(self):
        """Retorna a cor para o status no calendário"""
        cores = {
            'agendado': '#1A73E8',      # Azul
            'confirmado': '#4CAF50',    # Verde
            'realizado': '#2E7D32',     # Verde escuro
            'cancelado': '#f44335',     # Vermelho
            'faltou': '#FF9800',        # Laranja
        }
        return cores.get(self.status, '#1A73E8')
