from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Profissional
from .forms import ProfissionalForm

class ProfissionalInline(admin.StackedInline):
    model = Profissional
    form = ProfissionalForm
    can_delete = False
    verbose_name_plural = 'Profissional'
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': (
                'foto_perfil', 'foto_preview', 'celular',
                'data_nascimento', 'genero'
            ),
            'classes': ('tab-dados-pessoais',)
        }),
        ('Qualificação Profissional', {
            'fields': (
                'profissao', 'especialidade', 'registro_profissional',
                'local_registro', 'formacao', 'experiencia_neurodiversidade'
            ),
            'classes': ('tab-qualificacao',)
        }),
        ('Endereço', {
            'fields': (
                'cep', 'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'estado'
            ),
            'classes': ('tab-endereco',)
        }),
        ('Outros', {
            'fields': (
                'biografia', 'facebook', 'instagram'
            ),
            'classes': ('tab-outros',)
        }),
    )

    readonly_fields = ['foto_preview']

    class Media:
        css = {
            'all': ('admin/css/profissionais_forms.css',)
        }
        js = (
            'admin/js/jquery.mask.min.js',
            'admin/js/profissionais_admin.js',
            'admin/js/cep_autocomplete.js',
        )

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    form = ProfissionalForm
    list_display = ['get_nome_completo', 'get_profissao', 'celular', 'cidade', 'estado']
    list_filter = ['profissao', 'estado', 'experiencia_neurodiversidade']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'celular']
    ordering = ['user__first_name', 'user__last_name']
    
    def get_search_results(self, request, queryset, search_term):
        """
        Customiza a busca para funcionar com o autocomplete do Django Admin
        """
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        return queryset, may_have_duplicates

    fieldsets = (
        ('Usuário', {
            'fields': ('user',),
            'description': 'Selecione o usuário associado ao profissional'
        }),
        ('Dados Pessoais', {
            'fields': (
                'foto_perfil', 'foto_preview', 'celular',
                'data_nascimento', 'genero'
            ),
            'classes': ('tab-dados-pessoais',)
        }),
        ('Qualificação Profissional', {
            'fields': (
                'profissao', 'especialidade', 'registro_profissional',
                'local_registro', 'formacao', 'experiencia_neurodiversidade'
            ),
            'classes': ('tab-qualificacao',)
        }),
        ('Endereço', {
            'fields': (
                'cep', 'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'estado'
            ),
            'classes': ('tab-endereco',)
        }),
        ('Outros', {
            'fields': (
                'biografia', 'facebook', 'instagram'
            ),
            'classes': ('tab-outros',)
        }),
    )

    readonly_fields = ['foto_preview']

    def get_nome_completo(self, obj):
        return obj.user.get_full_name()
    get_nome_completo.short_description = 'Nome'
    get_nome_completo.admin_order_field = 'user__first_name'

    def get_profissao(self, obj):
        return obj.get_profissao_display()
    get_profissao.short_description = 'Profissão'
    get_profissao.admin_order_field = 'profissao'

    
    class Media:
        css = {
            'all': ('admin/css/profissionais_forms.css',)
        }
        js = (
            'admin/js/jquery.mask.min.js',
            'admin/js/profissionais_admin.js',
            'admin/js/cep_autocomplete.js',
        )