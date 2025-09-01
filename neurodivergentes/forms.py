from django import forms
import requests
from django.utils import timezone
from .models import (
    Neurodivergente, GrupoFamiliar, Neurodivergencia,
    PDI, PlanoEducacional,
    AdaptacaoCurricular, RegistroEvolucao,
    Monitoramento, ParecerAvaliativo,
    MetaHabilidade, Anamnese
)
from django.core.exceptions import ValidationError

class NeurodivergenteForms(forms.ModelForm):
    class Meta:
        model = Neurodivergente
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'escola': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Selecione a escola',
                'data-minimum-results-for-search': '0',
                'style': 'width: 100%;'
            }),
            'ano_escolar': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Selecione o ano escolar',
                'data-minimum-results-for-search': '0',
                'style': 'width: 100%;'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'margin-left: 0.5rem;'
            }),
            'motivo_inatividade': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva o motivo da inatividade (ex: transferência de cidade, mudança de escola, etc.)',
                'style': 'width: 100%;'
            }),
            'nacionalidade': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Selecione a nacionalidade',
                'data-minimum-results-for-search': '0',
                'style': 'width: 100%;'
            }),
            'naturalidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: São Paulo - SP, Rio de Janeiro - RJ',
                'style': 'width: 100%;'
            }),
            'pais_origem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Argentina, Estados Unidos',
                'style': 'width: 100%;'
            }),
            'cor_pele': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Selecione a cor da pele',
                'data-minimum-results-for-search': '0',
                'style': 'width: 100%;'
            }),
            'tipo_sanguineo': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Selecione o tipo sanguíneo',
                'data-minimum-results-for-search': '0',
                'style': 'width: 100%;'
            }),
        }

    def clean_cep(self):
        cep = self.cleaned_data['cep']
        cep = ''.join(filter(str.isdigit, cep))
        if len(cep) != 8:
            raise forms.ValidationError('CEP inválido.')
        
        # Formata o CEP
        cep_formatado = f'{cep[:5]}-{cep[5:]}'
        
        # A consulta à API do ViaCEP agora é feita via JavaScript no frontend
        # para evitar lentidão durante o salvamento
        
        return cep_formatado

class GrupoFamiliarForm(forms.ModelForm):
    class Meta:
        model = GrupoFamiliar
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'vinculo': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 100%;'
            }),
            'primeiro_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primeiro nome',
                'style': 'width: 100%;'
            }),
            'ultimo_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Último nome',
                'style': 'width: 100%;'
            }),
            'outro_vinculo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especifique o vínculo',
                'style': 'width: 100%;'
            }),
            'ocupacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ocupação',
                'style': 'width: 100%;'
            })
        }

class NeurodivergenciaForm(forms.ModelForm):
    class Meta:
        model = Neurodivergencia
        fields = '__all__'
        widgets = {
            'data_diagnostico': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            )
        }

class PDIForm(forms.ModelForm):
    class Meta:
        model = PDI
        fields = '__all__'
        widgets = {
            'data_criacao': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'meta': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva a meta ou habilidade a ser desenvolvida'
            }),
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Observações adicionais sobre o PDI'
            }),
            'neurodivergente': forms.Select(attrs={'class': 'form-select select2', 'data-minimum-results-for-search': '0'})
        }

class PlanoEducacionalForm(forms.ModelForm):
    class Meta:
        model = PlanoEducacional
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'data_fim': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'objetivos': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva os objetivos do plano'
            }),
            'estrategias': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva as estratégias a serem utilizadas'
            }),
            'recursos': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Liste os recursos necessários'
            })
        }

class AdaptacaoCurricularForm(forms.ModelForm):
    class Meta:
        model = AdaptacaoCurricular
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'data_fim': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'conteudo_adaptado': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva o conteúdo adaptado'
            }),
            'estrategias': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva as estratégias de ensino'
            }),
            'recursos': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Liste os recursos didáticos necessários'
            }),
            'avaliacao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva o processo avaliativo'
            })
        }

