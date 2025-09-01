import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from weasyprint import HTML, CSS
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from weasyprint import HTML, CSS
from django.conf import settings
from django.core.paginator import Paginator
import os
from .models import Neurodivergente, Monitoramento, PDI, PDIMetaHabilidade, evolucao, pei
import logging

logger = logging.getLogger(__name__)
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
    Escola, Neurodivergencia, PDIMetaHabilidade, DiagnosticoNeurodivergente,
    Anamnese
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

from configuracoes.models import ConfiguracaoCliente

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
    
    # Buscar dados institucionais para o cabeçalho
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None
    
    # Prepara o contexto com todos os dados necessários
    context = {
        'pdi': pdi,
        'data_impressao': timezone.now(),
        'metas': pdi.metas_habilidades.all().select_related('meta_habilidade'),
        'progresso_total': calculate_progresso_total(pdi),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura as fontes
    font_config = FontConfiguration()
    css_string = '''
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
    ''' % (
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
    
    # Calcula total de ausências no período
    total_ausencias = pdis.filter(status='ausente').count()
    
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
        'total_ausencias': total_ausencias,  # Adicionando total de ausências
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
        
        # Buscar dados institucionais para o cabeçalho
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None
        
        # Calcula total de ausências no período
        total_ausencias = PDI.objects.filter(
            neurodivergente=neurodivergente,
            data_criacao__range=(data_inicial_dt, data_final_dt),
            status='ausente'
        ).count()
        
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
            'total_ausencias': total_ausencias,  # Adicionando total de ausências
            'datas_metas': datas_metas,
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
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
def gerar_relatorio_evolucao_html(request, neurodivergente_id):
    try:
        # Obtém as datas do filtro
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        if not data_inicial or not data_final:
            messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                      f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Converte as datas para datetime
        try:
            data_inicial_dt = datetime.strptime(data_inicial + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            data_final_dt = datetime.strptime(data_final + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        except Exception as date_error:
            messages.error(request, 'Formato de data inválido.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                      f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Busca o neurodivergente
        neurodivergente = get_object_or_404(Neurodivergente, id=neurodivergente_id)
        
        # Busca as evoluções do período
        evolucoes = RegistroEvolucao.objects.filter(
            neurodivergente=neurodivergente,
            data__range=(data_inicial_dt, data_final_dt)
        ).order_by('data')
        
        # Buscar dados institucionais para o cabeçalho
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None
        
        context = {
            'neurodivergente': neurodivergente,
            'evolucoes': evolucoes,
            'nome_completo': f"{neurodivergente.primeiro_nome} {neurodivergente.ultimo_nome}",
            'data_inicial': data_inicial_dt.strftime('%d/%m/%Y'),
            'data_final': data_final_dt.strftime('%d/%m/%Y'),
            'data_geracao': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
        }
        
        return render(request, 'neurodivergentes/relatorio_evolucao.html', context)
        
    except Exception as e:
        messages.error(request, 'Erro ao gerar relatório.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                  f'?neurodivergente__id__exact={neurodivergente_id}')

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

def get_filtro_datas(queryset, request):
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    if data_inicial:
        queryset = queryset.filter(data__gte=data_inicial)
    if data_final:
        queryset = queryset.filter(data__lte=data_final)
    return queryset

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

@login_required
def imprimir_evolucao(request, evolucao_id):
    """View para imprimir uma evolução individual em PDF"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'Iniciando impressão da evolução {evolucao_id}')
    
    try:
        from weasyprint import HTML, CSS
        
        evolucao = get_object_or_404(
            RegistroEvolucao.objects.select_related(
                'neurodivergente',
                'profissional'
            ),
            id=evolucao_id
        )
        
        logger.info(f'Evolução encontrada: {evolucao.id} - {evolucao.neurodivergente.nome_completo}')
        
        # Buscar dados institucionais para o cabeçalho
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None
        
        context = {
            'evolucao': evolucao,
            'data_impressao': timezone.now(),
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
        }
        
        css_string = '''
            :root {
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --accent-color: #e74c3c;
                --text-color: #333;
                --light-gray: #ecf0f1;
                --border-color: #bdc3c7;
            }
            
            body {
                font-family: 'Roboto', sans-serif;
                color: var(--text-color);
                line-height: 1.6;
                margin: 0;
                padding: 2cm;
                background-color: white;
            }
            
            .header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid var(--primary-color);
            }
            
            .logo {
                color: var(--primary-color);
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            
            h1 {
                color: var(--primary-color);
                font-size: 1.8rem;
                margin: 0;
            }
            
            .info-section {
                background-color: var(--light-gray);
                padding: 1.5rem;
                border-radius: 8px;
                margin-bottom: 2rem;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1.5rem;
            }
            
            .info-group {
                background-color: white;
                padding: 1rem;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            .info-label {
                color: var(--secondary-color);
                font-weight: bold;
                font-size: 0.9rem;
                margin-bottom: 0.3rem;
            }
            
            .info-value {
                font-size: 1.1rem;
            }
            
            .content-section {
                margin-bottom: 2rem;
            }
            
            .section-title {
                color: var(--primary-color);
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border-color);
            }
            
            .description-box {
                background-color: white;
                padding: 1.5rem;
                border: 1px solid var(--border-color);
                border-radius: 4px;
                white-space: pre-wrap;
            }
            
            .anexos-list {
                list-style: none;
                padding: 0;
            }
            
            .anexos-list li {
                display: flex;
                align-items: center;
                padding: 0.5rem;
                background-color: var(--light-gray);
                border-radius: 4px;
                margin-bottom: 0.5rem;
            }
            
            .attachment-icon {
                margin-right: 0.5rem;
            }
            
            .footer {
                margin-top: 3rem;
                padding-top: 1rem;
                border-top: 1px solid var(--border-color);
            }
            
            .page-number {
                text-align: right;
                color: var(--text-color);
                font-size: 0.8rem;
                margin-bottom: 2rem;
            }
            
            .signature-section {
                text-align: center;
                margin-top: 3rem;
            }
            
            .signature-line {
                width: 200px;
                margin: 0 auto;
                border-bottom: 1px solid var(--text-color);
            }
            
            .signature-name {
                margin-top: 0.5rem;
                font-weight: bold;
            }
            
            .signature-title {
                color: var(--text-color);
                font-size: 0.9rem;
            }
            
            @page {
                size: A4;
                margin: 0;
                @top-right {
                    content: counter(page);
                }
            }
        '''
        
        logger.info('Renderizando template HTML')
        html_string = render_to_string('neurodivergentes/relatorio_evolucao.html', context)
        
        logger.info('Configurando fontes')
        font_config = FontConfiguration()
        
        logger.info('Gerando PDF')
        base_url = request.build_absolute_uri('/').rstrip('/')
        html = HTML(string=html_string, base_url=base_url)
        css = CSS(string=css_string, font_config=font_config)
        pdf = html.write_pdf(
            stylesheets=[css],
            font_config=font_config,
            presentational_hints=True
        )
        
        logger.info('Enviando PDF')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="evolucao_{evolucao.id}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        logger.error(f'Erro ao gerar PDF: {str(e)}')
        raise

@login_required
def gerar_relatorio_evolucao_html(request, neurodivergente_id):
    """View para gerar o relatório geral de evoluções em HTML"""
    try:
        # Obtém as datas do filtro
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        if not data_inicial or not data_final:
            messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                      f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Converte as datas para datetime
        try:
            data_inicial_dt = datetime.strptime(data_inicial + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            data_final_dt = datetime.strptime(data_final + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        except Exception as date_error:
            messages.error(request, 'Formato de data inválido.')
            return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                      f'?neurodivergente__id__exact={neurodivergente_id}')
        
        # Busca o neurodivergente
        neurodivergente = get_object_or_404(Neurodivergente, id=neurodivergente_id)
        
        # Busca as evoluções do período
        evolucoes = RegistroEvolucao.objects.filter(
            neurodivergente=neurodivergente,
            data__range=(data_inicial_dt, data_final_dt)
        ).order_by('data')
        
        # Buscar dados institucionais para o cabeçalho
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None
        
        context = {
            'neurodivergente': neurodivergente,
            'evolucoes': evolucoes,
            'nome_completo': f"{neurodivergente.primeiro_nome} {neurodivergente.ultimo_nome}",
            'data_inicial': data_inicial_dt.strftime('%d/%m/%Y'),
            'data_final': data_final_dt.strftime('%d/%m/%Y'),
            'data_geracao': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
        }
        
        return render(request, 'neurodivergentes/relatorio_evolucao.html', context)
        
    except Exception as e:
        messages.error(request, 'Erro ao gerar relatório.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_registroevolucao_changelist') + 
                                  f'?neurodivergente__id__exact={neurodivergente_id}')

@login_required
def lista_evolucao(request, aluno_id, evolucao_id=None):
    """View para listar as evoluções de um aluno específico ou visualizar uma evolução específica."""
    aluno = get_object_or_404(Neurodivergente, id=aluno_id)
    
    if evolucao_id:
        # Se um ID de evolução foi fornecido, mostra os detalhes dessa evolução
        evolucao = get_object_or_404(RegistroEvolucao, id=evolucao_id, neurodivergente=aluno)
        return render(request, 'neurodivergentes/evolucao_detail.html', {
            'aluno': aluno,
            'evolucao': evolucao
        })
    
    # Obtém os filtros de data
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    
    # Query base
    evolucoes = RegistroEvolucao.objects.filter(neurodivergente=aluno)
    
    # Aplica filtros de data se fornecidos
    if data_inicial:
        evolucoes = evolucoes.filter(data__gte=data_inicial)
    if data_final:
        evolucoes = evolucoes.filter(data__lte=data_final)
    
    # Ordenação
    evolucoes = evolucoes.order_by('-data')
    
    # Paginação
    paginator = Paginator(evolucoes, 10)  # 10 itens por página
    page = request.GET.get('page')
    evolucoes_paginadas = paginator.get_page(page)
    
    context = {
        'aluno': aluno,
        'evolucoes': evolucoes_paginadas,
        'data_inicial': data_inicial,
        'data_final': data_final,
    }
    
    return render(request, 'neurodivergentes/evolucao_list.html', context)

@login_required
def evolucao_popup_view(request, evolucao_id):
    """View para exibir o popup com detalhes da evolução"""
    evolucao = get_object_or_404(
        RegistroEvolucao.objects.select_related(
            'neurodivergente',
            'profissional'
        ),
        id=evolucao_id
    )
    
    context = {
        'evolucao': evolucao,
    }
    
    return render(request, 'admin/neurodivergentes/registroevolucao/popup_view.html', context)

@login_required
def lista_pei(request, aluno_id):
    """View para listar os PEIs de um aluno específico."""
    aluno = get_object_or_404(Neurodivergente, id=aluno_id)
    
    # Obtém os filtros
    ano = request.GET.get('ano')
    
    # Query base
    peis = Monitoramento.objects.filter(neurodivergente=aluno)
    
    # Aplica os filtros
    if ano:
        peis = peis.filter(ano=ano)
    
    # Ordena por ano (mais recente primeiro)
    peis = peis.order_by('-ano')
    
    # Paginação
    paginator = Paginator(peis, 10)
    page = request.GET.get('page')
    peis = paginator.get_page(page)
    
    # Lista de anos (do mais recente para o mais antigo)
    anos = sorted(set(Monitoramento.objects.filter(
        neurodivergente=aluno).values_list('ano', flat=True)
    ), reverse=True)
    
    context = {
        'aluno': aluno,
        'peis': peis,
        'anos': anos,
        'ano_selecionado': int(ano) if ano else None,
    }
    
    return render(request, 'neurodivergentes/pei_list.html', context)

@login_required
def pei_popup_view(request, pei_id):
    """View para exibir o popup com detalhes do PEI"""
    pei = get_object_or_404(
        Monitoramento.objects.select_related(
            'neurodivergente',
            'pedagogo_responsavel'
        ).prefetch_related('metas'),
        id=pei_id
    )
    
    context = {
        'pei': pei,
        'aluno': pei.neurodivergente
    }
    
    return render(request, 'neurodivergentes/pei_detail.html', context)

@login_required
def imprimir_pei(request, pei_id):
    """View para imprimir um PEI individual em PDF"""
    pei = get_object_or_404(
        Monitoramento.objects.select_related(
            'neurodivergente',
            'pedagogo_responsavel'
        ).prefetch_related('metas'),
        id=pei_id
    )
    
    # Buscar dados institucionais para o cabeçalho
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None
    
    context = {
        'pei': pei,
        'aluno': pei.neurodivergente,
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura as fontes
    font_config = FontConfiguration()
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_pei.html', context)
    
    # Cria o PDF
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    pdf = html.write_pdf(
        font_config=font_config,
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=pei_{pei.id}.pdf'
    
    return response

@login_required
def gerar_relatorio_parecer_pdf(request, neurodivergente_id):
    """View para gerar o relatório geral de pareceres em PDF"""
    # Obtém os filtros
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    
    if not data_inicial or not data_final:
        messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_pareceravaliativo_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
    
    # Converte as datas para datetime
    try:
        data_inicial_dt = datetime.strptime(data_inicial + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        data_final_dt = datetime.strptime(data_final + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    except Exception as date_error:
        logger.error(f"Erro ao converter datas: {str(date_error)}")
        messages.error(request, 'Formato de data inválido.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_pareceravaliativo_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
    
    # Busca o neurodivergente
    neurodivergente = get_object_or_404(Neurodivergente, id=neurodivergente_id)
    
    # Filtra os pareceres pelo período
    pareceres = ParecerAvaliativo.objects.filter(
        neurodivergente=neurodivergente,
        data_avaliacao__gte=data_inicial_dt,
        data_avaliacao__lte=data_final_dt
    ).select_related(
        'profissional_responsavel'
    ).order_by('data_avaliacao')
    
    if not pareceres.exists():
        messages.warning(request, 'Nenhum parecer encontrado no período selecionado.')
        return HttpResponseRedirect(reverse('admin:neurodivergentes_pareceravaliativo_changelist') + f'?neurodivergente__id__exact={neurodivergente_id}')
    
    # Busca as configurações da prefeitura (pega a primeira ativa, ou a mais recente)
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None

    context = {
        'pareceres': pareceres,
        'neurodivergente': neurodivergente,
        'periodo': {
            'inicio': datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y'),
            'fim': datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
        },
        'total_pareceres': pareceres.count(),
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura o CSS com as fontes
    css_string = '''
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
    ''' % (
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
    )
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_parecer_geral.html', context)
    
    # Cria o PDF
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    css = CSS(string=css_string)
    pdf = html.write_pdf(
        stylesheets=[css],
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=relatorio_pareceres_{neurodivergente.id}.pdf'
    
    return response

@login_required
def gerar_relatorio_parecer_geral_pdf(request, neurodivergente_id):
    try:
        # Obtém as datas do filtro
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        logger.info(f"Parâmetros recebidos - data_inicial: {data_inicial}, data_final: {data_final}, neurodivergente_id: {neurodivergente_id}")
        
        if not data_inicial or not data_final:
            logger.warning("Datas não fornecidas")
            messages.error(request, 'Por favor, selecione um período para gerar o relatório.')
            return redirect('admin:neurodivergentes_pareceravaliativo_changelist')
        
        # Converte as datas para datetime
        try:
            data_inicial_dt = datetime.strptime(data_inicial + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            data_final_dt = datetime.strptime(data_final + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        except Exception as date_error:
            logger.error(f"Erro ao converter datas: {str(date_error)}")
            messages.error(request, 'Formato de data inválido.')
            return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")
        
        # Busca o neurodivergente com prefetch para otimizar
        try:
            neurodivergente = Neurodivergente.objects.prefetch_related(
                'neurodivergencias',
                Prefetch(
                    'neurodivergencias__diagnosticos',
                    queryset=DiagnosticoNeurodivergente.objects.select_related('condicao')
                )
            ).get(id=neurodivergente_id)
            
            if not neurodivergente:
                logger.error(f"Neurodivergente não encontrado: {neurodivergente_id}")
                messages.error(request, 'Aluno não encontrado.')
                return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")
                
        except Neurodivergente.DoesNotExist:
            logger.error(f"Neurodivergente não encontrado: {neurodivergente_id}")
            messages.error(request, 'Aluno não encontrado.')
            return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")
        except Exception as neurodiv_error:
            logger.error(f"Erro ao buscar neurodivergente: {str(neurodiv_error)}")
            messages.error(request, 'Erro ao encontrar informações do aluno.')
            return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")
        
        # Busca pareceres no período com todos os relacionamentos necessários
        pareceres = ParecerAvaliativo.objects.filter(
            neurodivergente=neurodivergente,
            data_avaliacao__range=(data_inicial_dt, data_final_dt)
        ).select_related(
            'profissional_responsavel__user',  # Inclui o usuário do profissional
            'escola'
        ).order_by('data_avaliacao')
        
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
        
        # Busca as configurações da prefeitura (pega a primeira ativa, ou a mais recente)
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None

        # Prepara contexto com todos os dados
        context = {
            'neurodivergente': neurodivergente,
            'neurodivergencias': neurodivergencias,
            'pareceres': pareceres,
            'diagnosticos': diagnosticos,
            'periodo': {
                'inicio': datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%Y'),
                'fim': datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%Y')
            },
            'total_pareceres': pareceres.count(),
            'data_impressao': timezone.now(),
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
        }
        
        # Log de diagnóstico
        logger.info(f"Dados do relatório - Pareceres: {pareceres.count()}")
        
        # Configura o CSS com as fontes
        css_string = '''
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
        ''' % (
            os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
            os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
        )
        
        # Renderiza o template HTML
        html_string = render_to_string('neurodivergentes/relatorio_parecer_geral.html', context)
        
        # Cria o PDF
        base_url = request.build_absolute_uri('/').rstrip('/')
        html = HTML(string=html_string, base_url=base_url)
        css = CSS(string=css_string)
        pdf = html.write_pdf(
            stylesheets=[css],
            presentational_hints=True
        )
        
        try:
            # Retorna o PDF como resposta HTTP para visualização no navegador
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename=relatorio_pareceres_{neurodivergente.id}.pdf'
            
            return response
        except Exception as pdf_error:
            logger.error(f"Erro ao gerar PDF: {str(pdf_error)}", exc_info=True)
            messages.error(request, 'Erro ao gerar o PDF do relatório.')
            return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")
    
    except Exception as e:
        # Log de erro detalhado
        logger.error(f"Erro inesperado ao gerar relatório HTML: {str(e)}", exc_info=True)
        messages.error(request, 'Erro ao gerar o relatório. Por favor, tente novamente.')
        return redirect(f"{reverse('admin:neurodivergentes_pareceravaliativo_changelist')}?neurodivergente__id__exact={neurodivergente_id}")

@login_required
def imprimir_parecer(request, parecer_id):
    """View para gerar o relatório individual do parecer em PDF"""
    parecer = get_object_or_404(ParecerAvaliativo, id=parecer_id)
    
    # Busca as configurações da prefeitura (pega a primeira ativa, ou a mais recente)
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None

    context = {
        'parecer': parecer,
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura o CSS com as fontes
    css_string = '''
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
    ''' % (
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
    )
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_parecer.html', context)
    
    # Cria o PDF
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    css = CSS(string=css_string)
    pdf = html.write_pdf(
        stylesheets=[css],
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=parecer_{parecer.id}.pdf'
    
    return response

@login_required
def gerar_relatorio_pei_pdf(request, neurodivergente_id):
    """View para gerar o relatório geral de PAEEs em PDF"""
    # Obtém os filtros
    ano = request.GET.get('ano')
    
    if not ano:
        messages.error(request, 'Por favor, selecione o ano para gerar o relatório.')
        return redirect('neurodivergentes:lista_pei', neurodivergente_id=neurodivergente_id)
    
    neurodivergente = get_object_or_404(Neurodivergente, id=neurodivergente_id)
    
    # Filtra os PAEEs pelo ano
    peis = Monitoramento.objects.filter(
        neurodivergente=neurodivergente,
        ano=ano
    ).select_related(
        'pedagogo_responsavel'
    ).prefetch_related(
        'metas'
    ).order_by('ano')
    
    if not peis.exists():
        messages.warning(request, 'Nenhum PAEE encontrado no ano selecionado.')
        return redirect('neurodivergentes:lista_pei', neurodivergente_id=neurodivergente_id)
    
    # Buscar dados institucionais para o cabeçalho
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None
    
    context = {
        'aluno': neurodivergente,
        'peis': peis,
        'periodo': f"Ano de {ano}",
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura o CSS com as fontes
    css_string = '''
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
    ''' % (
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
    )
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_pei_geral.html', context)
    
    # Cria o PDF
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    css = CSS(string=css_string)
    pdf = html.write_pdf(
        stylesheets=[css],
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=relatorio_pei_{neurodivergente.id}.pdf'
    
    return response

@login_required
def imprimir_anamnese(request, anamnese_id):
    """View para imprimir uma anamnese individual em PDF"""
    anamnese = get_object_or_404(
        Anamnese.objects.select_related(
            'neurodivergente',
            'profissional_responsavel'
        ).prefetch_related(
            'medicacoes',
            'rotinas'
        ),
        id=anamnese_id
    )
    
    # Buscar dados institucionais para o cabeçalho
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None
    
    context = {
        'anamnese': anamnese,
        'aluno': anamnese.neurodivergente,
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
        'request': request
    }
    
    # Configura as fontes
    font_config = FontConfiguration()
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_anamnese.html', context, request=request)
    
    # Cria o PDF
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    pdf = html.write_pdf(
        font_config=font_config,
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=anamnese_{anamnese.id}.pdf'
    
    return response

@login_required
def imprimir_aluno(request, aluno_id):
    """View para imprimir um relatório completo do Aluno/Paciente"""
    aluno = get_object_or_404(
        Neurodivergente.objects.select_related('escola'),
        id=aluno_id
    )
    
    # Buscar informações sobre neurodivergências
    try:
        neurodivergencia = Neurodivergencia.objects.prefetch_related(
            'diagnosticos__condicao',
            'diagnosticos__categoria'
        ).get(neurodivergente=aluno)
        diagnosticos = neurodivergencia.diagnosticos.all()
        status_neurodivergencia = "Em Investigação" if not diagnosticos.exists() else ", ".join([d.condicao.nome for d in diagnosticos])
    except Neurodivergencia.DoesNotExist:
        neurodivergencia = None
        diagnosticos = []
        status_neurodivergencia = "Não"
    
    # Contar registros relacionados
    evolucoes_count = RegistroEvolucao.objects.filter(neurodivergente=aluno).count()
    pdis_count = PDI.objects.filter(neurodivergente=aluno).count()
    peis_count = Monitoramento.objects.filter(neurodivergente=aluno).count()
    pareceres_count = ParecerAvaliativo.objects.filter(neurodivergente=aluno).count()
    
    # Verificar se existe anamnese
    tem_anamnese = Anamnese.objects.filter(neurodivergente=aluno).exists()
    
    # Buscar grupo familiar
    grupo_familiar = aluno.grupo_familiar.all()
    
    hoje = date.today()
    for membro in grupo_familiar:
        if membro.data_nascimento:
            nascimento = membro.data_nascimento
            idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            membro.idade_calculada = idade
        else:
            membro.idade_calculada = None
    
    # Buscar dados institucionais para o cabeçalho
    config = ConfiguracaoCliente.objects.order_by('-id').first()
    logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
    nome_prefeitura = config.nome_municipio if config else None
    cnpj_prefeitura = config.cnpj if config else None
    
    context = {
        'aluno': aluno,
        'neurodivergencia': neurodivergencia,
        'diagnosticos': diagnosticos,
        'status_neurodivergencia': status_neurodivergencia,
        'evolucoes_count': evolucoes_count,
        'pdis_count': pdis_count,
        'peis_count': peis_count,
        'pareceres_count': pareceres_count,
        'tem_anamnese': tem_anamnese,
        'grupo_familiar': grupo_familiar,
        'data_impressao': timezone.now(),
        'logo_prefeitura_url': logo_prefeitura_url,
        'nome_prefeitura': nome_prefeitura,
        'cnpj_prefeitura': cnpj_prefeitura,
    }
    
    # Configura as fontes
    font_config = FontConfiguration()
    css_string = '''
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
    ''' % (
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Regular.ttf'),
        os.path.join(settings.STATIC_ROOT, 'fonts/Roboto-Bold.ttf')
    )
    
    # Renderiza o template HTML
    html_string = render_to_string('neurodivergentes/relatorio_aluno.html', context)
    
    # Cria o PDF com as configurações de fonte
    base_url = request.build_absolute_uri('/').rstrip('/')
    html = HTML(string=html_string, base_url=base_url)
    css = CSS(string=css_string)
    pdf = html.write_pdf(
        stylesheets=[css],
        presentational_hints=True
    )
    
    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=aluno_{aluno.id}.pdf'
    
    return response

@login_required
def imprimir_neurodivergencia(request, neurodivergencia_id):
    """
    Gera um relatório de neurodivergência para impressão.
    """
    try:
        neurodivergencia = Neurodivergencia.objects.get(pk=neurodivergencia_id)
        diagnosticos = DiagnosticoNeurodivergente.objects.filter(neurodivergencia=neurodivergencia)
        
        # Buscar dados institucionais para o cabeçalho
        config = ConfiguracaoCliente.objects.order_by('-id').first()
        logo_prefeitura_url = request.build_absolute_uri(config.logomarca.url) if config and config.logomarca else None
        nome_prefeitura = config.nome_municipio if config else None
        cnpj_prefeitura = config.cnpj if config else None
        
        context = {
            'neurodivergencia': neurodivergencia,
            'diagnosticos': diagnosticos,
            'data_impressao': timezone.now(),
            'logo_prefeitura_url': logo_prefeitura_url,
            'nome_prefeitura': nome_prefeitura,
            'cnpj_prefeitura': cnpj_prefeitura,
        }
        
        html_string = render_to_string('neurodivergentes/relatorio_neurodivergencia.html', context)
        base_url = request.build_absolute_uri('/').rstrip('/')
        html = HTML(string=html_string, base_url=base_url)
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename=neurodivergencia_{neurodivergencia_id}.pdf'
        return response
    except Neurodivergencia.DoesNotExist:
        raise Http404("Neurodivergência não encontrada")

@require_GET
def api_neurodivergencias_por_escola(request):
    from .models import Escola, Neurodivergente, DiagnosticoNeurodivergente, CondicaoNeurodivergente
    escolas = Escola.objects.all()

    # Buscar apenas as condicoes de diagnósticos realmente vinculados a alunos ativos
    neurodivergentes = Neurodivergente.objects.filter(ativo=True, escola__isnull=False)
    diagnos = DiagnosticoNeurodivergente.objects.filter(
        neurodivergencia__neurodivergente__in=neurodivergentes
    ).select_related('condicao', 'neurodivergencia__neurodivergente')
    condicoes_usadas = CondicaoNeurodivergente.objects.filter(id__in=diagnos.values_list('condicao_id', flat=True).distinct())

    labels = [escola.nome for escola in escolas]
    condicoes = list(condicoes_usadas)
    condicao_id_to_nome = {condicao.id: condicao.nome for condicao in condicoes}

    data_por_condicao = {condicao.nome: [0 for _ in escolas] for condicao in condicoes}
    escola_id_to_idx = {escola.id: idx for idx, escola in enumerate(escolas)}

    for diag in diagnos:
        escola = diag.neurodivergencia.neurodivergente.escola
        condicao = diag.condicao
        if escola and condicao and condicao.id in condicao_id_to_nome:
            escola_idx = escola_id_to_idx.get(escola.id)
            if escola_idx is not None:
                data_por_condicao[condicao.nome][escola_idx] += 1

    import random
    def pastel_color():
        base = 200
        r = random.randint(base, 255)
        g = random.randint(base, 255)
        b = random.randint(base, 255)
        return f'rgb({r},{g},{b})'
    datasets = []
    for condicao_nome, data in data_por_condicao.items():
        datasets.append({
            'label': condicao_nome,
            'data': data,
            'backgroundColor': pastel_color(),
            'stack': 'Stack 0',
        })
    return JsonResponse({'labels': labels, 'datasets': datasets})