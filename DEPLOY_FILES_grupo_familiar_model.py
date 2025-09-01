from django.db import models
from django.core.exceptions import ValidationError
from .base import Neurodivergente, validate_future_date
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class GrupoFamiliar(models.Model):
    VINCULO_CHOICES = [
        ('', '---------'),  # Opção em branco para evitar seleção automática
        ('pai_mae', 'Pai/Mãe'),
        ('filho', 'Filho(a)'),
        ('irmao', 'Irmão(ã)'),
        ('avo', 'Avô/Avó'),
        ('tio', 'Tio(a)'),
        ('sobrinho', 'Sobrinho(a)'),
        ('primo', 'Primo(a)'),
        ('conjuge', 'Cônjuge'),
        ('companheiro', 'Companheiro(a)'),
        ('padrasto', 'Padrasto/Madrasta'),
        ('enteado', 'Enteado(a)'),
        ('cunhado', 'Cunhado(a)'),
        ('genro', 'Genro/Nora'),
        ('sogro', 'Sogro(a)'),
        ('tutor', 'Tutor(a)'),
        ('cuidador', 'Cuidador(a)'),
        ('outro', 'Outro')
    ]
    
    neurodivergente = models.ForeignKey(
        Neurodivergente,
        on_delete=models.CASCADE,
        related_name='grupo_familiar',
        blank=True,
        null=True
    )
    primeiro_nome = models.CharField('Primeiro Nome', max_length=50, blank=True, null=True)
    ultimo_nome = models.CharField('Último Nome', max_length=50, blank=True, null=True)
    data_nascimento = models.DateField(
        'Data de Nascimento',
        validators=[validate_future_date],
        blank=True,
        null=True
    )
    vinculo = models.CharField(
        'Vínculo/Parentesco',
        max_length=20,
        choices=VINCULO_CHOICES,
        blank=True,
        null=True
    )
    outro_vinculo = models.CharField(
        'Especificar outro vínculo',
        max_length=50,
        blank=True,
        null=True
    )
    ocupacao = models.CharField('Ocupação', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Membro do Grupo Familiar'
        verbose_name_plural = 'Grupo Familiar'
        ordering = ['neurodivergente', 'primeiro_nome']
    
    def __str__(self):
        nome = f"{self.primeiro_nome or ''} {self.ultimo_nome or ''}".strip()
        vinculo = self.get_vinculo_display() if self.vinculo else ''
        if nome and vinculo:
            return f"{nome} - {vinculo}"
        elif nome:
            return nome
        elif vinculo:
            return vinculo
        else:
            return "Membro do Grupo Familiar"
    
    def clean(self):
        if self.vinculo == 'outro' and not self.outro_vinculo:
            raise ValidationError({'outro_vinculo': 'Por favor, especifique o vínculo quando selecionar "Outro".'})
        super().clean()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualização do neurodivergente será feita pelo signal post_save
        # para evitar recursão dupla

# Sinais para atualizar o neurodivergente quando um membro do grupo familiar for salvo ou excluído
@receiver(post_save, sender=GrupoFamiliar)
def update_neurodivergente_on_save(sender, instance, **kwargs):
    if instance.neurodivergente:
        # Usa update() para evitar recursão infinita
        from django.utils import timezone
        Neurodivergente.objects.filter(pk=instance.neurodivergente.pk).update(
            updated_at=timezone.now()
        )

@receiver(post_delete, sender=GrupoFamiliar)
def update_neurodivergente_on_delete(sender, instance, **kwargs):
    # Verifica se o neurodivergente ainda existe antes de tentar acessá-lo
    if hasattr(instance, 'neurodivergente_id') and instance.neurodivergente_id:
        try:
            # Usa update() para evitar recursão infinita
            from django.utils import timezone
            Neurodivergente.objects.filter(pk=instance.neurodivergente_id).update(
                updated_at=timezone.now()
            )
        except Neurodivergente.DoesNotExist:
            # Se o neurodivergente não existir mais, não faz nada
            pass