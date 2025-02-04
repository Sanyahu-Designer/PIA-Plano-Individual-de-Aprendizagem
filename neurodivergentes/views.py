from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, Max, F
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET
from django.conf import settings
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import json
import os
from .models import (
    Neurodivergente, PDI, PlanoEducacional, RegistroEvolucao,
    Monitoramento, ParecerAvaliativo, CondicaoNeurodivergente,
    Escola, Neurodivergencia, PDIMetaHabilidade, DiagnosticoNeurodivergente
)
from django.db.models import Prefetch
from django.http import HttpResponse
from django.template import Template, Context
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
import weasyprint
import platform
import sys
import traceback
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)

def calculate_progresso_total(pdi):
    """Calcula o progresso total do PDI"""
    metas = pdi.metas_habilidades.all()
    if not metas:
        return 0
    return int(sum(meta.progresso for meta in metas) / len(metas))

@login_required
def pdi_popup_view(request, pdi_id):
    pdi = get_object_or_404(
        PDI.objects.select_related(
            'neurodivergente',
            'pedagogo_responsavel'
        ).prefetch_related(
            'metas_habilidades__meta_habilidade'
        ),
        id=pdi_id
    )
    
    # Calcula o progresso usando a função auxiliar
    progresso = calculate_progresso_total(pdi)
    
    context = {
        'pdi': pdi,
        'progresso': progresso,
    }
    
    return render(request, 'admin/neurodivergentes/pdi/popup_view.html', context)

