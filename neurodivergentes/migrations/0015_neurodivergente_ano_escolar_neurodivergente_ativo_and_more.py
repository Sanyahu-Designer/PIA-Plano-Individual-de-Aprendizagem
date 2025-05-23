# Generated by Django 5.1.2 on 2025-04-16 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0002_anoescolar'),
        ('neurodivergentes', '0014_alter_pdi_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='neurodivergente',
            name='ano_escolar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alunos', to='neurodivergentes.seriescursadas', verbose_name='Ano Escolar'),
        ),
        migrations.AddField(
            model_name='neurodivergente',
            name='ativo',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
        migrations.AddField(
            model_name='neurodivergente',
            name='escola',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alunos', to='escola.escola', verbose_name='Escola'),
        ),
    ]
