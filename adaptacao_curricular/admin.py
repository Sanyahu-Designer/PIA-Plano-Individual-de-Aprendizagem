from django.contrib import admin
from django import forms
from django.urls import path, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from profissionais_app.models import Profissional
from .models import (
    BNCCDisciplina,
    BNCCHabilidade,
    AdaptacaoCurricularIndividualizada,
    AdaptacaoHabilidade
)

from django.forms.widgets import Select, Textarea
from django.utils.safestring import mark_safe

class LabelAboveWidget(Select):
    """Widget personalizado que renderiza o label acima do campo."""
    
    def __init__(self, attrs=None):
        # Garantir que attrs não seja None
        attrs = attrs or {}
        attrs['data-hide-label'] = 'true'  # Flag para identificar que o label deve ser removido
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Renderiza o select normalmente
        select_html = super().render(name, value, attrs, renderer)
        
        # Cria o HTML sem label
        html = f'''
        <div style="display: block; width: 100%;">
            <div style="display: block; width: 100%;">
                {select_html}
            </div>
        </div>
        '''
        
        return mark_safe(html)

class LabelAboveTextarea(Textarea):
    """Widget personalizado que renderiza o label acima do campo."""
    
    def render(self, name, value, attrs=None, renderer=None):
        # Renderiza o textarea normalmente
        textarea_html = super().render(name, value, attrs, renderer)
        
        # Obtém o label do campo
        label = self.attrs.get('label', name.replace('_', ' ').title())
        
        # Cria o HTML com o label acima do campo
        html = f'''
        <div style="display: block; width: 100%;">
            <div style="display: block; width: 100%; margin-bottom: 8px;">
                <label for="{attrs.get('id', '')}" style="display: block; width: 100%; text-align: left; font-weight: bold;">
                    {label}
                </label>
            </div>
            <div style="display: block; width: 100%;">
                {textarea_html}
            </div>
        </div>
        '''
        
        return mark_safe(html)

