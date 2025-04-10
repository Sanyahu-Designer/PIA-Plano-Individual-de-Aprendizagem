from django.db import models
from django.core.exceptions import ValidationError
from ..models import Neurodivergente

class CategoriaNeurodivergente(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.IntegerField('Ordem de Exibição', default=0)
    
    class Meta:
        verbose_name = 'Categoria CID-10'
        verbose_name_plural = 'Categorias CID-10'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return "Categorias CID-10"
        
    def get_nome_real(self):
        return self.nome

class CondicaoNeurodivergente(models.Model):
    categoria = models.ForeignKey(
        CategoriaNeurodivergente,
        on_delete=models.PROTECT,
        related_name='condicoes',
        verbose_name='Categoria'
    )
    nome = models.CharField('Nome da Condição', max_length=200)
    cid_10 = models.CharField('CID-10', max_length=50)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Condição CID-10'
        verbose_name_plural = 'Condições CID-10'
        ordering = ['categoria', 'nome']
        unique_together = ['categoria', 'nome']

    def __str__(self):
        return f"{self.nome} - CID-10: {self.cid_10}"

class Neurodivergencia(models.Model):
    neurodivergente = models.OneToOneField(
        Neurodivergente,
        on_delete=models.CASCADE,
        related_name='neurodivergencias',
        verbose_name='Aluno/Paciente'
    )
    data_diagnostico = models.DateField(
        'Data do Diagnóstico',
        blank=True,
        null=True
    )
    profissional_diagnostico = models.CharField(
        'Profissional Responsável',
        max_length=100,
        blank=True
    )
    observacoes = models.TextField(
        'Observações',
        blank=True
    )
    laudo_medico = models.FileField(
        'Laudo Médico',
        upload_to='neurodivergentes/laudos/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Neurodivergente'
        verbose_name_plural = 'Neurodivergentes'

    def __str__(self):
        return f"Neurodivergências - {self.neurodivergente}"

class DiagnosticoNeurodivergente(models.Model):
    neurodivergencia = models.ForeignKey(
        Neurodivergencia,
        on_delete=models.CASCADE,
        related_name='diagnosticos'
    )
    categoria = models.ForeignKey(
        CategoriaNeurodivergente,
        on_delete=models.PROTECT,
        related_name='diagnosticos'
    )
    condicao = models.ForeignKey(
        CondicaoNeurodivergente,
        on_delete=models.PROTECT,
        related_name='diagnosticos',
        verbose_name='Neurodivergência'
    )
    data_identificacao = models.DateField('Data de Identificação')
    observacoes = models.TextField('Observações', blank=True)
    
    def save(self, *args, **kwargs):
        # Garante que a categoria seja definida com base na condição antes de salvar
        if self.condicao_id and not self.categoria_id:
            self.categoria = self.condicao.categoria
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Diagnóstico'
        verbose_name_plural = 'Diagnósticos'
        ordering = ['data_identificacao']
        unique_together = ['neurodivergencia', 'condicao']

    def __str__(self):
        data_formatada = self.data_identificacao.strftime('%d/%m/%Y') if self.data_identificacao else ''
        return f"{self.condicao} - {data_formatada}"

    def clean(self):
        # Garante que a categoria seja definida com base na condição
        if self.condicao_id and not self.categoria_id:
            self.categoria = self.condicao.categoria
            
        # Verifica se a condição pertence à categoria apenas se ambos estiverem definidos
        if self.condicao_id and self.categoria_id and self.condicao.categoria_id != self.categoria_id:
            raise ValidationError({
                'condicao': 'A condição selecionada não pertence à categoria escolhida.'
            })