from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class MetaHabilidade(models.Model):
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta/Habilidade'
        verbose_name_plural = 'Metas/Habilidades'
        ordering = ['nome']

    def __str__(self):
        return "Metas/Habilidades"

class PDIMetaHabilidade(models.Model):
    PROGRESSO_CHOICES = [(i, f'{i}%') for i in range(0, 101, 10)]

    pdi = models.ForeignKey(
        'PDI',
        on_delete=models.CASCADE,
        related_name='metas_habilidades'
    )
    meta_habilidade = models.ForeignKey(
        MetaHabilidade,
        on_delete=models.PROTECT,
        verbose_name='Meta/Habilidade'
    )
    progresso = models.IntegerField(
        'Progresso (%)',
        choices=PROGRESSO_CHOICES,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta/Habilidade'
        verbose_name_plural = 'Metas/Habilidades'
        ordering = ['-created_at']
        unique_together = ['pdi', 'meta_habilidade']

    def __str__(self):
        return f"{self.meta_habilidade} - {self.progresso}%"