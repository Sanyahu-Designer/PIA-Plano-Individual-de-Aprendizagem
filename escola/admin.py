from django.contrib import admin
from django.utils.html import format_html
from .models import ModalidadeEnsino, ProgramaEducacional, Recurso, Escola
from .forms import EscolaForm

# Registros temporariamente comentados - podem ser necessários no futuro
"""
@admin.register(ModalidadeEnsino)
class ModalidadeEnsinoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'idade_minima', 'idade_maxima', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']

@admin.register(ProgramaEducacional)
class ProgramaEducacionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']
"""

@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    form = EscolaForm
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'nome', 'codigo_inep', 'tipo', 'ativo'
            ),
            'classes': ('tab-basic',)
        }),
        ('Contato', {
            'fields': (
                'telefone', 'email', 'diretor'
            ),
            'classes': ('tab-contact',)
        }),
        ('Endereço', {
            'fields': (
                'cep', 'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'estado'
            ),
            'classes': ('tab-address',)
        }),
        ('Funcionamento', {
            'fields': (
                'turnos', 'capacidade_atendimento'
                # Campo temporariamente oculto - pode ser necessário no futuro
                # 'modalidades',
            ),
            'classes': ('tab-operation',)
        }),
        ('Equipe Multiprofissional', {
            'fields': (
                'profissionais_educacao', 'profissionais_saude'
            ),
            'classes': ('tab-professionals',)
        }),
        # Aba temporariamente oculta - pode ser necessária no futuro
        # ('Recursos e Programas', {
        #     'fields': (
        #         'programas_educacionais', 'recursos_disponiveis'
        #     ),
        #     'classes': ('tab-resources',)
        # }),
    )

    list_display = [
        'nome', 'codigo_inep', 'telefone', 'cidade',
        'estado', 'tipo', 'get_turnos', 'ativo'
    ]
    
    list_filter = [
        'tipo', 'estado', 'turnos', 'ativo'
    ]
    
    search_fields = [
        'nome', 'codigo_inep', 'email',
        'diretor', 'cidade', 'bairro'
    ]
    
    list_editable = ['ativo']
    
    filter_horizontal = ['profissionais_educacao', 'profissionais_saude']
    
    def get_turnos(self, obj):
        return obj.get_turnos_display()
    get_turnos.short_description = 'Turnos'

    class Media:
        css = {
            'all': (
                'admin/css/escola_forms.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            )
        }
        js = (
            'admin/js/jquery.mask.min.js',
            'admin/js/escola_admin.js',
            'admin/js/escola_professionals.js',
        )