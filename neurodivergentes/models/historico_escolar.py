from django.db import models
from django.core.exceptions import ValidationError
from escola.models import Escola

class SeriesCursadas(models.Model):
    SERIES_CHOICES = [
        ('EDUCAÇÃO INFANTIL', (
            ('bercario1', 'Berçário I'),
            ('bercario2', 'Berçário II'),
            ('maternal', 'Maternal'),
            ('jardim', 'Jardim'),
            ('pre1', 'Pré I'),
            ('pre2', 'Pré II'),
        )),
        ('ENSINO FUNDAMENTAL I', (
            ('1ano', '1º Ano'),
            ('2ano', '2º Ano'),
            ('3ano', '3º Ano'),
            ('4ano', '4º Ano'),
            ('5ano', '5º Ano'),
        )),
        ('ENSINO FUNDAMENTAL II', (
            ('6ano', '6º Ano'),
            ('7ano', '7º Ano'),
            ('8ano', '8º Ano'),
            ('9ano', '9º Ano'),
        )),
    ]

    nome = models.CharField(
        'Série',
        max_length=10,
        choices=[item for group in SERIES_CHOICES for item in group[1]]
    )
    categoria = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('EDUCAÇÃO INFANTIL', 'Educação Infantil'),
            ('ENSINO FUNDAMENTAL I', 'Ensino Fundamental I'),
            ('ENSINO FUNDAMENTAL II', 'Ensino Fundamental II'),
        ]
    )
    ordem = models.IntegerField('Ordem de exibição', default=0)

    class Meta:
        verbose_name = 'Série Cursada'
        verbose_name_plural = 'Séries Cursadas'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.get_nome_display()

    def save(self, *args, **kwargs):
        # Define a ordem baseada na série
        ordem_map = {
            'bercario1': 1, 'bercario2': 2, 'maternal': 3,
            'jardim': 4, 'pre1': 5, 'pre2': 6,
            '1ano': 7, '2ano': 8, '3ano': 9, '4ano': 10, '5ano': 11,
            '6ano': 12, '7ano': 13, '8ano': 14, '9ano': 15
        }
        self.ordem = ordem_map.get(self.nome, 0)
        super().save(*args, **kwargs)

class HistoricoEscolar(models.Model):
    SERIES_CHOICES = [
        ('EDUCAÇÃO INFANTIL', (
            ('bercario1', 'Berçário I'),
            ('bercario2', 'Berçário II'),
            ('maternal', 'Maternal'),
            ('jardim', 'Jardim'),
            ('pre1', 'Pré I'),
            ('pre2', 'Pré II'),
        )),
        ('ENSINO FUNDAMENTAL I', (
            ('1ano', '1º Ano'),
            ('2ano', '2º Ano'),
            ('3ano', '3º Ano'),
            ('4ano', '4º Ano'),
            ('5ano', '5º Ano'),
        )),
        ('ENSINO FUNDAMENTAL II', (
            ('6ano', '6º Ano'),
            ('7ano', '7º Ano'),
            ('8ano', '8º Ano'),
            ('9ano', '9º Ano'),
        )),
    ]

    MODALIDADE_CHOICES = [
        ('regular', 'Ensino Regular'),
        ('especial', 'Ensino Especial'),
        ('inclusivo', 'Inclusivo'),
    ]

    neurodivergente = models.OneToOneField(
        'neurodivergentes.Neurodivergente',
        on_delete=models.CASCADE,
        related_name='historico_escolar'
    )
    escola_atual = models.ForeignKey(
        Escola,
        on_delete=models.PROTECT,
        related_name='alunos_neurodivergentes'
    )
    serie_atual = models.CharField(
        'Série/Ano Atual',
        max_length=10,
        choices=[item for group in SERIES_CHOICES for item in group[1]]
    )
    modalidade_ensino = models.CharField(
        'Modalidade de Ensino',
        max_length=10,
        choices=MODALIDADE_CHOICES
    )
    series_cursadas = models.ManyToManyField(
        SeriesCursadas,
        verbose_name='Séries Cursadas',
        related_name='historicos',
        help_text='Selecione todas as séries já cursadas na rede municipal',
        blank=True
    )
    adaptacoes_curriculares = models.TextField(
        'Adaptações Curriculares Necessárias',
        blank=True
    )
    necessidades_especificas = models.TextField(
        'Necessidades Educacionais Específicas',
        blank=True
    )
    historico_documento = models.FileField(
        'Histórico Escolar',
        upload_to='neurodivergentes/historicos/',
        blank=True,
        null=True
    )
    relatorios_pedagogicos = models.FileField(
        'Relatórios Pedagógicos',
        upload_to='neurodivergentes/relatorios/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Histórico Escolar'
        verbose_name_plural = 'Históricos Escolares'

    def __str__(self):
        return f"Histórico de {self.neurodivergente}"