@login_required
def imprimir_pdi(request, pdi_id):
    # Busca o PDI com todos os relacionamentos necessários
    pdi = get_object_or_404(PDI.objects.select_related(
        'neurodivergente',
        'pedagogo_responsavel'
    ).prefetch_related(
        'metas_habilidades__meta_habilidade'
    ), id=pdi_id)
    
    # Prepara o contexto com todos os dados necessários
    context = {
        'pdi': pdi,
        'data_impressao': timezone.now(),
        'metas': pdi.metas_habilidades.all().select_related('meta_habilidade'),
        'progresso_total': calculate_progresso_total(pdi)
    }
    
    # Configura as fontes
    font_config = FontConfiguration()
    css_string = """
        @font-face {
            font-family: 'Roboto';
            src: url('%s') format('truetype');
            font-weight: normal;
        }
        @font-face {
            font-family: 'Roboto';
            src: url('%s') format('truetype');
            font-weight: bold;
        }
    """ % (
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
    )
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/pdi_print.html', context)
    
    # Cria o PDF com as configurações de fonte
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    css = CSS(string=css_string, font_config=font_config)
    pdf = html.write_pdf(
        stylesheets=[css],
        font_config=font_config,
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=pdi_{pdi.id}.pdf'
    
    return response

@login_required
def imprimir_pdis_aluno(request, aluno_id):
    neurodivergente = get_object_or_404(Neurodivergente, id=aluno_id)
    
    # Filtros de data
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    pdis = PDI.objects.filter(neurodivergente=neurodivergente)
    
    if date_from:
        pdis = pdis.filter(data_criacao__gte=datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        pdis = pdis.filter(data_criacao__lte=datetime.strptime(date_to, '%Y-%m-%d'))
    
    context = {
        'neurodivergente': neurodivergente,
        'pdis': pdis,
        'data_impressao': timezone.now()
    }
    
    html_string = render_to_string('neurodivergentes/relatorio_pdis.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=pdis_{neurodivergente.id}.pdf'
    
    return response

@login_required
def gerar_relatorio_pdf(request, neurodivergente_id):
    # Obtém as datas do filtro
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    
    if not data_inicial or not data_final:
        messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
        return redirect('neurodivergentes:lista_pdis', neurodivergente_id=neurodivergente_id)
    
    # Converte as datas para o formato brasileiro
    data_inicial_formatada = datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y')
    data_final_formatada = datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
    
    neurodivergente = get_object_or_404(
        Neurodivergente.objects.prefetch_related(
            'neurodivergencias',
            Prefetch(
                'neurodivergencias__diagnosticos',
                queryset=DiagnosticoNeurodivergente.objects.select_related('condicao')
            ),
            'pdis__metas_habilidades__meta_habilidade',
            'pdis__pedagogo_responsavel'
        ),
        id=neurodivergente_id
    )
    
    # Converte as datas para datetime
    data_inicial_dt = datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
    data_final_dt = datetime.strptime(data_final, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
    
    # Busca direta na tabela PDIMetaHabilidade com mais detalhes
    metas_query = PDIMetaHabilidade.objects.raw("""
        SELECT 
            pm.id, 
            pm.progresso, 
            p.data_criacao, 
            m.nome as meta_nome, 
            m.descricao as meta_descricao,
            pm.meta_habilidade_id
        FROM neurodivergentes_pdimetahabilidade pm
        INNER JOIN neurodivergentes_pdi p ON pm.pdi_id = p.id
        INNER JOIN neurodivergentes_metahabilidade m ON pm.meta_habilidade_id = m.id
        WHERE p.neurodivergente_id = %s
        AND p.data_criacao BETWEEN %s AND %s
        AND p.status = 'concluido'  -- Apenas PDIs Concluídos
        ORDER BY p.data_criacao, m.nome
    """, [neurodivergente.id, data_inicial_dt, data_final_dt])
    
    # Estrutura os dados
    metas_habilidades = {}
    datas_unicas = set()
    
    # Processa os resultados
    for meta in metas_query:
        # Converte para date se for datetime, senão usa como está
        data = meta.data_criacao.date() if isinstance(meta.data_criacao, datetime) else meta.data_criacao
        
        datas_unicas.add(data)
        
        if meta.meta_nome not in metas_habilidades:
            metas_habilidades[meta.meta_nome] = []
        
        # Adiciona o progresso para esta data no formato correto
        metas_habilidades[meta.meta_nome].append({
            'pdi_data': data,
            'progresso': meta.progresso
        })
    
    # Ordena as datas
    datas_unicas = sorted(list(datas_unicas))
    
    # Preenche os valores faltantes com '-'
    for meta_nome in metas_habilidades:
        # Cria um dicionário de progressos por data
        progresso_por_data = {prog['pdi_data']: prog['progresso'] for prog in metas_habilidades[meta_nome]}
        
        # Atualiza a lista de progressos para incluir todas as datas
        metas_habilidades[meta_nome] = [
            {
                'pdi_data': data, 
                'progresso': progresso_por_data.get(data, '-')
            } 
            for data in datas_unicas
        ]
    
    # Prepara datas_metas para o template
    datas_metas = [{'data': data} for data in datas_unicas]
    
    # Converte o formato de metas_habilidades para ser compatível com o template
    metas_habilidades_template = {}
    for meta_nome, progressos in metas_habilidades.items():
        metas_habilidades_template[meta_nome] = progressos
    
    # Busca PDIs no período com todos os relacionamentos
    try:
        pdis = PDI.objects.filter(
            neurodivergente=neurodivergente,
            data_criacao__range=(data_inicial_dt, data_final_dt),
            status='concluido'
        ).prefetch_related(
            'metas_habilidades',
            'metas_habilidades__meta_habilidade',
            'pedagogo_responsavel'
        ).order_by('data_criacao')
        
        # Log detalhado dos PDIs
        logger.info(f"PDIs encontrados: {pdis.count()}")
        for pdi in pdis:
            # Converte data_criacao para date se for datetime
            data = pdi.data_criacao.date() if isinstance(pdi.data_criacao, datetime) else pdi.data_criacao
            
            logger.info(f"PDI - Data: {data}, Status: {pdi.status}")
            for meta in pdi.metas_habilidades.all():
                logger.info(f"  Meta: {meta.meta_habilidade.nome}, Progresso: {meta.progresso}")
        
    except Exception as pdis_error:
        logger.error(f"Erro ao buscar PDIs: {str(pdis_error)}")
        messages.error(request, 'Erro ao buscar PDIs do aluno.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_pdi_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
    
    pdis_list = list(pdis)
    
    # Obtém o primeiro PDI para pegar o pedagogo responsável
    primeiro_pdi = pdis.first()
    if primeiro_pdi:
        pedagogo = primeiro_pdi.pedagogo_responsavel
        # Log detalhado
        logger.info(f"Primeiro PDI: {primeiro_pdi}")
        logger.info(f"Pedagogo do PDI: {pedagogo}")
        
        if pedagogo:
            # Verifica os campos do pedagogo
            logger.info(f"Campos do pedagogo: {pedagogo.__dict__}")
            
            # Busca a escola do pedagogo
            if pedagogo:
                # Busca a escola onde o pedagogo está associado
                escola = Escola.objects.filter(profissionais_educacao__id=pedagogo.id).first()
            else:
                escola = None
        else:
            escola = None
    else:
        pedagogo = None
        escola = None
    
    # Busca neurodivergências e diagnósticos
    try:
        neurodivergencias = Neurodivergencia.objects.filter(
            neurodivergente=neurodivergente
        ).prefetch_related('diagnosticos__condicao')
        logger.info(f"Neurodivergências encontradas: {neurodivergencias.count()}")
    except Exception as neurodiv_error:
        logger.error(f"Erro ao buscar neurodivergências: {str(neurodiv_error)}")
        neurodivergencias = []
    
    # Busca diagnósticos
    try:
        diagnosticos = DiagnosticoNeurodivergente.objects.filter(
            neurodivergencia__neurodivergente=neurodivergente
        ).select_related('condicao')
        logger.info(f"Diagnósticos encontrados: {diagnosticos.count()}")
    except Exception as diag_error:
        logger.error(f"Erro ao buscar diagnósticos: {str(diag_error)}")
        diagnosticos = []
    
    # Busca metas e habilidades dos PDIs
    metas_habilidades = {}
    datas_unicas = set()
    for pdi in pdis:
        data = pdi.data_criacao.date() if isinstance(pdi.data_criacao, datetime) else pdi.data_criacao
        datas_unicas.add(data)
        for meta_pdi in pdi.metas_habilidades.all():
            meta_nome = meta_pdi.meta_habilidade.nome
            
            if meta_nome not in metas_habilidades:
                metas_habilidades[meta_nome] = []
            metas_habilidades[meta_nome].append({
                'pdi_data': data,
                'progresso': meta_pdi.progresso
            })
    
    # Ordena as datas
    datas_unicas = sorted(list(datas_unicas))
    
    # Log para diagnóstico
    logger.info("Metas e Habilidades:")
    for meta, progressos in metas_habilidades.items():
        logger.info(f"Meta: {meta}")
        for prog in progressos:
            logger.info(f"  Data: {prog['pdi_data']}, Progresso: {prog['progresso']}")
    
    logger.info("Datas Únicas:")
    for data in datas_unicas:
        logger.info(f"  {data}")
    
    # Prepara datas_metas para o template
    datas_metas = [{'data': data} for data in datas_unicas]
    
    # Preenche valores faltantes
    for meta_nome in metas_habilidades:
        # Cria um dicionário de progressos por data
        progresso_por_data = {prog['pdi_data']: prog['progresso'] for prog in metas_habilidades[meta_nome]}
        
        # Atualiza a lista de progressos para incluir todas as datas
        metas_habilidades[meta_nome] = [
            {
                'pdi_data': data, 
                'progresso': progresso_por_data.get(data, '-')
            } 
            for data in datas_unicas
        ]
    
    # Prepara contexto com todos os dados
    context = {
        'neurodivergente': neurodivergente,
        'neurodivergencias': neurodivergencias,
        'pdis_list': pdis_list,
        'metas_habilidades': metas_habilidades_template,
        'diagnosticos': diagnosticos,
        'datas_pdis': datas_unicas,
        'datas_metas': datas_metas,
        'total_alunos': len(pdis_list),
        'total_pdis': len(pdis_list),
        'total_evolucoes': len(pdis_list),
        'frequencia_media': len(pdis_list),  # Adicionando a frequência
        'periodo': {
            'inicio': datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y'),
            'fim': datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
        },
        'pedagogo': pedagogo,
        'escola': escola
    }
    
    html_string = render_to_string('neurodivergentes/relatorio_geral_aluno.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=relatorio_{neurodivergente.primeiro_nome}_{neurodivergente.ultimo_nome}.pdf'
    
    return response

@login_required
def gerar_relatorio_geral_html(request, neurodivergente_id):
    try:
        # Obtém as datas do filtro
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        logger.info(f"Parâmetros recebidos - data_inicial: {data_inicial}, data_final: {data_final}, neurodivergente_id: {neurodivergente_id}")
        
        if not data_inicial or not data_final:
            logger.info("Datas não fornecidas")
            messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_pdi_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Log para rastrear chamadas em produção
        logger.info(f"Gerando relatório HTML para neurodivergente {neurodivergente_id} - Período: {data_inicial} a {data_final}")
        
        # Converte as datas para datetime
        try:
            data_inicial_dt = datetime.strptime(data_inicial + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            data_final_dt = datetime.strptime(data_final + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        except Exception as date_error:
            logger.error(f"Erro ao converter datas: {str(date_error)}")
            messages.error(request, 'Formato de data inválido.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_pdi_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Busca o neurodivergente com prefetch para otimizar
        try:
            neurodivergente = get_object_or_404(
                Neurodivergente.objects.prefetch_related(
                    'neurodivergencias',
                    Prefetch(
                        'neurodivergencias__diagnosticos',
                        queryset=DiagnosticoNeurodivergente.objects.select_related('condicao')
                    ),
                    'pdis__metas_habilidades__meta_habilidade',
                    'pdis__pedagogo_responsavel'
                ),
                id=neurodivergente_id
            )
        except Exception as neurodiv_error:
            logger.error(f"Erro ao buscar neurodivergente: {str(neurodiv_error)}")
            messages.error(request, 'Erro ao encontrar informações do aluno.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_pdi_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Busca direta na tabela PDIMetaHabilidade
        metas_query = PDIMetaHabilidade.objects.raw("""
            SELECT pm.*, p.data_criacao, m.nome as meta_nome
            FROM neurodivergentes_pdimetahabilidade pm
            INNER JOIN neurodivergentes_pdi p ON pm.pdi_id = p.id
            INNER JOIN neurodivergentes_metahabilidade m ON pm.meta_habilidade_id = m.id
            WHERE p.neurodivergente_id = %s
            AND p.data_criacao BETWEEN %s AND %s
            AND p.status = 'concluido'  -- Apenas PDIs Concluídos
            ORDER BY p.data_criacao, m.nome
        """, [neurodivergente_id, data_inicial_dt, data_final_dt])
        
        # Estrutura os dados
        metas_habilidades = {}
        datas_unicas = set()
        
        # Processa os resultados
        for meta in metas_query:
            logger.info(f"Tipo de data_criacao: {type(meta.data_criacao)}")
            logger.info(f"Valor de data_criacao: {meta.data_criacao}")
            
            # Converte para date se for datetime, senão usa como está
            data = meta.data_criacao.date() if isinstance(meta.data_criacao, datetime) else meta.data_criacao
            
            datas_unicas.add(data)
            
            if meta.meta_nome not in metas_habilidades:
                metas_habilidades[meta.meta_nome] = []
            
            metas_habilidades[meta.meta_nome].append({
                'pdi_data': data,
                'progresso': meta.progresso
            })
        
        # Ordena as datas
        datas_unicas = sorted(list(datas_unicas))
        
        # Preenche os valores faltantes com '-'
        for meta_nome in metas_habilidades:
            # Cria um dicionário de progressos por data
            progresso_por_data = {prog['pdi_data']: prog['progresso'] for prog in metas_habilidades[meta_nome]}
            
            # Atualiza a lista de progressos para incluir todas as datas
            metas_habilidades[meta_nome] = [
                {
                    'pdi_data': data, 
                    'progresso': progresso_por_data.get(data, '-')
                } 
                for data in datas_unicas
            ]
        
        # Prepara datas_metas para o template
        datas_metas = [{'data': data} for data in datas_unicas]
        
        # Converte o formato de metas_habilidades para ser compatível com o template
        metas_habilidades_template = {}
        for meta_nome, progressos in metas_habilidades.items():
            metas_habilidades_template[meta_nome] = progressos
        
        # Busca PDIs no período
        pdis = PDI.objects.filter(
            neurodivergente=neurodivergente,
            data_criacao__range=(data_inicial_dt, data_final_dt),
            status='concluido'
        ).prefetch_related(
            'metas_habilidades',
            'metas_habilidades__meta_habilidade',
            'pedagogo_responsavel'
        ).order_by('data_criacao')
        
        # Busca neurodivergências e diagnósticos
        try:
            neurodivergencias = Neurodivergencia.objects.filter(
                neurodivergente=neurodivergente
            ).prefetch_related('diagnosticos__condicao')
            logger.info(f"Neurodivergências encontradas: {neurodivergencias.count()}")
        except Exception as neurodiv_error:
            logger.error(f"Erro ao buscar neurodivergências: {str(neurodiv_error)}")
            neurodivergencias = []
        
        # Busca diagnósticos
        try:
            diagnosticos = DiagnosticoNeurodivergente.objects.filter(
                neurodivergencia__neurodivergente=neurodivergente
            ).select_related('condicao')
            logger.info(f"Diagnósticos encontrados: {diagnosticos.count()}")
        except Exception as diag_error:
            logger.error(f"Erro ao buscar diagnósticos: {str(diag_error)}")
            diagnosticos = []
        
        # Busca o pedagogo e escola mais recente
        pedagogo = None
        escola = None
        frequencia_media = 0
        
        if pdis:
            # Pega o pedagogo do último PDI
            pedagogo = pdis.last().pedagogo_responsavel if pdis.last().pedagogo_responsavel else None
            
            # Pega a escola do pedagogo
            if pedagogo:
                escola = Escola.objects.filter(profissionais_educacao__id=pedagogo.id).first()
            
            # Calcula frequência média
            frequencia_media = pdis.count()
        
        # Prepara contexto com todos os dados
        context = {
            'neurodivergente': neurodivergente,
            'neurodivergencias': neurodivergencias,
            'pdis_list': list(pdis),
            'metas_habilidades': metas_habilidades_template,
            'diagnosticos': diagnosticos,
            'periodo': {
                'inicio': datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fim': datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
            },
            'total_pdis': pdis.count(),
            'pedagogo': pedagogo,
            'escola': escola,
            'frequencia_media': frequencia_media,
            'datas_metas': datas_metas
        }
        
        # Log de diagnóstico
        logger.info(f"Dados do relatório - PDIs: {pdis.count()}, Metas: {len(metas_habilidades)}")
        
        return render(request, 'neurodivergentes/relatorio_geral_html.html', context)
    
    except Exception as e:
        # Log de erro detalhado
        logger.error(f"Erro inesperado ao gerar relatório HTML: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao gerar relatório: {str(e)}')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_pdi_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')

@login_required
def grafico_evolucao(request, neurodivergente_id):
    neurodivergente = get_object_or_404(Neurodivergente, id=neurodivergente_id)
    
    # Dados para o gráfico de dispersão (evolução)
    monitoramentos = Monitoramento.objects.filter(
        neurodivergente=neurodivergente
    ).order_by('data')
    
    datas = [m.data for m in monitoramentos]
    niveis = [m.nivel for m in monitoramentos]
    metas = [m.meta for m in monitoramentos]
    
    # Criar subplots
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=(
            'Evolução do Desenvolvimento',
        )
    )
    
    # Adicionar gráfico de dispersão
    fig.add_trace(
        go.Scatter(
            x=datas,
            y=niveis,
            mode='lines+markers',
            name='Nível de Desenvolvimento',
            text=metas,
            hovertemplate='%{text}<br>Nível: %{y}%<br>Data: %{x}'
        ),
        row=1, col=1
    )
    
    # Atualizar layout
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text=f'Evolução de {neurodivergente}',
        title_x=0.5
    )
    
    # Atualizar eixos
    fig.update_yaxes(title_text='Nível (%)', row=1, col=1)
    
    # Converter para JSON
    grafico_json = fig.to_json()
    
    return JsonResponse({'grafico': grafico_json})

@login_required
@require_GET
def get_condicoes(request):
    """Retorna as condições neurodivergentes de uma categoria específica."""
    categoria_id = request.GET.get('categoria_id')
    if not categoria_id:
        return JsonResponse({'error': 'Categoria não especificada'}, status=400)
    
    try:
        condicoes = CondicaoNeurodivergente.objects.filter(
            categoria_id=categoria_id
        ).values('id', 'nome', 'cid_10')
        
        return JsonResponse({
            'condicoes': list(condicoes)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def teste_pdf_view(request):
    try:
        import os
        import sys
        import traceback
        import platform
        import weasyprint
        
        html_string = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    h1 { color: blue; }
                    pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Diagnóstico de Geração de PDF</h1>
                <p>Este é um teste detalhado de geração de PDF com WeasyPrint.</p>
                
                <h2>Informações do Sistema</h2>
                <pre>
Data e Hora do Teste: {{ data_hora }}
Python Version: {{ python_version }}
Python Executable: {{ python_executable }}
Python Path: {{ python_path }}

Versões de Bibliotecas:
- WeasyPrint: {{ weasyprint_version }}
- Cairo: {{ cairo_version }}
- Pango: {{ pango_version }}

Variáveis de Ambiente Relevantes:
{% for key, value in env_vars.items %}
{{ key }}: {{ value }}
{% endfor %}
                </pre>

                <h2>Verificação de Dependências</h2>
                <pre>
Dependências Instaladas:
{{ installed_dependencies }}
                </pre>
            </body>
        </html>
        """
        
        from django.template import Template, Context
        from datetime import datetime
        from django.http import HttpResponse
        from weasyprint import HTML
        
        # Tentativa de importar versões de bibliotecas
        try:
            from weasyprint import __version__ as weasyprint_version
        except ImportError:
            weasyprint_version = "Não disponível"
        
        try:
            import cairo
            cairo_version = cairo.version
        except ImportError:
            cairo_version = "Não disponível"
        
        try:
            import pango
            pango_version = pango.version
        except ImportError:
            pango_version = "Não disponível"
        
        # Listar variáveis de ambiente relevantes
        env_vars = {
            key: value for key, value in os.environ.items() 
            if any(substr in key.lower() for substr in ['python', 'path', 'lib', 'ld', 'django'])
        }
        
        # Tentar listar dependências instaladas
        try:
            import pkg_resources
            installed_dependencies = "\n".join([
                f"{dist.key}=={dist.version}" 
                for dist in pkg_resources.working_set
                if dist.key in ['weasyprint', 'django', 'cairo', 'pango', 'pillow', 'reportlab']
            ])
        except ImportError:
            installed_dependencies = "Não foi possível listar dependências"
        
        template = Template(html_string)
        context = Context({
            'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'python_version': platform.python_version(),
            'python_executable': sys.executable,
            'python_path': "\n".join(sys.path),
            'weasyprint_version': weasyprint_version,
            'cairo_version': cairo_version,
            'pango_version': pango_version,
            'env_vars': env_vars,
            'installed_dependencies': installed_dependencies
        })
        
        rendered_html = template.render(context)
        
        html = HTML(string=rendered_html)
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="diagnostico_pdf.pdf"'
        return response
    
    except Exception as e:
        error_details = traceback.format_exc()
        
        return HttpResponse(f"""
        Erro na geração do PDF:
        
        Tipo de Erro: {type(e).__name__}
        Mensagem de Erro: {str(e)}
        
        Detalhes do Traceback:
        {error_details}
        
        Informações do Sistema:
        Python Version: {platform.python_version()}
        Caminho do Python: {sys.executable}
        Caminho do Interpretador: {sys.path}
        """, content_type='text/plain', status=500)