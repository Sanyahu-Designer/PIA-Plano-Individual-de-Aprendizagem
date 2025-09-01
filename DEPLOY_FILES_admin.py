from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count, Subquery, OuterRef, Avg
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.template import loader
from .choices import MESES
from escola.models import ModalidadeEnsino, ProgramaEducacional, Recurso, Escola
from escola.forms import EscolaForm
from .models import (
    Neurodivergente, GrupoFamiliar,
    Neurodivergencia, CondicaoNeurodivergente,
    CategoriaNeurodivergente, DiagnosticoNeurodivergente,
    Anamnese, PDI, MetaHabilidade, PDIMetaHabilidade,
    PlanoEducacional, AdaptacaoCurricular, RegistroEvolucao,
    Monitoramento, ParecerAvaliativo
)
from .forms import (
    NeurodivergenteForms, GrupoFamiliarForm, PDIForm, PlanoEducacionalForm,
    AdaptacaoCurricularForm, RegistroEvolucaoForm,
    MonitoramentoForm, ParecerAvaliativoForm, NeurodivergenciaForm,
    AnamneseForm
)

from django.db.models import Max
from django.shortcuts import get_object_or_404

class GrupoFamiliarInline(admin.StackedInline):
    model = GrupoFamiliar
    form = GrupoFamiliarForm
    extra = 2  # Permite adicionar pelo menos dois novos membros por padrão
    template = 'admin/neurodivergentes/edit_inline/stacked_grupo_familiar.html'
    can_delete = True
    show_change_link = False
    
    formfield_overrides = {
        models.DateField: {
            'widget': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'vDateField date-input form-control',
                },
                format='%Y-%m-%d'
            )
        },
        models.CharField: {
            'widget': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            )
        },
        models.TextField: {
            'widget': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            )
        }
    }
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomFormset(formset):
            def _construct_form(self, *args, **kwargs):
                form = super()._construct_form(*args, **kwargs)
                if form.instance and form.instance.data_nascimento:
                    form.initial['data_nascimento'] = form.instance.data_nascimento.strftime('%Y-%m-%d')
                return form
                
            def save_new(self, form, commit=True):
                """
                Sobrescreve o método save_new para garantir que novos membros
                sejam corretamente salvos no banco de dados.
                """
                obj = super().save_new(form, commit=False)
                if commit:
                    obj.save()
                return obj
        
        return CustomFormset
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'vinculo':
            kwargs['widget'] = forms.Select(attrs={'class': 'form-control'})
            kwargs['choices'] = GrupoFamiliar.VINCULO_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/grupo_familiar.css',)
        }
        js = ('admin/js/grupo_familiar.js',)

@admin.register(Neurodivergente)
class NeurodivergenteAdmin(admin.ModelAdmin):
    verbose_name = 'Aluno/Paciente'
    verbose_name_plural = 'Alunos/Pacientes'
    form = NeurodivergenteForms
    inlines = [GrupoFamiliarInline]
    readonly_fields = ['foto_preview']
    list_display = ['primeiro_nome', 'ultimo_nome', 'idade', 'cidade', 'estado']
    list_filter = ['estado', 'genero']
    search_fields = ['primeiro_nome', 'ultimo_nome', 'cpf']
    
    def get_search_results(self, request, queryset, search_term):
        """
        Customiza a busca para funcionar com o autocomplete do Django Admin
        """
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        return queryset, may_have_duplicates
    formfield_overrides = {
        models.DateField: {'widget': forms.DateInput(attrs={'class': 'vDateField', 'type': 'date'})}
    }

    fieldsets = (
        ('Dados Pessoais', {
            'fields': (
                'primeiro_nome', 'ultimo_nome', 'data_nascimento', 'genero',
                'cpf', 'rg', 'foto_perfil', 'foto_preview'
            ),
            'classes': ('tab-dados-pessoais',)
        }),
        ('Informações Complementares', {
            'fields': (
                ('nacionalidade', 'pais_origem', 'cor_pele', 'tipo_sanguineo'),
            ),
            'classes': ('tab-info-complementares',)
        }),
        ('Endereço', {
            'fields': (
                'cep', 'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'estado'
            ),
            'classes': ('tab-endereco',)
        }),
        ('Contato', {
            'fields': (
                'celular', 'email'
            ),
            'classes': ('tab-contato',)
        }),
        ('Informações Escolares', {
            'fields': (
                'escola', 'ano_escolar', 'ativo'
            ),
            'classes': ('tab-informacoes-escolares',)
        })
    )


    
    class Media:
        css = {
            'all': ('admin/css/neurodivergentes_forms.css',)
        }
        js = (
            'admin/js/jquery.mask.min.js',
            'admin/js/neurodivergentes_admin.js',
            'admin/js/grupo_familiar.js',
            'admin/js/cep_autocomplete.js',
        )

@admin.register(CategoriaNeurodivergente)
class CategoriaNeurodivergentesAdmin(admin.ModelAdmin):
    list_display = ['nome']
    ordering = ['nome']
    search_fields = ['nome']
    exclude = ['ordem']
    change_list_template = 'admin/cid10/categoriacid10/change_list_material_dashboard.html'
    change_form_template = 'admin/cid10/categoriacid10/change_form.html'
    
    fieldsets = [
        ('Informações Gerais', {
            'fields': ['nome', 'descricao']
        }),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Personalizar widget de seleção com classes do Select2
        for field_name in form.base_fields:
            form.base_fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'style': 'border: 1px solid #d2d6da; border-radius: 0.5rem;'
            })
        
        return form

    def save_model(self, request, obj, form, change):
        # Se for uma nova categoria (sem ordem definida), define a ordem automaticamente
        if not change or obj.ordem == 0:
            # Obtém o maior valor de ordem existente e adiciona 1
            max_ordem = CategoriaNeurodivergente.objects.aggregate(models.Max('ordem'))['ordem__max'] or 0
            obj.ordem = max_ordem + 1
        super().save_model(request, obj, form, change)
        
    def __str__(self):
        return self.nome

    class Media:
        css = {
            'all': (
                'admin/css/base.css',
                'static/admin/css/edit_form_standard.css',
                'static/admin/css/form_fields_style.css'
            )
        }
        js = (
            'admin/js/jquery.js',
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/actions.js',
            'admin/js/urlify.js',
            'admin/js/prepopulate.js',
            'admin/js/vendor/select2/select2.full.min.js',
            'admin/js/vendor/select2/i18n/pt-BR.js'
        )