class RegistroEvolucaoForm(forms.ModelForm):
    def clean_anexos(self):
        anexo = self.cleaned_data.get('anexos')
        if anexo:
            if anexo.size > 5 * 1024 * 1024:
                raise ValidationError('Arquivo excede 5MB.')
            if not anexo.name.lower().endswith(('.pdf', '.docx')):
                raise ValidationError('Apenas PDF/DOCX permitidos.')
        return anexo

    class Meta:
        model = RegistroEvolucao
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'descricao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva a evolução observada'
            })
        }

class MonitoramentoForm(forms.ModelForm):
    metas = forms.ModelMultipleChoiceField(
        queryset=MetaHabilidade.objects.filter(ativo=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2',
            'style': 'width: 100%; color: #333333;'
        }),
        label='Metas/Habilidades',
        help_text='Selecione uma ou mais metas/habilidades para este planejamento'
    )

    class Meta:
        model = Monitoramento
        fields = ['neurodivergente', 'ano', 'metas', 'pedagogo_responsavel', 'observacoes']
        widgets = {
            'ano': forms.NumberInput(attrs={'min': 2020, 'max': 2050}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o planejamento para esta meta/habilidade',
                'style': 'width: 100%;'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-preenche com o ano atual se for um novo registro
        if not self.instance.pk:
            self.initial.update({
                'ano': timezone.now().year
            })

    def clean(self):
        cleaned_data = super().clean()
        ano = cleaned_data.get('ano')
        neurodivergente = cleaned_data.get('neurodivergente')
        metas = cleaned_data.get('metas')

        if ano and neurodivergente:
            # Verifica se já existe um PAEE para este ano/aluno
            if Monitoramento.objects.filter(
                neurodivergente=neurodivergente,
                ano=ano
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError(
                    'Já existe um PAEE para este aluno neste ano.'
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            # Limpa as metas existentes e adiciona as novas
            instance.metas.clear()
            metas = self.cleaned_data.get('metas')
            if metas:
                for meta in metas:
                    instance.monitoramento_metas.create(meta=meta)
        
        return instance

class ParecerAvaliativoForm(forms.ModelForm):
    class Meta:
        model = ParecerAvaliativo
        fields = '__all__'
        widgets = {
            'data_avaliacao': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'evolucao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva a evolução do aluno'
            }),
            'pontos_fortes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Liste os pontos fortes observados'
            }),
            'desafios': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva os desafios identificados'
            }),
            'recomendacoes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Liste as recomendações'
            }),
            'conclusoes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Apresente as conclusões'
            })
        }

class AnamneseForm(forms.ModelForm):
    def clean_anexos(self):
        anexo = self.cleaned_data.get('anexos')
        if anexo:
            if anexo.size > 5 * 1024 * 1024:
                raise ValidationError('Arquivo excede 5MB.')
            if not anexo.name.lower().endswith(('.pdf', '.docx')):
                raise ValidationError('Apenas PDF/DOCX permitidos.')
        return anexo
        
    class Meta:
        model = Anamnese
        fields = '__all__'
        widgets = {
            'tempo_gestacao': forms.NumberInput(attrs={'min': 20, 'max': 45}),
            'tempo_prematuridade': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'observacoes_parto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Observações sobre o parto'
            }),
            'comportamento_familiar': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva o comportamento no ambiente familiar'
            }),
            'comportamento_social': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva o comportamento em ambientes sociais'
            }),
            'aspectos_cognitivos': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva os aspectos cognitivos'
            }),
            'aspectos_psicomotores': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva os aspectos psicomotores'
            }),
            'aspectos_emocionais': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva os aspectos emocionais/sociais'
            }),
            'aspectos_sensoriais': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva os aspectos sensoriais'
            }),
            'descricao_restricoes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva as restrições alimentares'
            })
        }