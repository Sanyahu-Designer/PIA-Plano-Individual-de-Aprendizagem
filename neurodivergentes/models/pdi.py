from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Neurodivergente
from profissionais_app.models import Profissional

class PDI(models.Model):
    STATUS_CHOICES = [
        ('ausente', 'Ausente'),  # NOVO STATUS PRIMEIRA OPÇÃO
        ('iniciado', 'Iniciado'),
        ('em_andamento', 'Em Planejamento'),
        ('concluido', 'Concluído'),
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado')
    ]

    neurodivergente = models.ForeignKey(
    Neurodivergente,
    on_delete=models.CASCADE,
    related_name='pdis',
    verbose_name='Aluno/Paciente'
)

    data_criacao = models.DateField('Data do PDI')
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='iniciado'
    )
    pedagogo_responsavel = models.ForeignKey(
        Profissional,
        on_delete=models.PROTECT,
        related_name='pdis_responsavel',
        verbose_name='Pedagogo Responsável',
        limit_choices_to={'profissao__in': ['educador_especial', 'pedagogo', 'psicopedagogo', 'neuropsicopedagogo']}
    )
    observacoes = models.TextField(
        'Diário de Classe',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'PDI'
        verbose_name_plural = 'PDIs'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"PDI de {self.neurodivergente} - {self.data_criacao}"

    def clean(self):
        if self.status == 'concluido':
            # Impede salvar como concluído na primeira vez
            if not self.pk:
                raise ValidationError({
                    'status': 'Não é possível salvar como "Concluído". Sugiro usar "Iniciado" ou "Em Andamento".'
                })

class PlanoEducacional(models.Model):
    pdi = models.OneToOneField(
        PDI,
        on_delete=models.CASCADE,
        related_name='plano_educacional',
        verbose_name='PDI'
    )
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Finalização')
    pedagogo_responsavel = models.ForeignKey(
        Profissional,
        on_delete=models.PROTECT,
        related_name='planos_educacionais',
        limit_choices_to={'profissao__startswith': 'pedagogo'}
    )
    objetivos = models.TextField('Objetivos')
    estrategias = models.TextField('Estratégias')
    recursos = models.TextField('Recursos Necessários')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ACI'
        verbose_name_plural = 'ACIs'

    def __str__(self):
        return f"ACI de {self.pdi.neurodivergente}"

    def clean(self):
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': 'A data de finalização não pode ser anterior à data de início.'
            })

class AdaptacaoCurricular(models.Model):
    plano_educacional = models.ForeignKey(
        PlanoEducacional,
        on_delete=models.CASCADE,
        related_name='adaptacoes'
    )
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Finalização')
    professor_responsavel = models.ForeignKey(
        Profissional,
        on_delete=models.PROTECT,
        related_name='adaptacoes_curriculares',
        limit_choices_to={'profissao__startswith': 'educador_especial'}
    )
    componente_curricular = models.CharField('Componente Curricular', max_length=100)
    conteudo_adaptado = models.TextField('Conteúdo Adaptado')
    estrategias = models.TextField('Estratégias de Ensino')
    recursos = models.TextField('Recursos Didáticos')
    avaliacao = models.TextField('Processo Avaliativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Adaptação Curricular'
        verbose_name_plural = 'Adaptações Curriculares'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"Adaptação em {self.componente_curricular} para {self.plano_educacional.pdi.neurodivergente}"

    def clean(self):
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': 'A data de finalização não pode ser anterior à data de início.'
            })