@admin.register(CondicaoNeurodivergente)
class CondicaoNeurodivergentesAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'cid_10']
    list_filter = ['categoria']
    search_fields = ['nome', 'cid_10']
    ordering = ['nome']
    exclude = ['ativo']  # Excluir o campo 'ativo' do formulário
    change_list_template = 'admin/cid10/condicaocid10/change_list_material_dashboard.html'
    change_form_template = 'admin/cid10/condicaocid10/change_form.html'
    
    fieldsets = [
        ('Informações Gerais', {
            'fields': ['categoria', 'nome', 'cid_10', 'descricao']
        }),
    ]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Personalizar widget de seleção com classes do Select2
        for field_name in form.base_fields:
            form.base_fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'style': 'border: 1px solid #d2d6da; border-radius: 0.5rem;'
            })
        
        return form
        
    def save_model(self, request, obj, form, change):
        # Garantir que o campo 'ativo' sempre seja True
        obj.ativo = True
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': (
                'admin/css/base.css',
                'static/admin/css/edit_form_standard.css',
                'static/admin/css/form_fields_style.css'
            )
        }
        js = (
            'admin/js/jquery.js',
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/actions.js',
            'admin/js/urlify.js',
            'admin/js/prepopulate.js',
            'admin/js/vendor/select2/select2.full.min.js',
            'admin/js/vendor/select2/i18n/pt-BR.js'
        )
    
# Formulário personalizado para DiagnosticoNeurodivergente
    
class DiagnosticoNeurodivergenteForms(forms.ModelForm):
    class Meta:
        model = DiagnosticoNeurodivergente
        fields = ('condicao', 'data_identificacao', 'observacoes')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Armazena o estado original do formulário para comparar depois
        if self.instance and self.instance.pk:
            self.original_condicao_id = self.instance.condicao_id
        else:
            self.original_condicao_id = None
            
        # Torna o campo data_identificacao opcional no admin
        if 'data_identificacao' in self.fields:
            self.fields['data_identificacao'].required = False
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Garante que a categoria seja definida com base na condição
        if instance.condicao_id:
            instance.categoria = instance.condicao.categoria
        
        if commit:
            instance.save()
        
        return instance

class DiagnosticoInline(admin.StackedInline):
    model = DiagnosticoNeurodivergente
    form = DiagnosticoNeurodivergenteForms
    extra = 1
    min_num = 0  # Alterado para permitir remover todos os diagnósticos
    can_delete = True
    verbose_name = 'Diagnóstico'
    verbose_name_plural = 'Diagnósticos'
    template = 'admin/neurodivergentes/edit_inline/stacked_diagnostico.html'
    
    formfield_overrides = {
        models.DateField: {'widget': forms.DateInput(attrs={
            'class': 'vDateField form-control', 
            'type': 'date'
        })},
        models.TextField: {'widget': forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })},
        models.CharField: {'widget': forms.TextInput(attrs={
            'class': 'form-control'
        })}
    }
    
    fields = (
        ('data_identificacao',),
        ('condicao',),
        ('observacoes',)
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'condicao':
            # Organiza as condições por categoria para melhor visualização
            condicoes = CondicaoNeurodivergente.objects.all().order_by('categoria__nome', 'nome')
            kwargs['queryset'] = condicoes
            kwargs['widget'] = forms.Select(attrs={
                'class': 'form-control'
            })
            # Remove a validação de categoria para permitir a seleção de qualquer condição
            kwargs['to_field_name'] = 'id'
        elif db_field.name == 'categoria':
            # Torna o campo categoria não obrigatório para evitar problemas de validação
            kwargs['required'] = False
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/diagnostico.css',)
        }
        js = ('admin/js/diagnostico.js',)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomFormset(formset):
            def _construct_form(self, *args, **kwargs):
                form = super()._construct_form(*args, **kwargs)
                if form.instance and form.instance.data_identificacao:
                    form.initial['data_identificacao'] = form.instance.data_identificacao.strftime('%Y-%m-%d')
                return form
                
            def save_new(self, form, commit=True):
                """
                Sobrescreve o método save_new para garantir que novos diagnósticos
                sejam corretamente salvos no banco de dados.
                """
                obj = super().save_new(form, commit=False)
                
                # Garante que a categoria seja definida com base na condição
                if obj.condicao_id and not obj.categoria_id:
                    obj.categoria = obj.condicao.categoria
                
                if commit:
                    obj.save()
                return obj
        
        return CustomFormset
    
class AdaptacaoCurricularInline(admin.StackedInline):
    model = AdaptacaoCurricular
    form = AdaptacaoCurricularForm
    extra = 1
    verbose_name = 'Nova adaptação curricular'
    verbose_name_plural = 'Adaptações Curriculares'

