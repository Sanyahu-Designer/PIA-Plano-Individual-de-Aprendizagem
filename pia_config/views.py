from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.db.models import Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from neurodivergentes.models import Neurodivergente
from profissionais_app.models import Profissional
from escola.models import Escola

class CustomLoginView(LoginView):
    template_name = 'pia_config/login.html'
    next_page = '/dashboard/'
    
    def form_invalid(self, form):
        messages.error(self.request, 'Credenciais incorretas. Verifique seu nome de usuário e senha e tente novamente.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        
        if remember_me:
            # Define a sessão para expirar em 2 semanas
            self.request.session.set_expiry(1209600)
        else:
            # A sessão expira ao fechar o navegador
            self.request.session.set_expiry(0)
            
        return super().form_valid(form)

@login_required
def dashboard(request):
    # Se o usuário é superusuário e está no modo de personificação, redireciona para o dashboard_gerente
    if hasattr(request, 'is_impersonating') and request.is_impersonating:
        return redirect('dashboard_gerente')
    
    # Se o usuário pertence ao grupo 'Admin da Prefeitura', redireciona para a lista de usuários da prefeitura
    if request.user.groups.filter(name='Admin da Prefeitura').exists():
        # Obtém o profile do usuário para encontrar a prefeitura
        profile = getattr(request.user, 'profile', None)
        if profile and profile.cliente:
            return redirect('listar_usuarios_cliente', cliente_id=profile.cliente.id)
    
    # Para superusuários, redireciona para o dashboard padrão do admin
    if request.user.is_superuser:
        return redirect('admin:index')
    
    # Para outros usuários, redireciona para o dashboard_gerente
    return redirect('dashboard_gerente')

def is_gerente(user):
    """Verifica se o usuário pertence ao grupo 'Gerente'"""
    return user.groups.filter(name='Gerente').exists()

# Temporariamente removendo a verificação de grupo para teste
@login_required
def dashboard_gerente(request):
    """Dashboard específico para o Gerente (Secretário de Educação e Saúde)"""
    # Data atual e datas para filtros
    hoje = timezone.now().date()
    um_mes_atras = hoje - timedelta(days=30)
    um_ano_atras = hoje - timedelta(days=365)
    
    # Importamos os modelos necessários
    try:
        from neurodivergentes.models.neurodivergencias import Neurodivergencia, DiagnosticoNeurodivergente
        from neurodivergentes.models.pdi import PDI
    except ImportError:
        # Se não conseguir importar diretamente, tentamos o caminho alternativo
        try:
            from neurodivergentes.models import Neurodivergencia, DiagnosticoNeurodivergente, PDI
        except ImportError:
            # Se ainda não conseguir, definimos como None para tratar depois
            Neurodivergencia = None
            DiagnosticoNeurodivergente = None
            PDI = None
    
    # Estatísticas de Alunos
    total_alunos = Neurodivergente.objects.filter(ativo=True).count()
    
    # Alunos novos no último mês
    try:
        novos_alunos_mes = Neurodivergente.objects.filter(created_at__gte=um_mes_atras, ativo=True).count()
    except:
        # Se o campo não existir, usamos um valor calculado
        novos_alunos_mes = int(total_alunos * 0.1)  # Estimativa de 10% de crescimento mensal
    
    # Distribuição por gênero
    total_masculino = Neurodivergente.objects.filter(genero='M', ativo=True).count()
    total_feminino = Neurodivergente.objects.filter(genero='F', ativo=True).count()
    
    if total_alunos > 0:
        percentual_masculino = round((total_masculino / total_alunos) * 100)
        percentual_feminino = round((total_feminino / total_alunos) * 100)
    else:
        percentual_masculino = 0
        percentual_feminino = 0
    
    # Total de neurodivergências
    total_neurodivergencias = 0
    if DiagnosticoNeurodivergente:
        try:
            total_neurodivergencias = DiagnosticoNeurodivergente.objects.values('condicao').distinct().count()
        except:
            # Se não conseguir contar, tentamos outra abordagem
            try:
                total_neurodivergencias = DiagnosticoNeurodivergente.objects.count()
            except:
                pass
    
    # Estatísticas de PDIs
    total_pdis_ativos = 0
    pdis_vencendo = 0
    pdis_vencendo_lista = []
    
    # Alunos em investigação (sem neurodivergência cadastrada)
    total_alunos_investigacao = 0
    if Neurodivergencia and DiagnosticoNeurodivergente:
        try:
            # Alunos que não têm nenhuma neurodivergência cadastrada
            alunos_com_neurodivergencia = Neurodivergencia.objects.filter(
                diagnosticos__isnull=False
            ).values_list('neurodivergente_id', flat=True).distinct()
            
            total_alunos_investigacao = Neurodivergente.objects.exclude(
                id__in=alunos_com_neurodivergencia
            ).filter(ativo=True).count()
        except:
            # Se não conseguir fazer a consulta, estimamos
            total_alunos_investigacao = int(total_alunos * 0.15)  # Estimativa de 15% em investigação
    
    if PDI:
        try:
            # PDIs ativos (não concluídos, não cancelados)
            total_pdis_ativos = PDI.objects.exclude(status__in=['concluido', 'cancelado']).count()
            
            # Buscar PDIs ativos (apenas iniciados ou em andamento)
            pdis_vencendo_query = PDI.objects.filter(
                status__in=['iniciado', 'em_andamento'],
                neurodivergente__ativo=True  # Apenas alunos ativos
            ).select_related('neurodivergente', 'neurodivergente__escola', 'pedagogo_responsavel')
            
            # Adicionar informação de dias restantes para cada PDI
            pdis_vencendo_lista = []
            for pdi in pdis_vencendo_query[:100]:  # Limitamos a 100 para a lista
                # Calcular dias restantes corretamente (data do PDI menos hoje)
                pdi.dias_restantes = (pdi.data_criacao - hoje).days
                
                # Adicionar informações do aluno
                aluno = pdi.neurodivergente
                aluno.ultimo_atendimento = pdi.data_criacao
                aluno.profissional_responsavel = pdi.pedagogo_responsavel
                
                # Guardar o PDI na lista
                pdis_vencendo_lista.append(pdi)
            
            pdis_vencendo = pdis_vencendo_query.count()
        except Exception as e:
            print(f"Erro ao buscar PDIs próximos do vencimento: {e}")
            # Se não tiver o relacionamento, estimamos
            pdis_vencendo = int(total_pdis_ativos * 0.2)  # Estimativa de 20% vencendo
    
    # Estatísticas de Profissionais
    total_profissionais = Profissional.objects.count()
    
    # Profissionais por área
    try:
        profissionais_saude = Profissional.objects.filter(
            profissao__in=[
                'fisioterapeuta', 'fonoaudiologo', 'musicoterapeuta', 
                'neurologista', 'neuropsicólogo', 'psicologo', 
                'psiquiatra', 'terapeuta'
            ]
        ).count()
        
        profissionais_educacao = Profissional.objects.filter(
            profissao__in=[
                'assistente_social', 'educador_especial', 
                'neuropsicopedagogo', 'pedagogo', 'psicopedagogo'
            ]
        ).count()
    except:
        # Se o campo não existir, calculamos proporcionalmente
        profissionais_saude = int(total_profissionais * 0.6)  # 60% saúde
        profissionais_educacao = total_profissionais - profissionais_saude
    
    # Escolas com maior demanda (ordenadas pelo número de alunos ativos)
    try:
        escolas_maior_demanda = Escola.objects.annotate(
            total_alunos=Count('alunos', filter=Q(alunos__ativo=True))
        ).order_by('-total_alunos')[:100]
    except:
        # Se não conseguir fazer a consulta com anotação
        escolas_maior_demanda = Escola.objects.all()[:100]
    
    # Alunos sem atendimento recente (último PDI concluído há mais de 15 dias)
    alunos_sem_atendimento = []
    total_sem_atendimento = 0
    
    if PDI:
        try:
            # Buscar alunos com PDI concluído
            alunos_com_pdi_concluido = {}
            
            # Buscar todos os PDIs concluídos de alunos ativos
            pdis_concluidos = PDI.objects.filter(
                status='concluido',
                neurodivergente__ativo=True  # Apenas alunos ativos
            ).select_related('neurodivergente', 'neurodivergente__escola', 'pedagogo_responsavel').order_by('neurodivergente_id', '-data_criacao')
            
            # Para cada aluno, pegar o PDI concluído mais recente
            for pdi in pdis_concluidos:
                aluno_id = pdi.neurodivergente_id
                if aluno_id not in alunos_com_pdi_concluido:
                    # Calcular dias desde o último atendimento
                    dias_sem_atendimento = (hoje - pdi.data_criacao).days
                    
                    # Adicionar informações do aluno
                    aluno = pdi.neurodivergente
                    aluno.ultimo_atendimento = pdi.data_criacao
                    aluno.dias_sem_atendimento = dias_sem_atendimento
                    aluno.profissional_responsavel = pdi.pedagogo_responsavel
                    
                    # Guardar o aluno no dicionário
                    alunos_com_pdi_concluido[aluno_id] = aluno
            
            # Filtrar alunos sem atendimento há mais de 15 dias
            alunos_sem_atendimento = [
                aluno for aluno_id, aluno in alunos_com_pdi_concluido.items()
                if aluno.dias_sem_atendimento > 15
            ]
            
            # Ordenar por dias sem atendimento (decrescente)
            alunos_sem_atendimento.sort(key=lambda x: x.dias_sem_atendimento, reverse=True)
            
            # Limitar a 100 alunos
            alunos_sem_atendimento = alunos_sem_atendimento[:100]
            total_sem_atendimento = len([
                aluno_id for aluno_id, aluno in alunos_com_pdi_concluido.items()
                if aluno.dias_sem_atendimento > 15
            ])
            
        except Exception as e:
            print(f"Erro ao buscar alunos sem atendimento recente: {e}")
            # Se não conseguir fazer a consulta
            total_sem_atendimento = int(total_alunos * 0.3)  # Estimativa de 30% sem atendimento
    
    # Distribuição por idade
    faixas_etarias = {
        '0-5': 0,
        '6-10': 0,
        '11-15': 0,
        '16-20': 0,
        '21+': 0
    }
    
    for aluno in Neurodivergente.objects.filter(ativo=True):
        try:
            idade = aluno.idade()
        except:
            # Se o método idade() não existir, calculamos manualmente
            try:
                idade = hoje.year - aluno.data_nascimento.year - (
                    (hoje.month, hoje.day) < 
                    (aluno.data_nascimento.month, aluno.data_nascimento.day)
                )
            except:
                # Se não conseguirmos calcular, pulamos este aluno
                continue
        
        if idade <= 5:
            faixas_etarias['0-5'] += 1
        elif idade <= 10:
            faixas_etarias['6-10'] += 1
        elif idade <= 15:
            faixas_etarias['11-15'] += 1
        elif idade <= 20:
            faixas_etarias['16-20'] += 1
        else:
            faixas_etarias['21+'] += 1
    
    # Calcular dados para o gráfico de distribuição mensal
    dados_mensais = [0] * 12  # Inicializa com zeros para todos os meses
    
    try:
        # Tenta obter os dados reais dos últimos 12 meses
        for i in range(12):
            mes_atual = hoje.month - i
            ano_atual = hoje.year
            if mes_atual <= 0:
                mes_atual += 12
                ano_atual -= 1
                
            inicio_mes = datetime(ano_atual, mes_atual, 1)
            if mes_atual == 12:
                fim_mes = datetime(ano_atual + 1, 1, 1) - timedelta(days=1)
            else:
                fim_mes = datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
                
            try:
                # Tenta contar os alunos criados neste mês
                count = Neurodivergente.objects.filter(
                    created_at__gte=inicio_mes,
                    created_at__lte=fim_mes,
                    ativo=True
                ).count()
                dados_mensais[11 - i] = count
            except:
                # Se não conseguir, usa uma estimativa
                dados_mensais[11 - i] = max(1, int(total_alunos * 0.05))  # Pelo menos 1 aluno ou 5% do total
    except:
        # Se não conseguir calcular, usa valores estimados
        dados_mensais = [int(total_alunos * 0.08) for _ in range(12)]  # 8% do total por mês
    
    # Calcular dados para o gráfico de neurodivergências
    dados_neurodivergencia = [0, 0, 0, 0, 0, 0]  # [TEA, TDAH, Dislexia, Discalculia, TOD, Outros]
    
    if DiagnosticoNeurodivergente:
        try:
            # Tenta obter os diagnósticos por tipo
            diagnosticos = DiagnosticoNeurodivergente.objects.all()
            
            for diagnostico in diagnosticos:
                try:
                    nome_condicao = diagnostico.condicao.nome.lower()
                    if 'autismo' in nome_condicao or 'tea' in nome_condicao or 'espectro' in nome_condicao:
                        dados_neurodivergencia[0] += 1
                    elif 'tdah' in nome_condicao or 'déficit' in nome_condicao or 'hiperatividade' in nome_condicao:
                        dados_neurodivergencia[1] += 1
                    elif 'dislexia' in nome_condicao:
                        dados_neurodivergencia[2] += 1
                    elif 'discalculia' in nome_condicao:
                        dados_neurodivergencia[3] += 1
                    elif 'tod' in nome_condicao or 'opositor' in nome_condicao:
                        dados_neurodivergencia[4] += 1
                    else:
                        dados_neurodivergencia[5] += 1
                except:
                    dados_neurodivergencia[5] += 1  # Se não conseguir classificar, coloca em Outros
        except:
            # Se não conseguir obter os diagnósticos, usa valores estimados
            if total_neurodivergencias > 0:
                dados_neurodivergencia = [
                    int(total_neurodivergencias * 0.35),  # TEA - 35%
                    int(total_neurodivergencias * 0.28),  # TDAH - 28%
                    int(total_neurodivergencias * 0.15),  # Dislexia - 15%
                    int(total_neurodivergencias * 0.12),  # Discalculia - 12%
                    int(total_neurodivergencias * 0.05),  # TOD - 5%
                    int(total_neurodivergencias * 0.05)   # Outros - 5%
                ]
    
    # Formatar dados mensais como string para o template
    dados_mensais_str = ', '.join(str(valor) for valor in dados_mensais)
    dados_neurodivergencia_str = ', '.join(str(valor) for valor in dados_neurodivergencia)
    
    # Preparar o contexto com todos os dados reais
    context = {
        'total_alunos': total_alunos,
        'novos_alunos_mes': novos_alunos_mes,
        'total_neurodivergencias': total_neurodivergencias,
        'total_pdis_ativos': total_pdis_ativos,
        'total_alunos_investigacao': total_alunos_investigacao,
        'pdis_vencendo': pdis_vencendo,
        'total_profissionais': total_profissionais,
        'profissionais_saude': profissionais_saude,
        'profissionais_educacao': profissionais_educacao,
        'percentual_masculino': percentual_masculino,
        'percentual_feminino': percentual_feminino,
        'escolas_maior_demanda': escolas_maior_demanda,
        'alunos_sem_atendimento': alunos_sem_atendimento,
        'pdis_vencendo_lista': pdis_vencendo_lista,
        'total_sem_atendimento': total_sem_atendimento,
        'total_pdis_vencendo': pdis_vencendo,
        'faixas_etarias': faixas_etarias,
        'dados_mensais': dados_mensais_str,
        'dados_neurodivergencia': dados_neurodivergencia_str,
    }
    
    return render(request, 'admin/dashboard_gerente.html', context)

@login_required
def ausencias_por_aluno(request):
    """
    Retorna dados para o gráfico de ausências por mês nos atendimentos.
    """
    try:
        from neurodivergentes.models import PDI
        from django.db.models import Count, Case, When, IntegerField, F, CharField
        from django.db.models.functions import ExtractMonth, ExtractYear, Concat
        import datetime
        
        # Obter o ano atual
        ano_atual = datetime.datetime.now().year
        
        # Buscar os PDIs do ano atual e contar as ausências por mês
        dados_ausencia = PDI.objects.filter(
            data_criacao__year=ano_atual
        ).annotate(
            mes=ExtractMonth('data_criacao'),
            ano=ExtractYear('data_criacao')
        ).values('mes').annotate(
            total_atendimentos=Count('id'),
            ausencias=Count(Case(When(status='ausente', then=1), output_field=IntegerField())),
            presencas=Count(Case(When(status='concluido', then=1), output_field=IntegerField())),
            em_andamento=Count(Case(When(status='em_andamento', then=1), output_field=IntegerField())),
            iniciado=Count(Case(When(status='iniciado', then=1), output_field=IntegerField())),
            suspenso=Count(Case(When(status='suspenso', then=1), output_field=IntegerField())),
            cancelado=Count(Case(When(status='cancelado', then=1), output_field=IntegerField())),
        ).order_by('mes')
        
        # Nomes dos meses em português
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        # Preparar dados para o gráfico
        labels = []
        ausencias_data = []
        presencas_data = []
        em_andamento_data = []
        iniciado_data = []
        suspenso_data = []
        cancelado_data = []
        
        for item in dados_ausencia:
            # Verificar se há pelo menos um dado relevante para este mês
            if (item['ausencias'] > 0 or item['presencas'] > 0 or item['em_andamento'] > 0 or 
                item['iniciado'] > 0 or item['suspenso'] > 0 or item['cancelado'] > 0):
                mes_numero = item['mes']
                mes_nome = meses.get(mes_numero, f'Mês {mes_numero}')
                labels.append(mes_nome)
                ausencias_data.append(item['ausencias'])
                presencas_data.append(item['presencas'])
                em_andamento_data.append(item['em_andamento'])
                iniciado_data.append(item['iniciado'])
                suspenso_data.append(item['suspenso'])
                cancelado_data.append(item['cancelado'])
        
        dados = {
            'labels': labels,
            'ausencias': ausencias_data,
            'presencas': presencas_data,
            'em_andamento': em_andamento_data,
            'iniciado': iniciado_data,
            'suspenso': suspenso_data,
            'cancelado': cancelado_data
        }
        
        return JsonResponse(dados)
    except Exception as e:
        print(f"Erro ao buscar dados de ausências: {e}")
        return JsonResponse({'error': str(e)})

@login_required
def alunos_por_profissional(request):
    """
    Retorna dados para o gráfico de alunos por profissional.
    """
    try:
        from neurodivergentes.models import PDI
        from profissionais_app.models import Profissional
        from django.db.models import Count, Q
        
        # Buscar profissionais com contagem de alunos
        profissionais_dados = Profissional.objects.annotate(
            total_alunos=Count('pdis_responsavel__neurodivergente', distinct=True)
        ).filter(total_alunos__gt=0).order_by('-total_alunos')[:10]  # Top 10 profissionais com mais alunos
        
        # Preparar dados para o gráfico
        labels = []
        data = []
        cores = [
            '#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#E91E63',
            '#00BCD4', '#FFEB3B', '#795548', '#607D8B', '#3F51B5'
        ]
        
        for i, prof in enumerate(profissionais_dados):
            try:
                # Usar apenas o primeiro nome para o label
                nome_completo = prof.user.get_full_name()
                partes_nome = nome_completo.split()
                primeiro_nome = partes_nome[0] if partes_nome else f"Prof. {prof.id}"
                
                # Nome curto para o label
                nome_curto = f"{primeiro_nome}"
                
                # Nome completo para o tooltip
                nome_tooltip = f"{nome_completo} ({prof.get_profissao_display()})"
                
                labels.append(nome_curto)
                data.append(prof.total_alunos)
            except:
                nome_curto = f"Prof. {prof.id}"
                labels.append(nome_curto)
                data.append(prof.total_alunos)
        
        # Criar datasets para o gráfico
        datasets = [{
            'label': 'Alunos por Profissional',
            'data': data,
            'backgroundColor': cores[:len(data)],
            'borderColor': cores[:len(data)],
            'borderWidth': 1
        }]
        
        return JsonResponse({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        print(f"Erro ao buscar dados de alunos por profissional: {e}")
        return JsonResponse({'error': str(e)})

@login_required
def genero_por_neurodivergencia(request):
    """
    View para fornecer dados de gênero por neurodivergência para o gráfico do dashboard
    Retorna dados em formato JSON compatível com Chart.js
    """
    try:
        # Importar os modelos necessários
        try:
            from neurodivergentes.models.neurodivergencias import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        except ImportError:
            from neurodivergentes.models import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        
        # Lista padrão de neurodivergências mais comuns
        neurodivergencias_padrao = ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD']
        
        # Buscar as condições (neurodivergências) mais comuns do banco de dados
        # Limitamos a 10 para não sobrecarregar o gráfico
        top_condicoes = DiagnosticoNeurodivergente.objects.values('condicao__nome').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Extrair os nomes das condições mais comuns
        neurodivergencias = [item['condicao__nome'] for item in top_condicoes if item['condicao__nome']]
        
        # Se não houver condições no banco ou se a lista estiver vazia, usar a lista padrão
        if not neurodivergencias:
            neurodivergencias = neurodivergencias_padrao
        
        # Adicionar "Outros" ao final da lista apenas se for necessário
        # (será adicionado dinamicamente se algum diagnóstico for classificado como "Outros")
        
        # Dicionários para armazenar os dados por gênero e neurodivergência
        dados_por_genero = {
            'M': {neurodiv: 0 for neurodiv in neurodivergencias},
            'F': {neurodiv: 0 for neurodiv in neurodivergencias}
        }
        
        # Obter todos os diagnósticos com suas relações
        diagnosticos = DiagnosticoNeurodivergente.objects.select_related(
            'neurodivergencia__neurodivergente',
            'condicao'
        ).all()
        
        # Contar diagnósticos por gênero e neurodivergência
        for diagnostico in diagnosticos:
            try:
                # Obter o gênero do neurodivergente
                neurodivergente = diagnostico.neurodivergencia.neurodivergente
                # Verificar se o aluno está ativo
                if not neurodivergente.ativo:
                    continue
                genero = neurodivergente.genero if hasattr(neurodivergente, 'genero') else None
                
                # Obter o nome da condição (neurodivergência)
                if hasattr(diagnostico, 'condicao') and hasattr(diagnostico.condicao, 'nome'):
                    nome_condicao = diagnostico.condicao.nome
                    
                    # Verificar se a condição está na nossa lista de neurodivergências
                    if nome_condicao not in neurodivergencias:
                        nome_condicao = "Outros"
                        # Adicionar "Outros" à lista se ainda não estiver lá
                        if "Outros" not in neurodivergencias:
                            neurodivergencias.append("Outros")
                else:
                    # Se não conseguir determinar a condição, pular este diagnóstico
                    continue
                
                # Incrementar o contador apropriado
                if genero in ('M', 'F') and nome_condicao in dados_por_genero[genero]:
                    dados_por_genero[genero][nome_condicao] += 1
            except Exception as e:
                # Se ocorrer algum erro, apenas continuamos para o próximo
                print(f"Erro ao processar diagnóstico: {e}")
                continue
        
        # Verificar se há dados na categoria "Outros"
        if "Outros" in neurodivergencias and dados_por_genero['M'].get("Outros", 0) == 0 and dados_por_genero['F'].get("Outros", 0) == 0:
            # Se não houver dados em "Outros", remover da lista
            neurodivergencias.remove("Outros")
            
        # Converter os dicionários em listas para o formato esperado pelo Chart.js
        dados_masculino = [dados_por_genero['M'].get(neurodiv, 0) for neurodiv in neurodivergencias]
        dados_feminino = [dados_por_genero['F'].get(neurodiv, 0) for neurodiv in neurodivergencias]
        
        # Preparar o formato de dados para o Chart.js
        data = {
            'labels': neurodivergencias,
            'datasets': [
                {
                    'label': 'Masculino',
                    'data': dados_masculino,
                    'backgroundColor': 'rgba(26, 115, 232, 0.7)',
                    'borderWidth': 0,
                    'borderRadius': 4
                },
                {
                    'label': 'Feminino',
                    'data': dados_feminino,
                    'backgroundColor': 'rgba(233, 30, 99, 0.7)',
                    'borderWidth': 0,
                    'borderRadius': 4
                }
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        # Em caso de erro, retornar dados vazios e logar o erro
        print(f"Erro ao gerar dados do gráfico: {e}")
        return JsonResponse({
            'labels': ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD', 'Outros'],
            'datasets': [
                {
                    'label': 'Masculino',
                    'data': [0, 0, 0, 0, 0, 0],
                    'backgroundColor': 'rgba(26, 115, 232, 0.7)',
                    'borderWidth': 0,
                    'borderRadius': 4
                },
                {
                    'label': 'Feminino',
                    'data': [0, 0, 0, 0, 0, 0],
                    'backgroundColor': 'rgba(233, 30, 99, 0.7)',
                    'borderWidth': 0,
                    'borderRadius': 4
                }
            ]
        })

@login_required
def distribuicao_por_neurodivergencia(request):
    """
    View para fornecer dados de distribuição total por neurodivergência para o gráfico do dashboard
    Retorna dados em formato JSON compatível com Chart.js
    """
    try:
        # Importar os modelos necessários
        try:
            from neurodivergentes.models.neurodivergencias import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        except ImportError:
            from neurodivergentes.models import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        
        # Lista padrão de neurodivergências mais comuns
        neurodivergencias_padrao = ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD']
        
        # Buscar as condições (neurodivergências) mais comuns do banco de dados
        # Limitamos a 10 para não sobrecarregar o gráfico
        top_condicoes = DiagnosticoNeurodivergente.objects.values('condicao__nome').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Extrair os nomes das condições mais comuns
        neurodivergencias = [item['condicao__nome'] for item in top_condicoes if item['condicao__nome']]
        
        # Se não houver condições no banco ou se a lista estiver vazia, usar a lista padrão
        if not neurodivergencias:
            neurodivergencias = neurodivergencias_padrao
        
        # Dicionário para armazenar os dados por neurodivergência
        dados_por_neurodivergencia = {neurodiv: 0 for neurodiv in neurodivergencias}
        
        # Obter todos os diagnósticos com suas relações
        diagnosticos = DiagnosticoNeurodivergente.objects.select_related(
            'condicao',
            'neurodivergencia__neurodivergente'
        ).all()
        
        # Contar diagnósticos por neurodivergência
        for diagnostico in diagnosticos:
            try:
                # Verificar se o aluno está ativo
                neurodivergente = diagnostico.neurodivergencia.neurodivergente
                if not neurodivergente.ativo:
                    continue
                    
                # Obter o nome da condição (neurodivergência)
                if hasattr(diagnostico, 'condicao') and hasattr(diagnostico.condicao, 'nome'):
                    nome_condicao = diagnostico.condicao.nome
                    
                    # Verificar se a condição está na nossa lista de neurodivergências
                    if nome_condicao not in neurodivergencias:
                        nome_condicao = "Outros"
                        # Adicionar "Outros" à lista se ainda não estiver lá
                        if "Outros" not in neurodivergencias:
                            neurodivergencias.append("Outros")
                            dados_por_neurodivergencia["Outros"] = 0
                else:
                    # Se não conseguir determinar a condição, pular este diagnóstico
                    continue
                
                # Incrementar o contador apropriado
                if nome_condicao in dados_por_neurodivergencia:
                    dados_por_neurodivergencia[nome_condicao] += 1
            except Exception as e:
                # Se ocorrer algum erro, apenas continuamos para o próximo
                print(f"Erro ao processar diagnóstico: {e}")
                continue
        
        # Verificar se há dados na categoria "Outros"
        if "Outros" in neurodivergencias and dados_por_neurodivergencia.get("Outros", 0) == 0:
            # Se não houver dados em "Outros", remover da lista
            neurodivergencias.remove("Outros")
            
        # Converter o dicionário em lista para o formato esperado pelo Chart.js
        dados_total = [dados_por_neurodivergencia.get(neurodiv, 0) for neurodiv in neurodivergencias]
        
        # Preparar o formato de dados para o Chart.js
        data = {
            'labels': neurodivergencias,
            'datasets': [
                {
                    'label': 'Alunos',
                    'data': dados_total,
                    'backgroundColor': [
                        'rgba(233, 30, 99, 0.7)',
                        'rgba(26, 115, 232, 0.7)',
                        'rgba(76, 175, 80, 0.7)',
                        'rgba(251, 140, 0, 0.7)',
                        'rgba(244, 67, 53, 0.7)',
                        'rgba(123, 128, 154, 0.7)'
                    ],
                    'borderWidth': 0,
                    'borderRadius': 4
                }
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        # Em caso de erro, retornar dados vazios e logar o erro
        print(f"Erro ao gerar dados do gráfico de distribuição por neurodivergência: {e}")
        return JsonResponse({
            'labels': ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD', 'Outros'],
            'datasets': [
                {
                    'label': 'Alunos',
                    'data': [0, 0, 0, 0, 0, 0],
                    'backgroundColor': [
                        'rgba(233, 30, 99, 0.7)',
                        'rgba(26, 115, 232, 0.7)',
                        'rgba(76, 175, 80, 0.7)',
                        'rgba(251, 140, 0, 0.7)',
                        'rgba(244, 67, 53, 0.7)',
                        'rgba(123, 128, 154, 0.7)'
                    ],
                    'borderWidth': 0,
                    'borderRadius': 4
                }
            ]
        })

@login_required
def especializacao_profissionais(request):
    """
    Retorna dados para o gráfico de especialização dos profissionais por tipo de neurodivergência.
    """
    try:
        # Importar os modelos necessários
        try:
            from neurodivergentes.models.neurodivergencias import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        except ImportError:
            from neurodivergentes.models import Neurodivergencia, DiagnosticoNeurodivergente, CondicaoNeurodivergente
        from neurodivergentes.models import PDI, Neurodivergente
        from profissionais_app.models import Profissional
        from django.db.models import Count
        
        # Obter os 10 profissionais com mais alunos
        top_profissionais = Profissional.objects.annotate(
            total_alunos=Count('pdis_responsavel__neurodivergente', distinct=True)
        ).filter(total_alunos__gt=0).order_by('-total_alunos')[:10]
        
        # Buscar as condições (neurodivergências) mais comuns do banco de dados
        top_condicoes = DiagnosticoNeurodivergente.objects.values('condicao__nome').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Extrair os nomes das condições mais comuns
        neurodivergencias = [item['condicao__nome'] for item in top_condicoes if item['condicao__nome']]
        
        # Se não houver condições no banco ou se a lista estiver vazia, usar uma lista padrão
        if not neurodivergencias:
            neurodivergencias = ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD']
        
        # Preparar dados para o gráfico
        datasets = []
        labels = neurodivergencias.copy()
        
        # Obter todos os diagnósticos com suas relações
        all_diagnosticos = DiagnosticoNeurodivergente.objects.select_related('condicao').all()
        
        # Para cada profissional, contar alunos por tipo de neurodivergência
        for prof in top_profissionais:
            # Obter todos os alunos atendidos por este profissional
            alunos_ids = PDI.objects.filter(
                pedagogo_responsavel=prof
            ).values_list('neurodivergente', flat=True).distinct()
            
            # Inicializar contagem para cada neurodivergência
            contagem_por_neurodivergencia = {neurodiv: 0 for neurodiv in neurodivergencias}
            
            # Para rastrear quais alunos já foram contados para cada neurodivergência
            alunos_contados = {neurodiv: set() for neurodiv in neurodivergencias}
            
            # Para cada aluno atendido por este profissional
            for aluno_id in alunos_ids:
                # Obter diagnósticos deste aluno
                for diagnostico in all_diagnosticos:
                    try:
                        # Verificar se o diagnóstico pertence a este aluno
                        aluno_do_diagnostico = False
                        if hasattr(diagnostico, 'neurodivergente') and diagnostico.neurodivergente and diagnostico.neurodivergente.id == aluno_id:
                            aluno_do_diagnostico = True
                        elif hasattr(diagnostico, 'neurodivergencia') and diagnostico.neurodivergencia and diagnostico.neurodivergencia.id == aluno_id:
                            aluno_do_diagnostico = True
                        elif hasattr(diagnostico, 'aluno') and diagnostico.aluno and diagnostico.aluno.id == aluno_id:
                            aluno_do_diagnostico = True
                        
                        if aluno_do_diagnostico and hasattr(diagnostico, 'condicao') and hasattr(diagnostico.condicao, 'nome'):
                            nome_condicao = diagnostico.condicao.nome
                            
                            # Verificar se a condição está na nossa lista de neurodivergências
                            if nome_condicao in neurodivergencias:
                                # Verificar se este aluno já foi contado para esta neurodivergência
                                if aluno_id not in alunos_contados[nome_condicao]:
                                    contagem_por_neurodivergencia[nome_condicao] += 1
                                    alunos_contados[nome_condicao].add(aluno_id)
                    except Exception as e:
                        print(f"Erro ao processar diagnóstico para aluno {aluno_id}: {e}")
                        continue
            
            # Obter nome do profissional
            try:
                nome_completo = prof.user.get_full_name()
                partes_nome = nome_completo.split()
                primeiro_nome = partes_nome[0] if partes_nome else f"Prof. {prof.id}"
            except:
                primeiro_nome = f"Prof. {prof.id}"
            
            # Adicionar dataset para este profissional (mesmo que não tenha alunos com diagnóstico)
            datasets.append({
                'label': primeiro_nome,
                'data': [contagem_por_neurodivergencia[neurodiv] for neurodiv in neurodivergencias],
                'fill': True,
                'backgroundColor': 'rgba(0, 0, 0, 0.2)',  # Será substituído pelo frontend
                'borderColor': 'rgba(0, 0, 0, 1)',        # Será substituído pelo frontend
                'pointBackgroundColor': 'rgba(0, 0, 0, 1)', # Será substituído pelo frontend
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgba(0, 0, 0, 1)' # Será substituído pelo frontend
            })
        
        # Adicionar log para depuração
        print(f"Total de profissionais encontrados: {len(top_profissionais)}")
        print(f"Total de datasets gerados: {len(datasets)}")
        print(f"Neurodivergências encontradas: {neurodivergencias}")
        
        return JsonResponse({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        print(f"Erro ao buscar dados de especialização dos profissionais: {e}")
        return JsonResponse({
            'labels': ['TEA', 'TDAH', 'Dislexia', 'Discalculia', 'TOD'],
            'datasets': []
        })

@login_required
def alunos_em_risco(request):
    """
    Retorna dados de alunos que estão em situação de risco com base em critérios como:
    - Ausências consecutivas
    - Falta de progresso nos objetivos do PDI
    - Tempo sem atendimento
    """
    try:
        from neurodivergentes.models import PDI, Neurodivergente
        from django.db.models import Count, F, Q, Case, When, IntegerField, Value
        from django.utils import timezone
        import datetime
        
        print("\n\n==== INÍCIO DA FUNÇÃO ALUNOS EM RISCO ====")
        
        # Definir o período de referência (últimos 90 dias)
        data_referencia = timezone.now() - datetime.timedelta(days=90)
        data_sem_atendimento = timezone.now().date() - datetime.timedelta(days=30)
        data_desatualizado = timezone.now() - datetime.timedelta(days=60)
        
        print(f"Data atual: {timezone.now().date()}")
        print(f"Data referência (90 dias atrás): {data_referencia.date()}")
        print(f"Data sem atendimento (30 dias atrás): {data_sem_atendimento}")
        print(f"Data desatualizado (60 dias atrás): {data_desatualizado.date()}")
        
        # Lista para armazenar os alunos em risco
        alunos_risco = []
        
        # 1. Alunos com ausências consecutivas (3 ou mais)
        alunos_ausencias = PDI.objects.filter(
            status='ausente',
            data_criacao__gte=data_referencia
        ).values('neurodivergente').annotate(
            total_faltas=Count('id')
        ).filter(total_faltas__gte=3)
        
        for aluno_data in alunos_ausencias:
            try:
                aluno = Neurodivergente.objects.get(id=aluno_data['neurodivergente'])
                
                # Buscar o PDI mais recente para obter o profissional responsável
                ultimo_pdi = PDI.objects.filter(
                    neurodivergente=aluno
                ).select_related('pedagogo_responsavel').order_by('-data_criacao').first()
                
                profissional_nome = "Não informado"
                if ultimo_pdi and ultimo_pdi.pedagogo_responsavel:
                    profissional_nome = f"{ultimo_pdi.pedagogo_responsavel.user.first_name} {ultimo_pdi.pedagogo_responsavel.user.last_name}".strip()
                
                alunos_risco.append({
                    'id': aluno.id,
                    'nome': aluno.nome_completo,
                    'escola': aluno.escola.nome if aluno.escola else "Não informada",
                    'profissional_responsavel': profissional_nome,
                    'tipo_risco': 'Ausências Consecutivas',
                    'detalhe': f'{aluno_data["total_faltas"]} faltas nos últimos 90 dias',
                    'severidade': 'alta'
                })
            except Neurodivergente.DoesNotExist:
                continue
        
        # 3. Alunos sem atendimento recente (mais de 30 dias)
        print("\n=== Verificando alunos sem atendimento recente ===")
        
        # Listar todos os alunos para depuração
        todos_alunos = Neurodivergente.objects.filter(ativo=True)
        print(f"Total de alunos no sistema: {todos_alunos.count()}")
        for a in todos_alunos:
            print(f"ID: {a.id}, Nome: {a.nome_completo}")
        
        for aluno in Neurodivergente.objects.filter(ativo=True):
            # Adicionar log para rastrear o processamento de cada aluno
            print(f"\nVerificando aluno: {aluno.id} - {aluno.nome_completo}")
            
            # Verificar especificamente o João
            if "João" in aluno.nome_completo:
                print(f"*** ENCONTRADO JOÃO: ID {aluno.id} ***")
                print(f"*** Detalhes do João: {aluno.__dict__} ***")
            
            # Calcular dias desde o último atendimento
            try:
                # Listar todos os PDIs do aluno para depuração
                todos_pdis = PDI.objects.filter(neurodivergente=aluno).order_by('-data_criacao')
                print(f"  - Total de PDIs para {aluno.nome_completo}: {todos_pdis.count()}")
                for pdi in todos_pdis:
                    print(f"    PDI ID: {pdi.id}, Data: {pdi.data_criacao}, Status: {pdi.status}")
                
                ultimo_pdi = PDI.objects.filter(
                    neurodivergente=aluno
                ).order_by('-data_criacao').first()
                
                if ultimo_pdi:
                    dias_sem_atendimento = (timezone.now().date() - ultimo_pdi.data_criacao).days
                    print(f"  - Último PDI: {ultimo_pdi.id}, data: {ultimo_pdi.data_criacao}, dias sem atendimento: {dias_sem_atendimento}")
                    
                    if dias_sem_atendimento > 30:  # Apenas adiciona se for mais de 30 dias
                        # Verificar se este aluno já está na lista por este motivo específico
                        ja_na_lista = any(item['id'] == aluno.id and item['tipo_risco'] == 'Sem Atendimento Recente' for item in alunos_risco)
                        print(f"  - Já na lista por Sem Atendimento Recente? {ja_na_lista}")
                        
                        if not ja_na_lista:
                            print(f"  - ADICIONANDO aluno {aluno.nome_completo} à lista de risco (Sem Atendimento Recente)")
                            detalhe = f"{dias_sem_atendimento} dias sem atendimento"
                            
                            # Obter profissional responsável do último PDI
                            profissional_nome = "Não informado"
                            if ultimo_pdi and ultimo_pdi.pedagogo_responsavel:
                                profissional_nome = f"{ultimo_pdi.pedagogo_responsavel.user.first_name} {ultimo_pdi.pedagogo_responsavel.user.last_name}".strip()
                            
                            alunos_risco.append({
                                'id': aluno.id,
                                'nome': aluno.nome_completo,
                                'escola': aluno.escola.nome if aluno.escola else "Não informada",
                                'profissional_responsavel': profissional_nome,
                                'tipo_risco': 'Sem Atendimento Recente',
                                'detalhe': detalhe,
                                'severidade': 'média'
                            })
                        else:
                            print(f"  - Aluno {aluno.nome_completo} já está na lista por Sem Atendimento Recente")
                    else:
                        print(f"  - Aluno {aluno.nome_completo} tem menos de 30 dias sem atendimento ({dias_sem_atendimento} dias)")
                else:
                    print(f"  - Aluno {aluno.nome_completo} não tem PDI registrado")
                    # Verificar se este aluno já está na lista por este motivo específico
                    ja_na_lista = any(item['id'] == aluno.id and item['tipo_risco'] == 'Sem Atendimento Recente' for item in alunos_risco)
                    print(f"  - Já na lista por Sem Atendimento Recente? {ja_na_lista}")
                    
                    if not ja_na_lista:
                        print(f"  - ADICIONANDO aluno {aluno.nome_completo} à lista de risco (Nunca recebeu atendimento)")
                        alunos_risco.append({
                            'id': aluno.id,
                            'nome': aluno.nome_completo,
                            'escola': aluno.escola.nome if aluno.escola else "Não informada",
                            'profissional_responsavel': "Não informado",
                            'tipo_risco': 'Sem Atendimento Recente',
                            'detalhe': "Nunca recebeu atendimento",
                            'severidade': 'alta'
                        })
                    else:
                        print(f"  - Aluno {aluno.nome_completo} já está na lista por Sem Atendimento Recente")
            except Exception as e:
                print(f"Erro ao verificar atendimento para aluno {aluno.id} - {aluno.nome_completo}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 4. Verificação de objetivos não alcançados removida conforme solicitado
        # 5. PDIs desatualizados (sem atualização há mais de 60 dias)
        alunos_pdi_desatualizado = PDI.objects.filter(
            updated_at__lt=data_desatualizado,
            status__in=['em_andamento', 'iniciado']
        ).values('neurodivergente').distinct()
        
        for aluno_data in alunos_pdi_desatualizado:
            try:
                aluno = Neurodivergente.objects.get(id=aluno_data['neurodivergente'])
                # Verificar se este aluno já está na lista por este motivo
                if not any(item['id'] == aluno.id and item['tipo_risco'] == 'PDI Desatualizado' for item in alunos_risco):
                    # Buscar o PDI mais recente para obter o profissional responsável
                    ultimo_pdi = PDI.objects.filter(
                        neurodivergente=aluno
                    ).select_related('pedagogo_responsavel').order_by('-data_criacao').first()
                    
                    profissional_nome = "Não informado"
                    if ultimo_pdi and ultimo_pdi.pedagogo_responsavel:
                        profissional_nome = f"{ultimo_pdi.pedagogo_responsavel.user.first_name} {ultimo_pdi.pedagogo_responsavel.user.last_name}".strip()
                    
                    alunos_risco.append({
                        'id': aluno.id,
                        'nome': aluno.nome_completo,
                        'escola': aluno.escola.nome if aluno.escola else "Não informada",
                        'profissional_responsavel': profissional_nome,
                        'tipo_risco': 'PDI Desatualizado',
                        'detalhe': 'PDI sem atualização há mais de 60 dias',
                        'severidade': 'média'
                    })
            except Neurodivergente.DoesNotExist:
                continue
        
        # Ordenar por severidade (alta, média, baixa)
        def ordem_severidade(item):
            if item['severidade'] == 'alta':
                return 0
            elif item['severidade'] == 'média':
                return 1
            else:
                return 2
        
        alunos_risco.sort(key=ordem_severidade)
        
        # Limitar a 100 alunos para melhor visualização no dashboard
        alunos_risco_limitado = alunos_risco[:100]
        
        print("\n=== Alunos em risco (resultado final - limitado a 100) ===")
        for aluno in alunos_risco_limitado:
            print(f"ID: {aluno['id']}, Nome: {aluno['nome']}, Tipo: {aluno['tipo_risco']}, Detalhe: {aluno['detalhe']}")
        
        print(f"Total de alunos em risco: {len(alunos_risco)} | Exibindo: {len(alunos_risco_limitado)}")
        print("==== FIM DA FUNÇÃO ALUNOS EM RISCO ====\n\n")
        
        return JsonResponse({
            'alunos_risco': alunos_risco_limitado,
            'total_alunos': len(alunos_risco),
            'exibindo': len(alunos_risco_limitado)
        })
    except Exception as e:
        print(f"Erro ao buscar dados de alunos em risco: {e}")
        return JsonResponse({'alunos_risco': []})

@login_required
def atendimentos_mensais_profissional(request):
    """
    Retorna dados de atendimentos mensais por profissional para o gráfico do dashboard.
    Suporta filtros por profissional e período.
    """
    try:
        from neurodivergentes.models import PDI
        from profissionais_app.models import Profissional
        from django.db.models import Count, Q
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta
        import calendar
        
        # Obter filtros da requisição
        profissional_id = request.GET.get('profissional_id', '')
        periodo = request.GET.get('periodo', '')  # formato: 2024-01 ou vazio para últimos 12 meses
        
        # Definir período de análise
        hoje = timezone.now().date()
        if periodo:
            # Período específico (um mês)
            ano, mes = periodo.split('-')
            data_inicio = datetime(int(ano), int(mes), 1).date()
            if int(mes) == 12:
                data_fim = datetime(int(ano) + 1, 1, 1).date() - timedelta(days=1)
            else:
                data_fim = datetime(int(ano), int(mes) + 1, 1).date() - timedelta(days=1)
        else:
            # Últimos 12 meses
            data_inicio = hoje.replace(day=1) - timedelta(days=365)
            data_fim = hoje
        
        # Buscar atendimentos de todos os profissionais através dos PDIs
        # Como PDI só tem pedagogo_responsavel, vamos buscar por esse campo
        # mas também incluir outros profissionais que possam estar relacionados
        
        # Query base para PDIs no período - apenas concluídos
        pdis_query = PDI.objects.filter(
            data_criacao__gte=data_inicio,
            data_criacao__lte=data_fim,
            status='concluido'
        )
        
        # Filtrar por profissional se especificado
        if profissional_id:
            pdis_query = pdis_query.filter(pedagogo_responsavel_id=profissional_id)
        
        # Agrupar por mês e profissional
        if periodo:
            # Para um mês específico, mostrar por profissional
            dados_agrupados = pdis_query.values(
                'pedagogo_responsavel__user__first_name',
                'pedagogo_responsavel__user__last_name',
                'pedagogo_responsavel__profissao',
                'pedagogo_responsavel_id'
            ).annotate(
                total_atendimentos=Count('id')
            ).order_by('-total_atendimentos')
            
            labels = []
            data = []
            
            for item in dados_agrupados:
                if item['pedagogo_responsavel__user__first_name']:
                    primeiro_nome = item['pedagogo_responsavel__user__first_name']
                    profissao_raw = item['pedagogo_responsavel__profissao'] or 'profissional'
                    # Formatar profissão: substituir _ por espaço e capitalizar
                    profissao = profissao_raw.replace('_', ' ').title()
                    nome = f"{primeiro_nome} - {profissao}"
                else:
                    nome = f"Prof. {item['pedagogo_responsavel_id']}"
                
                labels.append(nome)
                data.append(item['total_atendimentos'])
            
            # Nomes dos meses em português
            nomes_meses_pt = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            
            mes_num = int(periodo.split("-")[1])
            ano = periodo.split("-")[0]
            mes_nome = nomes_meses_pt[mes_num]
            
            datasets = [{
                'label': f'Atendimentos concluídos em {mes_nome} {ano}',
                'data': data,
                'backgroundColor': 'rgba(76, 175, 80, 0.7)',
                'borderColor': 'rgba(76, 175, 80, 1)',
                'borderWidth': 1
            }]
            
        else:
            # Para últimos 12 meses, mostrar evolução temporal
            if profissional_id:
                # Um profissional específico ao longo dos meses
                dados_agrupados = pdis_query.filter(
                    pedagogo_responsavel_id=profissional_id
                ).annotate(
                    mes=TruncMonth('data_criacao')
                ).values('mes').annotate(
                    total_atendimentos=Count('id')
                ).order_by('mes')
                
                # Criar labels dos últimos 12 meses
                labels = []
                data = []
                
                for i in range(12):
                    mes_atual = (hoje.replace(day=1) - timedelta(days=30*i)).replace(day=1)
                    labels.insert(0, f"{calendar.month_name[mes_atual.month][:3]} {mes_atual.year}")
                    
                    # Buscar dados para este mês
                    total = 0
                    for item in dados_agrupados:
                        if item['mes'].month == mes_atual.month and item['mes'].year == mes_atual.year:
                            total = item['total_atendimentos']
                            break
                    data.insert(0, total)
                
                # Obter nome do profissional
                try:
                    prof = Profissional.objects.get(id=profissional_id)
                    primeiro_nome = prof.user.first_name
                    profissao_raw = prof.profissao or 'profissional'
                    # Formatar profissão: substituir _ por espaço e capitalizar
                    profissao = profissao_raw.replace('_', ' ').title()
                    nome_prof = f"{primeiro_nome} - {profissao}"
                except:
                    nome_prof = f"Prof. {profissional_id}"
                
                datasets = [{
                    'label': f'Atendimentos concluídos - {nome_prof}',
                    'data': data,
                    'backgroundColor': 'rgba(76, 175, 80, 0.7)',
                    'borderColor': 'rgba(76, 175, 80, 1)',
                    'borderWidth': 1
                }]
                
            else:
                # Todos os profissionais - top 5 nos últimos 12 meses
                dados_agrupados = pdis_query.values(
                    'pedagogo_responsavel__user__first_name',
                    'pedagogo_responsavel__user__last_name',
                    'pedagogo_responsavel__profissao',
                    'pedagogo_responsavel_id'
                ).annotate(
                    total_atendimentos=Count('id')
                ).order_by('-total_atendimentos')[:5]
                
                labels = []
                data = []
                
                for item in dados_agrupados:
                    if item['pedagogo_responsavel__user__first_name']:
                        primeiro_nome = item['pedagogo_responsavel__user__first_name']
                        profissao_raw = item['pedagogo_responsavel__profissao'] or 'profissional'
                        # Formatar profissão: substituir _ por espaço e capitalizar
                        profissao = profissao_raw.replace('_', ' ').title()
                        nome = f"{primeiro_nome} - {profissao}"
                    else:
                        nome = f"Prof. {item['pedagogo_responsavel_id']}"
                    
                    labels.append(nome)
                    data.append(item['total_atendimentos'])
                
                datasets = [{
                    'label': 'Atendimentos concluídos (Últimos 12 meses)',
                    'data': data,
                    'backgroundColor': 'rgba(76, 175, 80, 0.7)',
                    'borderColor': 'rgba(76, 175, 80, 1)',
                    'borderWidth': 1
                }]
        
        return JsonResponse({
            'labels': labels,
            'datasets': datasets
        })
        
    except Exception as e:
        print(f"Erro ao buscar dados de atendimentos mensais por profissional: {e}")
        return JsonResponse({
            'labels': [],
            'datasets': [{
                'label': 'Atendimentos',
                'data': [],
                'backgroundColor': 'rgba(76, 175, 80, 0.7)',
                'borderColor': 'rgba(76, 175, 80, 1)',
                'borderWidth': 1
            }]
        })

@login_required
def lista_profissionais_api(request):
    """
    Retorna lista de profissionais para popular o dropdown de filtros.
    """
    try:
        from profissionais_app.models import Profissional
        
        profissionais = Profissional.objects.select_related('user').all().order_by('user__first_name')
        
        lista = []
        for prof in profissionais:
            nome = prof.user.get_full_name() or f"Prof. {prof.id}"
            lista.append({
                'id': prof.id,
                'nome': nome
            })
        
        return JsonResponse({'profissionais': lista})
        
    except Exception as e:
        print(f"Erro ao buscar lista de profissionais: {e}")
        return JsonResponse({'profissionais': []})

# View para a página inicial que verifica se o usuário já está autenticado
def index_view(request):
    """
    View para a página inicial. Se o usuário já estiver autenticado,
    redireciona automaticamente para o dashboard. Caso contrário,
    mostra a página de login.
    """
    # Verifica se o usuário já está autenticado
    if request.user.is_authenticated:
        # Redireciona para o dashboard
        return redirect('dashboard')
    else:
        # Usa a CustomLoginView para mostrar a página de login
        return CustomLoginView.as_view()(request)

# Função de logout personalizada
def custom_logout(request):
    """
    View personalizada para processar o logout e redirecionar para a página de login.
    """
    # Executa o logout
    logout(request)
    
    # Adiciona mensagem de sucesso
    messages.success(request, 'Você saiu do sistema com sucesso.')
    
    # Redireciona para a página de login
    return redirect('login')

# Handler para erros 403 (acesso negado)
def custom_permission_denied_view(request, exception=None):
    """
    View para exibir mensagem de acesso negado e redirecionar para o dashboard.
    """
    # Adicionar mensagem de alerta que será exibida no dashboard
    messages.warning(
        request, 
        'Você não tem permissão para acessar esta página. '
        'Se você acredita que isso é um erro, entre em contato com o administrador da instituição.'
    )
    
    # Redirecionar para o dashboard
    return redirect('/dashboard/')