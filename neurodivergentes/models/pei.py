from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from ..models import Neurodivergente
from profissionais_app.models import Profissional

class Monitoramento(models.Model):
    neurodivergente = models.ForeignKey(
        Neurodivergente,
        verbose_name='Aluno/Paciente',
        on_delete=models.CASCADE,
        related_name='monitoramentos'
    )
    mes = models.IntegerField(
        'Mês',
        help_text='Selecione o mês do PEI',
        choices=[
            (1, 'Janeiro'),
            (2, 'Fevereiro'),
            (3, 'Março'),
            (4, 'Abril'),
            (5, 'Maio'),
            (6, 'Junho'),
            (7, 'Julho'),
            (8, 'Agosto'),
            (9, 'Setembro'),
            (10, 'Outubro'),
            (11, 'Novembro'),
            (12, 'Dezembro')
        ],
        default=timezone.now().month
    )
    ano = models.IntegerField(
        'Ano',
        help_text='Selecione o ano do PEI',
        default=timezone.now().year
    )
    metas = models.ManyToManyField(
        'neurodivergentes.MetaHabilidade',
        through='MonitoramentoMeta',
        verbose_name='Metas/Habilidades',
        help_text='Selecione uma ou mais metas/habilidades para este planejamento'
    )
    observacoes = CKEditor5Field(
        'Planejamento',
        help_text='Descreva o planejamento para esta meta/habilidade',
        null=True,
        blank=True
    )
    pedagogo_responsavel = models.ForeignKey(
        'profissionais_app.Profissional',
        verbose_name='Profissional Responosável',
        on_delete=models.PROTECT,
        related_name='monitoramentos',
        limit_choices_to={'profissao__in': ['assistente_social', 'educador_especial', 'neuropsicopedagogo', 'pedagogo', 'psicopedagogo']},
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'PAEE'
        verbose_name_plural = 'PAEE'
        ordering = ['-ano', '-mes']
        unique_together = ['neurodivergente', 'mes', 'ano']

    def __str__(self):
        return f"PEI de {self.neurodivergente} - {self.get_mes_display()}/{self.ano}"

class MonitoramentoMeta(models.Model):
    monitoramento = models.ForeignKey(
        'neurodivergentes.Monitoramento',
        on_delete=models.CASCADE,
        related_name='monitoramento_metas'
    )
    meta = models.ForeignKey(
        'neurodivergentes.MetaHabilidade',
        on_delete=models.CASCADE,
        related_name='monitoramento_metas'
    )

    class Meta:
        db_table = 'neurodivergentes_monitoramento_metas'
        unique_together = ['monitoramento', 'meta']

    def __str__(self):
        return f"{self.monitoramento} - {self.meta}"