@admin.register(Neurodivergencia)
class NeurodivergenciaAdmin(admin.ModelAdmin):
    form = NeurodivergenciaForm
    inlines = [DiagnosticoInline]
    list_display = ['neurodivergente', 'data_diagnostico', 'profissional_diagnostico']
    list_filter = ['data_diagnostico']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']
    change_list_template = 'admin/neurodivergentes/neurodivergencia/change_list_material_dashboard.html'
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo principal"""
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        """Processa os formsets de diagnósticos"""
        # Processa as exclusões normalmente
        instances = formset.save(commit=False)
        
        # Para cada instância, garante que a categoria seja definida corretamente
        for instance in instances:
            if isinstance(instance, DiagnosticoNeurodivergente) and instance.condicao_id:
                instance.categoria = instance.condicao.categoria
                instance.save()
        
        # Processa as exclusões
        for obj in formset.deleted_objects:
            obj.delete()
            
        # Salva as relações many-to-many
        formset.save_m2m()
    
    fieldsets = (
        ('Aluno/Paciente', {
            'fields': ('neurodivergente',)
        }),
        ('Diagnóstico', {
            'fields': (
                'data_diagnostico',
                'profissional_diagnostico',
                'observacoes',
                'laudo_medico'
            ),
            'classes': ('wide', 'diagnosticos-container')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.data_diagnostico:
            form.base_fields['data_diagnostico'].initial = obj.data_diagnostico.strftime('%Y-%m-%d')
        return form

    
    class Media:
        css = {
            'all': ('neurodivergentes/css/neurodivergentes_forms.css',)
        }
        js = ('admin/js/neurodivergentes_admin.js',)

@admin.register(MetaHabilidade)
class MetaHabilidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    list_filter = []
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    exclude = ['ativo']
    change_list_template = 'admin/metashabilidades/metahabilidade/change_list_material_dashboard.html'
    change_form_template = 'admin/metashabilidades/metahabilidade/change_form.html'
    
    fieldsets = [
        ('Informações Gerais', {
            'fields': ['nome', 'descricao']
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        obj.ativo = True
        super().save_model(request, obj, form, change)
    
class PDIMetaHabilidadeInline(admin.TabularInline):
    model = PDIMetaHabilidade
    extra = 5
    min_num = 0
    can_delete = True
    fields = ('meta_habilidade', 'progresso')
    template = 'admin/neurodivergentes/edit_inline/tabular_meta_habilidade.html'
    classes = []  # Removendo qualquer classe CSS personalizada que possa estar interferindo
    
@admin.register(PDI)
class PDIAdmin(admin.ModelAdmin):
    form = PDIForm
    inlines = [PDIMetaHabilidadeInline]
    list_display = ['get_aluno_nome', 'get_idade', 'get_total_pdis', 'get_ultimo_pdi', 'get_view_button', 'get_status', 'get_qtd_metas', 'get_responsavel']
    list_filter = ['neurodivergente']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']
    list_per_page = 20
    autocomplete_fields = ['neurodivergente']

    def get_queryset(self, request):
        """
        Retorna apenas o PDI mais recente por aluno na lista inicial,
        ou todos os PDIs se um filtro de aluno estiver ativo.
        """
        self.request = request
        queryset = super().get_queryset(request).select_related(
            'neurodivergente', 'pedagogo_responsavel'
        ).prefetch_related('metas_habilidades')

        neurodivergente_id = request.GET.get('neurodivergente__id__exact')
        if neurodivergente_id:
            # Lista todos os PDIs do aluno filtrado
            return queryset.filter(neurodivergente_id=neurodivergente_id).order_by('-data_criacao')

        # Lista inicial: retorna apenas o PDI mais recente por aluno
        from django.db.models import Max
        latest_pdi_ids = queryset.values('neurodivergente').annotate(
            max_id=Max('id')
        ).values_list('max_id', flat=True)

        return queryset.filter(id__in=latest_pdi_ids).order_by('neurodivergente__primeiro_nome')

    def get_object(self, request, object_id, from_field=None):
        """
        Personaliza a busca de objetos para garantir que qualquer PDI seja carregado,
        independentemente do queryset usado na exibição agrupada.
        """
        queryset = super().get_queryset(request)
        return get_object_or_404(PDI, pk=object_id)

    def get_aluno_nome(self, obj):
        """
        Gera o link correto para o nome do aluno:
        - Lista inicial: redireciona para a lista de PDIs do aluno.
        - Lista filtrada: redireciona para o detalhe do PDI.
        """
        if not obj.neurodivergente:
            return '-'

        if hasattr(self, 'request') and 'neurodivergente__id__exact' not in self.request.GET:
            # Link para a lista de PDIs do aluno
            url = f"{reverse('admin:neurodivergentes_pdi_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
        else:
            # Link para o detalhe do PDI
            url = reverse('admin:neurodivergentes_pdi_change', args=[obj.id])

        nome_completo = f"{obj.neurodivergente.primeiro_nome} {obj.neurodivergente.ultimo_nome}"
        return format_html(
            '<a href="{}" style="color: #447e9b; text-decoration: none;">{}</a>',
            url,
            nome_completo
        )
    get_aluno_nome.short_description = 'Aluno/Paciente'
    get_aluno_nome.admin_order_field = 'neurodivergente__primeiro_nome'

    def get_total_pdis(self, obj):
        """
        Retorna o número total de PDIs associados ao aluno.
        """
        if not obj.neurodivergente:
            return 0
        return PDI.objects.filter(neurodivergente=obj.neurodivergente).count()
    get_total_pdis.short_description = 'Total de PDIs'

    def get_ultimo_pdi(self, obj):
        """
        Retorna a data de criação do último PDI.
        """
        return obj.data_criacao if obj.data_criacao else '-'
    get_ultimo_pdi.short_description = 'Último PDI'

    def changelist_view(self, request, extra_context=None):
        """
        Ajusta as colunas exibidas na listagem com base no contexto:
        - Lista inicial: exibe agrupamento.
        - Lista detalhada: exibe todos os PDIs do aluno.
        """
        self.request = request
        if 'neurodivergente__id__exact' in request.GET:
            self.list_display = ['get_aluno_nome', 'data_criacao', 'get_status', 'get_qtd_metas', 'get_responsavel', 'get_print_button']
        else:
            self.list_display = ['get_aluno_nome', 'get_idade', 'get_total_pdis', 'get_ultimo_pdi', 'get_view_button', 'get_status', 'get_qtd_metas', 'get_responsavel']
        return super().changelist_view(request, extra_context)

    def get_progresso(self, obj):
        """
        Calcula o progresso médio das metas associadas ao PDI.
        """
        metas = obj.metas_habilidades.all()
        if not metas:
            return '0%'
        total_progresso = sum(meta.progresso for meta in metas)
        media_progresso = total_progresso / len(metas)
        return f'{int(media_progresso)}%'
    get_progresso.short_description = 'Progresso (%)'

    def get_view_button(self, obj):
        """
        Gera um botão de ação para visualizar detalhes do PDI.
        """
        if not obj.id:
            return '-'

        if hasattr(self, 'request') and 'neurodivergente__id__exact' in self.request.GET:
            return format_html(
                '<a href="{}" class="btn btn-outline-primary btn-sm mb-0" target="_blank">'                
                '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">print</i> Imprimir</a>',
                reverse('admin:neurodivergentes_pdi_change', args=[obj.id])
            )
        else:
            url = f"{reverse('admin:neurodivergentes_pdi_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
            return format_html(
                '<a href="{}" class="btn btn-outline-primary btn-sm mb-0">'                
                '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">visibility</i> Ver PDIs</a>',
                url
            )
    get_view_button.short_description = 'Ações'

    def get_print_button(self, obj):
        """
        Gera botões de ação para o PDI: Editar, Imprimir e Remover.
        """
        if not obj.id:
            return '-'
            
        editar_url = reverse('admin:neurodivergentes_pdi_change', args=[obj.id])
        imprimir_url = reverse('neurodivergentes:imprimir_pdi', args=[obj.id])
        remover_url = reverse('admin:neurodivergentes_pdi_delete', args=[obj.id])
        
        return format_html(
            '<div class="btn-group">' 
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0" title="Editar"><i class="material-symbols-rounded opacity-10" style="font-size: 16px;">edit</i></a>' 
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0 ms-2" target="_blank" title="Imprimir"><i class="material-symbols-rounded opacity-10" style="font-size: 16px;">print</i></a>' 
            '<a href="{}" class="btn btn-outline-danger btn-sm mb-0 ms-2" title="Remover"><i class="material-symbols-rounded opacity-10" style="font-size: 16px;">delete</i></a>' 
            '</div>',
            editar_url,
            imprimir_url,
            remover_url
        )
    get_print_button.short_description = 'Ações'

    def get_idade(self, obj):
        """
        Retorna a idade e gênero do aluno.
        """
        if not obj.neurodivergente:
            return '-'
        return format_html(
            '<div class="d-flex flex-column"><span class="text-sm font-weight-bold">{} anos</span><span class="text-xs text-secondary">{}</span></div>',
            obj.neurodivergente.idade(),
            'Masculino' if obj.neurodivergente.genero == 'M' else 'Feminino'
        )
    get_idade.short_description = 'Idade'

    def get_status(self, obj):
        """
        Retorna o status do PDI baseado no progresso das metas.
        """
        metas = obj.metas_habilidades.all()
        if not metas:
            return format_html('<span class="badge bg-secondary">Pendente</span>')
            
        total_progresso = sum(meta.progresso for meta in metas)
        media_progresso = total_progresso / len(metas)
        
        if media_progresso >= 100:
            return format_html('<span class="badge bg-success">Concluído</span>')
        elif media_progresso > 0:
            return format_html('<span class="badge bg-warning">Em andamento</span>')
        else:
            return format_html('<span class="badge bg-secondary">Pendente</span>')
    get_status.short_description = 'Status'
    
    def get_qtd_metas(self, obj):
        """
        Retorna a quantidade de metas associadas ao PDI.
        """
        return obj.metas_habilidades.count()
    get_qtd_metas.short_description = 'Qtd. Metas'
    
    def get_responsavel(self, obj):
        """
        Retorna o nome do profissional responsável pelo PDI.
        """
        if hasattr(obj, 'pedagogo_responsavel') and obj.pedagogo_responsavel:
            return obj.pedagogo_responsavel.user.get_full_name()
        return '-'
    get_responsavel.short_description = 'Responsável'
    
    class Media:
        """
        Inclui arquivos CSS e JavaScript adicionais para customização.
        """
        css = {
            'all': (
                'admin/css/pdi_forms.css',
                'admin/css/pdi_popup.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            )
        }

        js = (
            # 'admin/js/pdi_admin.js',  # Desativado para resolver o problema com o card Metas/Habilidades
            # 'admin/js/pdi_popup.js',  # Temporariamente desativado para testar
        )

@admin.register(Monitoramento)
class MonitoramentoAdmin(admin.ModelAdmin):
    form = MonitoramentoForm
    list_display = ['get_aluno_nome', 'get_idade_sexo', 'get_total_peis', 'get_ultimo_pei', 'get_view_button']
    list_filter = ['neurodivergente']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']
    list_per_page = 20
    
    def changelist_view(self, request, extra_context=None):
        """
        Ajusta as colunas exibidas na listagem com base no contexto:
        - Lista inicial: exibe agrupamento.
        - Lista detalhada: exibe todos os PEIs do aluno.
        """
        self.request = request
        if 'neurodivergente__id__exact' in request.GET:
            self.list_display = ['get_aluno_nome', 'get_mes_ano', 'get_metas', 'get_acoes']
        else:
            self.list_display = ['get_aluno_nome', 'get_idade_sexo', 'get_total_peis', 'get_ultimo_pei', 'get_view_button']
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        """
        Retorna apenas o PEI mais recente por aluno na lista inicial,
        ou todos os PEIs se um filtro de aluno estiver ativo.
        """
        qs = super().get_queryset(request)
        
        # Se estamos na lista de PEIs de um aluno específico, retorna todos os PEIs desse aluno
        if request.GET.get('neurodivergente__id__exact'):
            return qs
        
        # Na lista inicial, agrupa por aluno e retorna apenas o PEI mais recente de cada aluno
        latest_peis = {}
        for pei in qs:
            if pei.neurodivergente_id not in latest_peis or (
                pei.ano > latest_peis[pei.neurodivergente_id].ano or 
                (pei.ano == latest_peis[pei.neurodivergente_id].ano and pei.mes > latest_peis[pei.neurodivergente_id].mes)
            ):
                latest_peis[pei.neurodivergente_id] = pei
        
        # Retorna apenas os PEIs mais recentes
        return qs.filter(id__in=[pei.id for pei in latest_peis.values()])

    def get_object(self, request, object_id, from_field=None):
        """
        Personaliza a busca de objetos para garantir que qualquer PEI seja carregado,
        independentemente do queryset usado na exibição agrupada.
        """
        queryset = super().get_queryset(request)
        return get_object_or_404(Monitoramento, pk=object_id)

    def get_aluno_nome(self, obj):
        """
        Gera o link correto para o nome do aluno:
        - Lista inicial: redireciona para a lista de PEIs do aluno.
        - Lista filtrada: redireciona para o detalhe do PEI.
        """
        if not obj.neurodivergente:
            return '-'

        if hasattr(self, 'request') and 'neurodivergente__id__exact' not in self.request.GET:
            # Link para a lista de PEIs do aluno
            url = f"{reverse('admin:neurodivergentes_monitoramento_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
        else:
            # Link para o detalhe do PEI
            url = reverse('admin:neurodivergentes_monitoramento_change', args=[obj.id])

        nome_completo = f"{obj.neurodivergente.primeiro_nome} {obj.neurodivergente.ultimo_nome}"
        return format_html(
            '<a href="{}" style="color: #447e9b; text-decoration: none;">{}</a>',
            url,
            nome_completo
        )
    get_aluno_nome.short_description = 'Aluno/Paciente'
    get_aluno_nome.admin_order_field = 'neurodivergente__primeiro_nome'

    def get_total_peis(self, obj):
        """
        Retorna o total de PEIs do aluno.
        """
        if not obj.neurodivergente:
            return 0
        total = Monitoramento.objects.filter(neurodivergente=obj.neurodivergente).count()
        return total
    get_total_peis.short_description = 'Total de PEIs'

    def get_ultimo_pei(self, obj):
        """
        Retorna o mês/ano do último PEI.
        """
        if not obj.neurodivergente:
            return '-'
        ultimo = Monitoramento.objects.filter(
            neurodivergente=obj.neurodivergente
        ).order_by('-ano', '-mes').first()
        
        if ultimo:
            return f"{ultimo.get_mes_display()}/{ultimo.ano}"
        return '-'
    get_ultimo_pei.short_description = 'Último PEI'

    def get_list_display(self, request):
        """
        Altera as colunas exibidas dependendo se estamos na lista inicial
        ou na lista de PEIs de um aluno.
        """
        if request.GET.get('neurodivergente__id__exact'):
            # Na página de PEIs do aluno
            return ['neurodivergente', 'get_mes_ano', 'get_metas', 'get_acoes']
        # Na página inicial
        return ['get_aluno_nome', 'get_idade_sexo', 'get_total_peis', 'get_ultimo_pei', 'get_view_button']

    def get_mes_ano(self, obj):
        """
        Retorna o mês/ano formatado.
        """
        return f"{obj.get_mes_display()}/{obj.ano}"
    get_mes_ano.short_description = 'Mês/Ano'
    get_mes_ano.admin_order_field = 'ano'

    def get_metas(self, obj):
        """
        Retorna as metas do PEI.
        """
        return ", ".join([meta.nome for meta in obj.metas.all()])
    get_metas.short_description = 'Metas/Habilidades'

    def get_view_button(self, obj):
        """
        Retorna o botão de visualização que leva para a lista de PEIs do aluno.
        """
        if not obj.neurodivergente:
            return ''
        
        url = f"{reverse('admin:neurodivergentes_monitoramento_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
        return format_html(
            '<a class="btn btn-info btn-sm" style="min-width: 100px;" href="{}"><i class="fas fa-eye me-1"></i> Ver PEIs</a>',
            url
        )
    get_view_button.short_description = 'Ver PEIs'

    def get_acoes(self, obj):
        """
        Retorna os botões de ação para a lista de PEIs do aluno.
        """
        editar_url = reverse('admin:neurodivergentes_monitoramento_change', args=[obj.id])
        imprimir_url = reverse('neurodivergentes:imprimir_pei', args=[obj.id])
        remover_url = reverse('admin:neurodivergentes_monitoramento_delete', args=[obj.id])
        
        return format_html(
            '<div class="btn-group">' 
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0" title="Editar"><i class="material-symbols-rounded opacity-10" style="font-size: 16px;">edit</i></a>' 
            '<button type="button" class="btn btn-outline-primary btn-sm mb-0 ms-2" onclick="window.open(\'{}\')" title="Imprimir">' 
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">print</i></button>' 
            '<a href="{}" class="btn btn-outline-danger btn-sm mb-0 ms-2" title="Remover"><i class="material-symbols-rounded opacity-10" style="font-size: 16px;">delete</i></a>' 
            '</div>',
            editar_url,
            imprimir_url,
            remover_url
        )
    get_acoes.short_description = 'Ações'

    def get_idade_sexo(self, obj):
        """
        Retorna a idade e gênero do aluno.
        """
        if not obj.neurodivergente:
            return '-'
        return format_html(
            '<div class="d-flex flex-column"><span class="text-sm font-weight-bold">{} anos</span><span class="text-xs text-secondary">{}</span></div>',
            obj.neurodivergente.idade(),
            'Masculino' if obj.neurodivergente.genero == 'M' else 'Feminino'
        )
    get_idade_sexo.short_description = 'Idade/Sexo'
    get_idade_sexo.admin_order_field = 'neurodivergente__data_nascimento'
    
    class Media:
        css = {
            'all': (
                'neurodivergentes/css/pei_forms.css',
                'neurodivergentes/css/pei_popup.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            )
        }
        js = (
            'admin/js/pei_admin.js',
            'admin/js/pei_popup.js',
        )

@admin.register(RegistroEvolucao)
class RegistroEvolucaoAdmin(admin.ModelAdmin):
    form = RegistroEvolucaoForm
    list_display = ['get_aluno_nome', 'get_total_evolucoes', 'get_ultima_evolucao', 'get_view_button']
    list_filter = ['neurodivergente']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome', 'descricao']
    list_per_page = 20

    def get_queryset(self, request):
        """
        Retorna apenas a evolução mais recente por aluno na lista inicial,
        ou todas as evoluções se um filtro de aluno estiver ativo.
        """
        self.request = request
        queryset = super().get_queryset(request).select_related(
            'neurodivergente', 'profissional'
        )

        neurodivergente_id = request.GET.get('neurodivergente__id__exact')
        if neurodivergente_id:
            # Lista todas as evoluções do aluno filtrado
            return queryset.filter(neurodivergente_id=neurodivergente_id).order_by('-data')

        # Lista inicial: retorna apenas a evolução mais recente por aluno
        from django.db.models import Max
        latest_evolucao_ids = queryset.values('neurodivergente').annotate(
            max_id=Max('id')
        ).values_list('max_id', flat=True)

        return queryset.filter(id__in=latest_evolucao_ids).order_by('neurodivergente__primeiro_nome')

    def get_object(self, request, object_id, from_field=None):
        """
        Personaliza a busca de objetos para garantir que qualquer evolução seja carregada,
        independentemente do queryset usado na exibição agrupada.
        """
        queryset = super().get_queryset(request)
        return get_object_or_404(RegistroEvolucao, pk=object_id)

    def get_aluno_nome(self, obj):
        """
        Gera o link correto para o nome do aluno:
        - Lista inicial: redireciona para a lista de evoluções do aluno.
        - Lista filtrada: redireciona para o detalhe da evolução.
        """
        if not obj.neurodivergente:
            return '-'

        if hasattr(self, 'request') and 'neurodivergente__id__exact' not in self.request.GET:
            # Link para a lista de evoluções do aluno
            url = f"{reverse('admin:neurodivergentes_registroevolucao_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
        else:
            # Link para o detalhe da evolução
            url = reverse('admin:neurodivergentes_registroevolucao_change', args=[obj.id])

        nome_completo = f"{obj.neurodivergente.primeiro_nome} {obj.neurodivergente.ultimo_nome}"
        return format_html(
            '<a href="{}" style="color: #447e9b; text-decoration: none;">{}</a>',
            url,
            nome_completo
        )
    get_aluno_nome.short_description = 'Aluno/Paciente'
    get_aluno_nome.admin_order_field = 'neurodivergente__primeiro_nome'

    def get_total_evolucoes(self, obj):
        """
        Retorna o total de evoluções do aluno.
        """
        if not obj.neurodivergente:
            return '0'
        return obj.neurodivergente.registros_evolucao.count()
    get_total_evolucoes.short_description = 'Total de Evoluções'

    def get_ultima_evolucao(self, obj):
        """
        Retorna a data da última evolução formatada.
        """
        if not obj.neurodivergente:
            return '-'
        ultima = obj.neurodivergente.registros_evolucao.order_by('-data').first()
        return ultima.data.strftime('%d/%m/%Y') if ultima else '-'
    get_ultima_evolucao.short_description = 'Última Evolução'

    def get_view_button(self, obj):
        """
        Retorna o botão de visualização que leva para a lista de evoluções do aluno.
        """
        if not obj.neurodivergente:
            return ''
        
        url = f"{reverse('admin:neurodivergentes_registroevolucao_changelist')}?neurodivergente__id__exact={obj.neurodivergente.id}"
        return format_html(
            '<a class="btn btn-info btn-sm" href="{}"><i class="fas fa-eye"></i> Ver Evoluções</a>',
            url
        )
    get_view_button.short_description = 'Ver Evoluções'

    def get_neurodivergente(self, obj):
        """
        Retorna o neurodivergente, mas com um nome de coluna personalizado
        """
        return obj.neurodivergente
    get_neurodivergente.short_description = 'Aluno/Paciente'
    
    def get_list_display(self, request):
        """
        Altera as colunas exibidas dependendo se estamos na lista inicial
        ou na lista de evoluções de um aluno.
        """
        if request.GET.get('neurodivergente__id__exact'):
            # Na página de evoluções do aluno
            return ['get_neurodivergente', 'get_data_formatada', 'profissional', 'tem_anexos', 'get_acoes']
        # Na página inicial
        return ['get_aluno_nome', 'get_total_evolucoes', 'get_ultima_evolucao', 'get_view_button']

    def get_data_formatada(self, obj):
        """
        Retorna a data no formato dd/mm/yy
        """
        return obj.data.strftime('%d/%m/%y')
    get_data_formatada.short_description = 'Data'
    get_data_formatada.admin_order_field = 'data'

    def tem_anexos(self, obj):
        return bool(obj.anexos)
    tem_anexos.boolean = True
    tem_anexos.short_description = 'Anexos'

    def get_acoes(self, obj):
        """
        Retorna os botões de ação para a lista de evoluções do aluno.
        """
        editar_url = reverse('admin:neurodivergentes_registroevolucao_change', args=[obj.id])
        
        # Construir URL para imprimir evolução
        imprimir_url = reverse('neurodivergentes:imprimir_evolucao', args=[obj.id])
        
        return format_html(
            '<div class="d-flex justify-content-center">'            
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0 me-2">'            
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">edit</i> Editar</a>'            
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0" target="_blank">'            
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">print</i> Imprimir</a>'            
            '</div>',
            editar_url, imprimir_url
        )
    get_acoes.short_description = 'Ações'

    def get_edit_button(self, obj):
        """
        Retorna o botão de edição para a lista de evoluções do aluno.
        """
        url = reverse('admin:neurodivergentes_registroevolucao_change', args=[obj.id])
        return format_html(
            '<a class="btn btn-info btn-sm" href="{}"><i class="fas fa-edit"></i> Editar</a>',
            url
        )
    get_edit_button.short_description = 'Editar'
    
    class Media:
        css = {
            'all': ('neurodivergentes/css/neurodivergentes_forms.css',)
        }
        js = (
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.mask.min.js',
            'js/neurodivergentes_admin.js',
        )

from django import forms



class ParecerAvaliativoAdminForm(forms.ModelForm):
    grafico_frequencia_base64 = forms.CharField(required=False, widget=forms.HiddenInput())
    grafico_monitoramento_base64 = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = ParecerAvaliativo
        fields = '__all__'
        widgets = {
            'neurodivergente': forms.Select(attrs={'class': 'vLargeTextField'}),
            'escola': forms.Select(attrs={'class': 'vLargeTextField'}),
            'data_avaliacao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'vDateField'
                },
                format='%Y-%m-%d'
            ),
            'evolucao': forms.Textarea(attrs={
                'rows': 4,
                'class': 'vLargeTextField',
                'placeholder': 'Descreva a evolução do aluno'
            }),
            'profissional_responsavel': forms.Select(attrs={'class': 'vLargeTextField'}),
            'anexos': forms.ClearableFileInput(attrs={'class': 'vFileUploadField'}),
            'grafico_data_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'vDateField',
                    'id': 'data_inicio'
                },
                format='%Y-%m-%d'
            ),
            'grafico_data_fim': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'vDateField',
                    'id': 'data_fim'
                },
                format='%Y-%m-%d'
            ),
            'grafico_frequencia': forms.HiddenInput(),
            'grafico_monitoramento': forms.HiddenInput()
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Garantir que os campos de data sejam processados corretamente
        if 'grafico_data_inicio' in self.data:
            try:
                instance.grafico_data_inicio = self.data['grafico_data_inicio']
            except (ValueError, TypeError):
                pass
                
        if 'grafico_data_fim' in self.data:
            try:
                instance.grafico_data_fim = self.data['grafico_data_fim']
            except (ValueError, TypeError):
                pass
        
        if commit:
            instance.save()
            
        return instance

@admin.register(ParecerAvaliativo)
class ParecerAvaliativoAdmin(admin.ModelAdmin):
    form = ParecerAvaliativoAdminForm
    list_display = ['get_aluno_nome', 'get_total_pareceres', 'get_ultimo_parecer', 'get_view_button']
    list_filter = ['neurodivergente']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']
    list_per_page = 20
    readonly_fields = ['idade', 'ver_graficos', 'grafico_frequencia', 'grafico_monitoramento']
    
    
    class Media:
        css = {
            'all': (
                'css/filtro_data.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            )
        }
        js = ('js/filtro_data.js',)

    def get_list_display(self, request):
        if 'neurodivergente__id__exact' in request.GET:
            # Visualização de pareceres do aluno específico
            return ['get_aluno_nome', 'get_profissional', 'get_data_parecer', 'tem_anexos', 'get_acoes']
        # Visualização agrupada por aluno
        return ['get_aluno_nome', 'get_total_pareceres', 'get_ultimo_parecer', 'get_view_button']
        
    def get_acoes(self, obj):
        if not obj.pk:
            return '-'
        
        # Botão de relatório individual
        url_relatorio = reverse('neurodivergentes:imprimir_parecer', args=[obj.pk])
        botao_individual = f'''
            <a href="{url_relatorio}" 
               target="_blank" 
               title="Gerar Relatório Individual"
               style="display: inline-block; 
                      padding: 6px 12px; 
                      background-color: #4e73df; 
                      color: white; 
                      border-radius: 4px; 
                      text-decoration: none; 
                      font-size: 13px;">
                <i class="fas fa-file-pdf" style="margin-right: 5px;"></i>
                Relatório Individual
            </a>
        '''
        
        return format_html(botao_individual)
    get_acoes.short_description = 'Ações'
    get_acoes.allow_tags = True
    
    def get_profissional(self, obj):
        return obj.profissional_responsavel or '-'
    get_profissional.short_description = 'Profissional Responsável'
    
    def get_data_parecer(self, obj):
        return obj.data_avaliacao.strftime('%d/%m/%Y') if obj.data_avaliacao else '-'
    get_data_parecer.short_description = 'Data do Parecer'
    
    fieldsets = [
        (None, {
            'fields': [
                'neurodivergente',
                'idade',
                'escola', 
                'data_avaliacao',
                'profissional_responsavel',
                'ver_graficos',
                'evolucao',
                'anexos'
            ]
        })
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if 'neurodivergente__id__exact' in request.GET:
            return queryset
        
        # Pega o último parecer de cada aluno usando uma abordagem mais simples
        from django.db.models import Max
        latest_dates = ParecerAvaliativo.objects.values('neurodivergente').annotate(
            max_data=Max('data_avaliacao')
        )
        
        latest_pareceres = []
        for item in latest_dates:
            parecer = ParecerAvaliativo.objects.filter(
                neurodivergente_id=item['neurodivergente'],
                data_avaliacao=item['max_data']
            ).first()
            if parecer:
                latest_pareceres.append(parecer.id)
        
        return queryset.filter(id__in=latest_pareceres).order_by('neurodivergente__primeiro_nome')

    def get_object(self, request, object_id, from_field=None):
        queryset = ParecerAvaliativo.objects.filter(pk=object_id)
        return queryset.get()

    def get_aluno_nome(self, obj):
        if 'neurodivergente__id__exact' in self.request.GET:
            return obj.neurodivergente.nome_completo
        url = f'{reverse("admin:neurodivergentes_pareceravaliativo_changelist")}?neurodivergente__id__exact={obj.neurodivergente.id}'
        return format_html('<a href="{}">{}</a>', url, obj.neurodivergente.nome_completo)
    get_aluno_nome.short_description = 'Aluno/Paciente'
    get_aluno_nome.admin_order_field = 'neurodivergente__primeiro_nome'

    def get_total_pareceres(self, obj):
        return ParecerAvaliativo.objects.filter(neurodivergente=obj.neurodivergente).count()
    get_total_pareceres.short_description = 'Total de Pareceres'

    def get_ultimo_parecer(self, obj):
        ultimo = ParecerAvaliativo.objects.filter(
            neurodivergente=obj.neurodivergente
        ).order_by('-data_avaliacao').first()
        return ultimo.data_avaliacao.strftime('%d/%m/%Y') if ultimo else '-'
    get_ultimo_parecer.short_description = 'Último Parecer'

    def save_model(self, request, obj, form, change):
        # Processamento de gráficos temporariamente desabilitado para melhorar performance
        super().save_model(request, obj, form, change)
    
    def get_view_button(self, obj):
        if 'neurodivergente__id__exact' in self.request.GET:
            return ''
        url = f'{reverse("admin:neurodivergentes_pareceravaliativo_changelist")}?neurodivergente__id__exact={obj.neurodivergente.id}'
        return format_html(
            '<a class="button" href="{}" style="white-space:nowrap;">' 
            '<i class="fas fa-eye"></i> Ver Pareceres</a>', 
            url
        )
        
        return format_html(''.join(botoes)) + format_html(
            '<a class="button" href="{}" style="white-space:nowrap;">' 
            '<i class="fas fa-eye"></i> Ver Pareceres</a>', 
            url
        )
    get_view_button.short_description = 'Ações'

    def changelist_view(self, request, extra_context=None):
        """
        Ajusta as colunas exibidas na listagem com base no contexto:
        - Lista inicial: exibe agrupamento.
        - Lista detalhada: exibe todos os pareceres do aluno.
        """
        self.request = request
        
        # Adiciona botão de relatório geral no topo se estiver na lista de pareceres de um aluno
        if 'neurodivergente__id__exact' in request.GET:
            neurodivergente_id = request.GET['neurodivergente__id__exact']
            url_relatorio_geral = reverse('neurodivergentes:gerar_relatorio_parecer_geral_pdf', args=[neurodivergente_id])
            
            # Botão de relatório geral
            botao_geral = f'''
                <a href="javascript:void(0);" 
                   onclick="FiltroData.abrirModalFiltroData('{url_relatorio_geral}');"
                   class="addlink"
                   style="margin-left: 5px;">
                    <i class="fas fa-file-alt" style="margin-right: 5px;"></i>
                    Relatório Geral
                </a>
            '''
            
            # Modal de filtro de data
            modal_filtro = '''
                <div id="modal-filtro-data" class="modal-filtro" style="display: none;">
                    <div class="modal-content">
                        <h2>Selecione o Período</h2>
                        <form id="form-filtro-data">
                            <div class="form-group">
                                <label for="data_inicial">Data Inicial:</label>
                                <input type="date" id="data_inicial" name="data_inicial" required>
                            </div>
                            <div class="form-group">
                                <label for="data_final">Data Final:</label>
                                <input type="date" id="data_final" name="data_final" required>
                            </div>
                            <div class="form-actions">
                                <button type="button" onclick="FiltroData.fecharModalFiltroData()" class="closelink">Cancelar</button>
                                <button type="button" onclick="FiltroData.gerarRelatorio()" class="default">Gerar Relatório</button>
                            </div>
                        </form>
                    </div>
                </div>
            '''
            
            if not extra_context:
                extra_context = {}
            
            extra_context['additional_buttons'] = format_html(botao_geral)
            extra_context['modal_filtro'] = format_html(modal_filtro)
        
        return super().changelist_view(request, extra_context)

    def ver_graficos(self, obj):
        if obj and obj.pk:
            return format_html(
                '<a class="button" href="{}" target="_blank" style="margin-bottom: 10px;">' 
                '<i class="fas fa-chart-bar"></i> Ver Gráficos</a>',
                reverse('neurodivergentes:parecer_graficos', args=[obj.pk])
            )
        return ''
    ver_graficos.short_description = ''
    
    def tem_anexos(self, obj):
        return bool(obj.anexos)
    tem_anexos.boolean = True
    tem_anexos.short_description = 'Anexos'

#@admin.register(HistoricoEscolar)
#class HistoricoEscolarAdmin(admin.ModelAdmin):
#    list_display = ['neurodivergente', 'escola_atual', 'serie_atual', 'modalidade_ensino']
#    list_filter = ['modalidade_ensino', 'serie_atual']
#    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']

@admin.register(Anamnese)
class AnamneseAdmin(admin.ModelAdmin):
    
    form = AnamneseForm
    list_display = ['neurodivergente', 'tipo_parto', 'prematuridade', 'tem_anexos', 'acoes']
    list_filter = ['tipo_parto', 'prematuridade']
    search_fields = ['neurodivergente__primeiro_nome', 'neurodivergente__ultimo_nome']
    formfield_overrides = {
        models.DateField: {'widget': forms.DateInput(attrs={'class': 'vDateField', 'type': 'date'})}
    }
    
    def tem_anexos(self, obj):
        if obj.anexos:
            return format_html('<i class="material-symbols-rounded text-danger opacity-10" style="font-size: 16px;">attach_file</i>')
        return ""
    tem_anexos.short_description = 'Anexos'
    
    def acoes(self, obj):
        imprimir_url = reverse('neurodivergentes:imprimir_anamnese', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank">Imprimir</a>',
            imprimir_url
        )
    acoes.short_description = 'Ações'
    
#@admin.register(PlanoEducacional)
#class PlanoEducacionalAdmin(admin.ModelAdmin):
#    form = PlanoEducacionalForm
#    list_display = ['pdi', 'data_inicio', 'data_fim', 'pedagogo_responsavel']
#    list_filter = ['data_inicio', 'pedagogo_responsavel']
#    search_fields = ['pdi__neurodivergente__primeiro_nome', 'pdi__neurodivergente__ultimo_nome']
#    inlines = [AdaptacaoCurricularInline]

#    fieldsets = (
#        ('Informações Básicas', {
#            'fields': ('pdi', 'pedagogo_responsavel', 'data_inicio', 'data_fim')
#        }),
#        ('Detalhes do Plano', {
#            'fields': ('objetivos', 'estrategias', 'recursos')
#        }),
#    )       'fields': ('objetivos', 'estrategias', 'recursos')
#        }),
#    )   }),
#    )       'fields': ('objetivos', 'estrategias', 'recursos')
#        }),
#    )   }),
#    )       'fields': ('objetivos', 'estrategias', 'recursos')
#        }),
#    )