class AdaptacaoHabilidadeForm(forms.ModelForm):
    class Meta:
        model = AdaptacaoHabilidade
        fields = ('habilidade', 'descritivo_adaptacao')
        widgets = {
            'habilidade': LabelAboveWidget(attrs={
                'class': 'select2-habilidade',
                'data-placeholder': 'Digite o código ou palavras-chave da habilidade',
                'style': 'width: 100%; display: block;',
                'label': 'Buscar Habilidade',
            }),
            'descritivo_adaptacao': LabelAboveTextarea(attrs={
                'rows': 3,
                'placeholder': 'Descreva a adaptação curricular para esta habilidade',
                'style': 'width: 100%; display: block;',
                'label': 'Descritivo da Adaptação Curricular',
            }),
        }
        labels = {
            'habilidade': 'Buscar Habilidade',
            'descritivo_adaptacao': 'Descritivo da Adaptação Curricular',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configura o campo de habilidade
        self.fields['habilidade'].label = 'Buscar Habilidade'
        
        # Configura o queryset inicial
        self.fields['habilidade'].queryset = BNCCHabilidade.objects.all().select_related('disciplina')
        
    def clean(self):
        cleaned_data = super().clean()
        if 'habilidade' in cleaned_data:
            habilidade = cleaned_data['habilidade']
            if not habilidade:
                raise forms.ValidationError('Por favor, selecione uma habilidade.')
        return cleaned_data

class AdaptacaoCurricularIndividualizadaForm(forms.ModelForm):
    class Meta:
        model = AdaptacaoCurricularIndividualizada
        fields = '__all__'
        widgets = {
            'aluno': LabelAboveWidget(attrs={
                'class': 'select2-aluno',
                'data-placeholder': 'Selecione o Aluno/Paciente',
                'style': 'width: 100%; display: block;',
                'label': 'Aluno/Paciente',
            }),
            'escola': LabelAboveWidget(attrs={
                'class': 'select2-escola',
                'data-placeholder': 'Selecione a Escola',
                'style': 'width: 100%; display: block;',
                'label': 'Escola',
            }),
            'profissional_responsavel': LabelAboveWidget(attrs={
                'class': 'select2-profissional',
                'data-placeholder': 'Selecione o Profissional Responsável',
                'style': 'width: 100%; display: block;',
                'label': 'Profissional Responsável',
            }),
        }

class AdaptacaoHabilidadeInline(admin.StackedInline):
    model = AdaptacaoHabilidade
    form = AdaptacaoHabilidadeForm
    extra = 1
    fields = ('habilidade', 'descritivo_adaptacao')
    can_delete = True
    show_change_link = True
    classes = ('adaptacao-inline',)
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['habilidade'].widget.can_add_related = False
        formset.form.base_fields['habilidade'].widget.can_change_related = False
        return formset

@admin.register(BNCCDisciplina)
class BNCCDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    ordering = ['nome']
    change_list_template = 'admin/bncc/disciplinabncc/change_list_material_dashboard.html'
    change_form_template = 'admin/bncc/disciplinabncc/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remover o label "Nome"
        if form.base_fields['nome'].label == 'Nome':
            form.base_fields['nome'].label = ''
        return form

@admin.register(BNCCHabilidade)
class BNCCHabilidadeAdmin(admin.ModelAdmin):
    fields = ('codigo', 'disciplina', 'ano', 'trimestre', 'objeto_conhecimento', 'descricao')
    change_list_template = 'admin/bncc/codigobncc/change_list_material_dashboard.html'
    change_form_template = 'admin/bncc/codigobncc/change_form.html'
    
    list_filter = ('disciplina', 'ano', 'trimestre')
    search_fields = ('codigo', 'descricao', 'objeto_conhecimento')
    autocomplete_fields = ['disciplina']
    list_select_related = ['disciplina']
    list_display = ('codigo', 'disciplina', 'ano', 'trimestre', 'objeto_conhecimento')
    ordering = ['codigo']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remover o label "Disciplina"
        if form.base_fields['disciplina'].label == 'Disciplina':
            form.base_fields['disciplina'].label = ''
        form.base_fields['disciplina'].widget = LabelAboveWidget(attrs={
            'class': 'select2-disciplina',
            'data-placeholder': 'Selecione a disciplina BNCC',
            'style': 'width: 100%; display: block;',
        })
        return form

@admin.register(AdaptacaoCurricularIndividualizada)
class AdaptacaoCurricularIndividualizadaAdmin(admin.ModelAdmin):
    search_fields = ['aluno__primeiro_nome', 'aluno__ultimo_nome', 'escola__nome']

    inlines = [AdaptacaoHabilidadeInline]
    change_form_template = 'admin/adaptacao_curricular/adaptacaocurricularindividualizada/change_form.html'
    change_list_template = 'admin/adaptacao_curricular/adaptacaocurricularindividualizada/change_list_material_dashboard.html'
    list_display = ['get_aluno_nome', 'get_total_adaptacoes', 'get_ultima_adaptacao', 'get_acoes']
    list_filter = ['aluno', 'escola']
    list_per_page = 20
    
    form = AdaptacaoCurricularIndividualizadaForm
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_habilidade_details/', self.admin_site.admin_view(self.get_habilidade_details), name='get_habilidade_details'),
            path('buscar-habilidades/', self.admin_site.admin_view(self.buscar_habilidades), name='buscar_habilidades'),
        ]
        return custom_urls + urls
    
    def get_habilidade_details(self, request):
        """Endpoint para obter detalhes de uma habilidade pelo ID"""
        if not request.user.is_staff:
            raise PermissionDenied
            
        habilidade_id = request.GET.get('habilidade_id')
        if not habilidade_id:
            return JsonResponse({'error': 'ID da habilidade não fornecido'}, status=400)
            
        try:
            habilidade = BNCCHabilidade.objects.select_related('disciplina').get(id=habilidade_id)
            
            # Formata os dados para exibição
            ano_display = dict(BNCCHabilidade.ANOS_CHOICES).get(habilidade.ano, habilidade.ano)
            trimestre_display = dict(BNCCHabilidade.TRIMESTRE_CHOICES).get(habilidade.trimestre, habilidade.trimestre)
            
            data = {
                'codigo': habilidade.codigo,
                'disciplina': habilidade.disciplina.nome,
                'objeto_conhecimento': habilidade.objeto_conhecimento,
                'descricao': habilidade.descricao,
                'ano': ano_display,
                'trimestre': trimestre_display,
            }
            return JsonResponse(data)
        except BNCCHabilidade.DoesNotExist:
            return JsonResponse({'error': 'Habilidade não encontrada'}, status=404)

    def get_queryset(self, request):
        """
        Retorna apenas a adaptação mais recente por aluno na lista inicial,
        ou todas as adaptações se um filtro de aluno estiver ativo.
        """
        self.request = request
        queryset = super().get_queryset(request).select_related('aluno', 'escola')

        aluno_id = request.GET.get('aluno__id__exact')
        if aluno_id:
            # Lista todas as adaptações do aluno filtrado
            return queryset.filter(aluno_id=aluno_id).order_by('-data_cadastro')

        # Lista inicial: retorna apenas a adaptação mais recente por aluno
        latest_adaptacao_ids = queryset.values('aluno').annotate(
            max_id=models.Max('id')
        ).values_list('max_id', flat=True)

        return queryset.filter(id__in=latest_adaptacao_ids).order_by('aluno__primeiro_nome')
        
    def get_changelist(self, request, **kwargs):
        """
        Retorna uma classe ChangeList personalizada que adiciona contagens e datas às linhas
        """
        from django.contrib.admin.views.main import ChangeList
        
        class CustomChangeList(ChangeList):
            def get_results(self, *args, **kwargs):
                super().get_results(*args, **kwargs)
                
                # Adiciona contagens e datas para cada objeto na lista de resultados
                from adaptacao_curricular.models import AdaptacaoCurricularIndividualizada
                
                for obj in self.result_list:
                    # Adiciona a contagem de adaptações para este aluno
                    obj.total_adaptacoes = AdaptacaoCurricularIndividualizada.objects.filter(aluno=obj.aluno).count()
                    
                    # Adiciona a data da última adaptação para este aluno
                    ultima = AdaptacaoCurricularIndividualizada.objects.filter(
                        aluno=obj.aluno
                    ).order_by('-data_cadastro').first()
                    obj.ultima_adaptacao = ultima.data_cadastro if ultima else None
        
        return CustomChangeList

    def get_list_display(self, request):
        """
        Altera as colunas exibidas dependendo se estamos na lista inicial
        ou na lista de adaptações de um aluno.
        """
        if request.GET.get('aluno__id__exact'):
            # Lista de adaptações do aluno
            return ['get_aluno_nome', 'escola', 'get_data_cadastro', 'get_acoes']
        # Lista inicial
        return ['get_aluno_nome', 'get_total_adaptacoes', 'get_ultima_adaptacao', 'get_view_button']

    def get_aluno_nome(self, obj):
        """
        Retorna o nome do aluno.
        """
        if not obj.aluno:
            return '-'
        return f"{obj.aluno.primeiro_nome} {obj.aluno.ultimo_nome}"
    get_aluno_nome.short_description = 'Aluno'
    get_aluno_nome.admin_order_field = 'aluno__primeiro_nome'

    def get_total_adaptacoes(self, obj):
        """
        Retorna o total de adaptações do aluno.
        """
        if not obj.aluno:
            return '0'
        return AdaptacaoCurricularIndividualizada.objects.filter(aluno=obj.aluno).count()
    get_total_adaptacoes.short_description = 'Total de PEIs'

    def get_ultima_adaptacao(self, obj):
        """
        Retorna a data da última adaptação do aluno no formato dd/mm/aaaa.
        """
        if not obj.aluno:
            return '-'
        ultima = AdaptacaoCurricularIndividualizada.objects.filter(
            aluno=obj.aluno
        ).order_by('-data_cadastro').first()
        if ultima and ultima.data_cadastro:
            # Formata a data no padrão brasileiro dd/mm/aaaa
            return ultima.data_cadastro.strftime('%d/%m/%Y')
        return '-'
    get_ultima_adaptacao.short_description = 'Último PEI'
    get_ultima_adaptacao.admin_order_field = 'data_cadastro'

    def get_view_button(self, obj):
        """
        Retorna o botão de visualização que leva para a lista de adaptações do aluno.
        """
        if not obj.aluno:
            return '-'
        url = f"{reverse('admin:adaptacao_curricular_adaptacaocurricularindividualizada_changelist')}?aluno__id__exact={obj.aluno.id}"
        return format_html(
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0">' 
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">visibility</i> Ver PEIs</a>',
            url
        )
    get_view_button.short_description = 'Ver PEIs'

    def get_acoes(self, obj):
        """
        Retorna os botões de ação para a lista de adaptações do aluno.
        """
        edit_url = reverse('admin:adaptacao_curricular_adaptacaocurricularindividualizada_change', args=[obj.id])
        delete_url = reverse('admin:adaptacao_curricular_adaptacaocurricularindividualizada_delete', args=[obj.id])
        
        return format_html(
            '<div>' 
            '<a href="{}" class="btn btn-outline-primary btn-sm mb-0 me-2">' 
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">edit</i> Editar</a>' 
            '<a href="{}" class="btn btn-outline-danger btn-sm mb-0">' 
            '<i class="material-symbols-rounded opacity-10" style="font-size: 16px;">delete</i> Remover</a>' 
            '</div>',
            edit_url, delete_url
        )
    get_acoes.short_description = 'Ações'

    class Media:
        css = {
            'all': (
                'https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200',
            )
        }

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            # Importa o modelo BNCCDisciplina
            from .models import BNCCDisciplina
            
            # Busca todas as disciplinas disponíveis
            disciplinas = BNCCDisciplina.objects.all().order_by('nome')
            
            # Adiciona as disciplinas ao contexto
            extra_context['disciplinas'] = disciplinas
            
            # Mantém a lógica anterior para compatibilidade
            adaptacoes_por_disciplina = {}
            for adaptacao in obj.adaptacoes.select_related('habilidade__disciplina').all():
                disciplina = adaptacao.habilidade.disciplina
                if disciplina not in adaptacoes_por_disciplina:
                    adaptacoes_por_disciplina[disciplina] = []
                adaptacoes_por_disciplina[disciplina].append(adaptacao)
            
            # Cria os botões para cada disciplina
            disciplina_buttons = []
            
            # Se não houver adaptações, busca todas as disciplinas disponíveis
            if not adaptacoes_por_disciplina:
                # Verificar se há disciplinas disponíveis
                if disciplinas.exists():
                    for disciplina in disciplinas:
                        disciplina_buttons.append({
                            'nome': disciplina.nome,
                            'id': disciplina.id,
                            'url': reverse('adaptacao_curricular:imprimir_adaptacao_disciplina', 
                                          args=[obj.id, disciplina.id])
                        })
            else:
                # Usa as disciplinas que já têm adaptações
                for disciplina in adaptacoes_por_disciplina.keys():
                    disciplina_buttons.append({
                        'nome': disciplina.nome,
                        'id': disciplina.id,
                        'url': reverse('adaptacao_curricular:imprimir_adaptacao_disciplina', 
                                      args=[obj.id, disciplina.id])
                    })
            
            extra_context['disciplina_buttons'] = disciplina_buttons
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def buscar_habilidades(self, request):
        """Endpoint para buscar habilidades baseado no termo de busca."""
        if not request.user.is_staff:
            raise PermissionDenied
            
        term = request.GET.get('term', '')
        print(f'Termo de busca recebido: {term}')
        
        try:
            # Primeiro tenta buscar por ID
            if term.isdigit():
                habilidade = BNCCHabilidade.objects.select_related('disciplina').filter(id=term).first()
                if habilidade:
                    results = [{
                        'id': habilidade.id,
                        'codigo': habilidade.codigo,
                        'disciplina': habilidade.disciplina.nome if habilidade.disciplina else '',
                        'ano': habilidade.get_ano_display() if hasattr(habilidade, 'get_ano_display') else str(habilidade.ano),
                        'trimestre': habilidade.get_trimestre_display() if hasattr(habilidade, 'get_trimestre_display') else str(habilidade.trimestre),
                        'objeto_conhecimento': habilidade.objeto_conhecimento,
                        'descricao': habilidade.descricao,
                        'text': habilidade.codigo  # Campo obrigatório para o Select2
                    }]
                    return JsonResponse({'results': results})
            
            # Se não for ID ou não encontrar, busca por outros campos
            habilidades = BNCCHabilidade.objects.select_related('disciplina').filter(
                models.Q(codigo__icontains=term) |
                models.Q(objeto_conhecimento__icontains=term) |
                models.Q(descricao__icontains=term) |
                models.Q(ano__icontains=term) |
                models.Q(trimestre__icontains=term) |
                models.Q(disciplina__nome__icontains=term)
            ).order_by('disciplina__nome', 'ano', 'trimestre', 'codigo')[:20]  # Limita a 20 resultados
            
            print(f'Habilidades encontradas: {habilidades.count()}')
            
            results = [{
                'id': h.id,
                'codigo': h.codigo,
                'disciplina': h.disciplina.nome if h.disciplina else '',
                'ano': h.get_ano_display() if hasattr(h, 'get_ano_display') else str(h.ano),
                'trimestre': h.get_trimestre_display() if hasattr(h, 'get_trimestre_display') else str(h.trimestre),
                'objeto_conhecimento': h.objeto_conhecimento,
                'descricao': h.descricao,
                'text': h.codigo  # Campo obrigatório para o Select2
            } for h in habilidades]
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f'Erro ao buscar habilidades: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

    def get_anos(self, request, disciplina_id):
        anos = BNCCHabilidade.objects.filter(
            disciplina_id=disciplina_id
        ).values_list('ano', flat=True).distinct().order_by('ano')
        anos_list = [{'id': ano, 'text': dict(BNCCHabilidade.ANOS_CHOICES)[ano]} for ano in anos]
        return JsonResponse(anos_list, safe=False)

    def get_trimestres(self, request, disciplina_id, ano):
        trimestres = BNCCHabilidade.objects.filter(
            disciplina_id=disciplina_id,
            ano=ano
        ).values_list('trimestre', flat=True).distinct().order_by('trimestre')
        trimestres_list = [{'id': tri, 'text': dict(BNCCHabilidade.TRIMESTRE_CHOICES)[tri]} for tri in trimestres]
        return JsonResponse(trimestres_list, safe=False)

    def get_habilidades(self, request, disciplina_id, ano, trimestre):
        habilidades = BNCCHabilidade.objects.filter(
            disciplina_id=disciplina_id,
            ano=ano,
            trimestre=trimestre
        ).values('id', 'codigo', 'objeto_conhecimento', 'descricao')
        return JsonResponse(list(habilidades), safe=False)

    fieldsets = [
        ('Informações do Aluno', {
            'fields': ['aluno', 'escola', 'modalidade_ensino', 'ano', 'trimestre', 'profissional_responsavel']
        }),
    ]
    list_display = ('aluno', 'escola', 'profissional_responsavel', 'get_data_cadastro')
    
    def get_data_cadastro(self, obj):
        """
        Retorna a data de cadastro formatada no padrão brasileiro dd/mm/aaaa.
        """
        if obj.data_cadastro:
            return obj.data_cadastro.strftime('%d/%m/%Y')
        return '-'
    get_data_cadastro.short_description = 'Data do Cadastro'
    get_data_cadastro.admin_order_field = 'data_cadastro'
    list_filter = ('escola', 'data_cadastro')
    search_fields = (
        'aluno__primeiro_nome',
        'aluno__ultimo_nome',
        'escola__nome',
        'profissional_responsavel__nome'
    )
    autocomplete_fields = ['aluno', 'escola', 'profissional_responsavel']
    inlines = [AdaptacaoHabilidadeInline]
    
    class Media:
        css = {
            'all': (
                'admin/css/forms.css',
                'admin/css/widgets.css',
                'admin/css/vendor/select2/select2.min.css',
                'admin/css/autocomplete.css',
                'adaptacao_curricular/css/adaptacao.css',
            )
        }
        js = (
            'admin/js/vendor/select2/select2.full.min.js',
            'admin/js/vendor/select2/i18n/pt-BR.js',
            'admin/js/jquery.init.js',
            'admin/js/autocomplete.js',
            'adaptacao_curricular/js/adaptacao.js',
        )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Garante que o campo 'trimestre' sempre tenha o label correto
        if 'trimestre' in form.base_fields:
            form.base_fields['trimestre'].label = 'Trimestre/Bimestre'
        if not obj:  # Se é um novo objeto
            try:
                profissional = Profissional.objects.get(user=request.user)
                form.base_fields['profissional_responsavel'].initial = profissional
            except Profissional.DoesNotExist:
                pass
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            try:
                profissional = Profissional.objects.get(user=request.user)
                if not obj.profissional_responsavel:
                    obj.profissional_responsavel = profissional
            except Profissional.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        """
        Redireciona para a lista de PDIs do aluno após adicionar um novo PDI.
        """
        if obj and obj.aluno:
            # Redireciona para a lista de PDIs do aluno específico
            redirect_url = f"{reverse('admin:adaptacao_curricular_adaptacaocurricularindividualizada_changelist')}?aluno__id__exact={obj.aluno.id}"
            return HttpResponseRedirect(redirect_url)
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """
        Redireciona para a lista de PDIs do aluno após editar um PDI.
        """
        if obj and obj.aluno:
            # Redireciona para a lista de PDIs do aluno específico
            redirect_url = f"{reverse('admin:adaptacao_curricular_adaptacaocurricularindividualizada_changelist')}?aluno__id__exact={obj.aluno.id}"
            return HttpResponseRedirect(redirect_url)
        return super().response_change(request, obj)
