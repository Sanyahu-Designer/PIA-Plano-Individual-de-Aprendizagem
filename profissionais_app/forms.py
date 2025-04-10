from django import forms
import requests
from .models import Profissional

class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = '__all__'
        labels = {
            'user': 'Usuário',
        }
        widgets = {
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'vDateField'
                }
            ),
            'horario_manha_inicio': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'horario_manha_fim': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'horario_tarde_inicio': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'horario_tarde_fim': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'biografia': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Conte um pouco sobre você...'}
            ),
            'formacao': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Descreva sua formação acadêmica...'}
            ),
            'especialidade': forms.TextInput(
                attrs={'placeholder': 'Ex: Especialização em Autismo'}
            ),
            'registro_profissional': forms.TextInput(
                attrs={'placeholder': 'Ex: CRP 12/34567'}
            ),
            'facebook': forms.URLInput(
                attrs={'placeholder': 'https://facebook.com/seu.perfil'}
            ),
            'instagram': forms.URLInput(
                attrs={'placeholder': 'https://instagram.com/seu.perfil'}
            ),
            'celular': forms.TextInput(
                attrs={'data-mask': '(00) 00000-0000'}
            ),
            'cep': forms.TextInput(
                attrs={
                    'data-mask': '00000-000',
                    'class': 'viacep',
                    'placeholder': 'Digite o CEP'
                }
            ),
            'experiencia_neurodiversidade': forms.Select(
                choices=Profissional.SIM_NAO_CHOICES
            ),
            'profissao': forms.Select(
                attrs={'class': 'select2'},
                choices=Profissional.PROFISSAO_CHOICES
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%Y-%m-%d')

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