from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from datetime import datetime
import json

from .models import Agendamento
from .permissions import (
    require_agenda_access, require_create_permission,
    can_edit_agendamento, can_delete_agendamento,
    get_user_permissions, is_profissional
)
from neurodivergentes.models import Neurodivergente
from profissionais_app.models import Profissional


@login_required
@require_agenda_access
def calendario_view(request):
    """
    View principal do calendário de agendamentos
    """
    permissions = get_user_permissions(request.user)
    
    # Buscar todos os pacientes e profissionais para popular os selects
    pacientes = Neurodivergente.objects.all().order_by('primeiro_nome', 'ultimo_nome')
    profissionais = Profissional.objects.all().select_related('user').order_by('user__first_name', 'user__last_name')
    
    context = {
        'title': 'Agenda',
        'permissions': permissions,
        'user_is_admin': permissions['is_gestor_or_admin'],
        'pacientes': pacientes,
        'profissionais': profissionais,
    }
    return render(request, 'agendamento/calendario.html', context)


@login_required
@require_agenda_access
def eventos_api(request):
    """
    API que retorna os eventos do calendário em formato JSON
    """
    try:
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        # Busca todos os agendamentos
        agendamentos = Agendamento.objects.all()
        
        # Filtra por período se fornecido
        if start and end:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
            agendamentos = agendamentos.filter(
                data_hora_inicio__range=[start_date, end_date]
            )
        
        # Converte para formato do FullCalendar
        eventos = []
        for agendamento in agendamentos:
            if agendamento.data_hora_inicio:  # Só inclui se tiver data/hora
                # Definir título incluindo descrição quando disponível, mantendo profissional e paciente
                profissional_nome = agendamento.profissional.user.get_full_name()
                paciente_nome = agendamento.neurodivergente.nome_completo if agendamento.neurodivergente else None
                descricao = agendamento.descricao
                
                # Truncar descrição longa para o calendário
                descricao_truncada = descricao[:30] + "..." if descricao and len(descricao) > 30 else descricao
                
                if paciente_nome and descricao_truncada:
                    titulo = f"{profissional_nome} - {paciente_nome} - {descricao_truncada}"
                elif paciente_nome:
                    titulo = f"{profissional_nome} - {paciente_nome}"
                elif descricao_truncada:
                    titulo = f"{profissional_nome} - {descricao_truncada}"
                else:
                    titulo = f"{profissional_nome} - Agendamento"
                
                evento = {
                    'id': agendamento.id,
                    'title': titulo,
                    'start': agendamento.data_hora_inicio.isoformat(),
                    'end': agendamento.data_hora_fim.isoformat() if agendamento.data_hora_fim else None,
                    'backgroundColor': agendamento.get_cor_status(),
                    'borderColor': agendamento.get_cor_status(),
                    'extendedProps': {
                        'profissional': str(agendamento.profissional),
                        'profissional_id': agendamento.profissional.id,
                        'paciente': str(agendamento.neurodivergente) if agendamento.neurodivergente else None,
                        'paciente_id': agendamento.neurodivergente.id if agendamento.neurodivergente else None,
                        'descricao': agendamento.descricao,
                        'observacoes': agendamento.observacoes,
                        'status': agendamento.get_status_display(),
                        'status_key': agendamento.status,
                        'duracao': agendamento.duracao_real,
                        'recorrencia': agendamento.get_recorrencia_display() if agendamento.recorrencia else None,
                        'can_edit': can_edit_agendamento(request.user, agendamento),
                        'can_delete': can_delete_agendamento(request.user, agendamento),
                    }
                }
                eventos.append(evento)
        
        return JsonResponse(eventos, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_create_permission
def criar_agendamento_api(request):
    """
    API para criar novo agendamento
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"DEBUG - Dados recebidos: {data}")  # Debug temporário
        
        # Determina o profissional baseado nas permissões
        if (request.user.is_superuser or request.user.is_staff or 
            request.user.has_perm('agendamento.can_manage_all_schedules')):
            # Admin/gestor/pessoa designada pode criar para qualquer profissional
            if data.get('profissional_id'):
                try:
                    profissional = Profissional.objects.get(id=data['profissional_id'])
                except Profissional.DoesNotExist:
                    return JsonResponse({'error': 'Profissional não encontrado'}, status=404)
            else:
                # Se não especificado e o usuário é profissional, usa ele mesmo
                try:
                    profissional = request.user.profissional
                except:
                    return JsonResponse({'error': 'Profissional deve ser especificado'}, status=400)
        else:
            # Profissional só pode criar para si mesmo
            try:
                profissional = request.user.profissional
            except:
                return JsonResponse({'error': 'Profissional não encontrado'}, status=404)
        
        # Cria o agendamento
        agendamento_data = {
            'profissional': profissional,
            'criado_por': request.user,
        }
        
        # Campos opcionais
        if data.get('neurodivergente_id'):
            try:
                neurodivergente = Neurodivergente.objects.get(id=data['neurodivergente_id'])
                agendamento_data['neurodivergente'] = neurodivergente
            except Neurodivergente.DoesNotExist:
                return JsonResponse({'error': 'Paciente não encontrado'}, status=404)
        
        if data.get('data_hora_inicio'):
            # Converter formato brasileiro dd/mm/yyyy HH:MM para datetime
            try:
                # Tentar formato ISO primeiro (para compatibilidade)
                agendamento_data['data_hora_inicio'] = datetime.fromisoformat(data['data_hora_inicio'])
            except ValueError:
                # Se falhar, tentar formato brasileiro dd/mm/yyyy HH:MM
                agendamento_data['data_hora_inicio'] = datetime.strptime(data['data_hora_inicio'], '%d/%m/%Y %H:%M')
        
        if data.get('duracao'):
            agendamento_data['duracao_minutos'] = int(data['duracao'])
        else:
            agendamento_data['duracao_minutos'] = 60  # padrão
        
        if data.get('descricao'):
            agendamento_data['descricao'] = data['descricao']
        
        if data.get('observacoes'):
            agendamento_data['observacoes'] = data['observacoes']
        
        if data.get('recorrencia'):
            agendamento_data['recorrencia'] = data['recorrencia']
        
        agendamento_data['enviar_copia_gestor'] = data.get('enviar_copia', False)
        
        agendamento = Agendamento.objects.create(**agendamento_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Agendamento criado com sucesso',
            'agendamento_id': agendamento.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def editar_agendamento_api(request, agendamento_id):
    """
    API para editar agendamento existente
    """
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        print(f"DEBUG - Buscando agendamento ID: {agendamento_id}")
        agendamento = Agendamento.objects.get(id=agendamento_id)
        print(f"DEBUG - Agendamento encontrado: {agendamento}")
        print(f"DEBUG - Tenant ID atual: {getattr(agendamento, 'tenant_id', 'N/A')}")
        
        # Verifica permissões usando o sistema de permissões
        if not can_edit_agendamento(request.user, agendamento):
            return JsonResponse({'error': 'Sem permissão para editar este agendamento'}, status=403)
        
        data = json.loads(request.body)
        print(f"DEBUG - Dados recebidos: {data}")
        
        # Atualiza profissional se permitido
        if ('profissional_id' in data and 
            (request.user.is_superuser or request.user.is_staff or 
             request.user.has_perm('agendamento.can_manage_all_schedules'))):
            if data['profissional_id']:
                try:
                    profissional = Profissional.objects.get(id=data['profissional_id'])
                    agendamento.profissional = profissional
                except Profissional.DoesNotExist:
                    return JsonResponse({'error': 'Profissional não encontrado'}, status=404)
        
        # Atualiza campos opcionais
        if 'neurodivergente_id' in data:
            if data['neurodivergente_id']:
                try:
                    neurodivergente = Neurodivergente.objects.get(id=data['neurodivergente_id'])
                    agendamento.neurodivergente = neurodivergente
                except Neurodivergente.DoesNotExist:
                    return JsonResponse({'error': 'Paciente não encontrado'}, status=404)
            else:
                agendamento.neurodivergente = None
        
        if 'data_hora_inicio' in data:
            if data['data_hora_inicio']:
                # Converter formato brasileiro dd/mm/yyyy HH:MM para datetime
                try:
                    # Tentar formato ISO primeiro (para compatibilidade)
                    agendamento.data_hora_inicio = datetime.fromisoformat(data['data_hora_inicio'])
                except ValueError:
                    # Se falhar, tentar formato brasileiro dd/mm/yyyy HH:MM
                    agendamento.data_hora_inicio = datetime.strptime(data['data_hora_inicio'], '%d/%m/%Y %H:%M')
            else:
                agendamento.data_hora_inicio = None
        
        if 'duracao' in data:
            agendamento.duracao_minutos = int(data['duracao']) if data['duracao'] else None
        
        if 'descricao' in data:
            agendamento.descricao = data['descricao']
        
        if 'observacoes' in data:
            agendamento.observacoes = data['observacoes']
        
        if 'recorrencia' in data:
            agendamento.recorrencia = data['recorrencia']
        
        if 'enviar_copia' in data:
            agendamento.enviar_copia_gestor = data['enviar_copia']
        
        # Definir tenant_id antes de salvar para evitar erro do TenantModelMixin
        if not hasattr(agendamento, 'tenant_id') or not agendamento.tenant_id:
            agendamento.tenant_id = 'default'
        
        print(f"DEBUG - Salvando agendamento com tenant_id: {agendamento.tenant_id}")
        
        # Usar update() em vez de save() para evitar problemas com TenantModelMixin
        Agendamento.objects.filter(id=agendamento_id).update(
            profissional=agendamento.profissional,
            neurodivergente=agendamento.neurodivergente,
            data_hora_inicio=agendamento.data_hora_inicio,
            duracao_minutos=agendamento.duracao_minutos,
            descricao=agendamento.descricao,
            observacoes=agendamento.observacoes,
            recorrencia=agendamento.recorrencia,
            enviar_copia_gestor=agendamento.enviar_copia_gestor
        )
        
        print("DEBUG - Agendamento atualizado com sucesso")
        
        return JsonResponse({
            'success': True,
            'message': 'Agendamento atualizado com sucesso'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def excluir_agendamento_api(request, agendamento_id):
    """
    API para excluir agendamento
    """
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        agendamento = get_object_or_404(Agendamento, id=agendamento_id)
        
        # Verifica permissões usando o sistema de permissões
        if not can_delete_agendamento(request.user, agendamento):
            return JsonResponse({'error': 'Sem permissão para excluir este agendamento'}, status=403)
        
        agendamento.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Agendamento excluído com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def buscar_pacientes_api(request):
    """
    API para buscar pacientes/alunos
    """
    termo = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    page_size = 10
    
    if len(termo) < 2:
        return JsonResponse({'results': [], 'total_count': 0})
    
    # Filtrar pacientes por nome (nome_completo é uma property, não um campo do DB)
    pacientes_query = Neurodivergente.objects.filter(
        Q(primeiro_nome__icontains=termo) |
        Q(ultimo_nome__icontains=termo)
    ).select_related('escola')
    
    total_count = pacientes_query.count()
    
    # Paginação
    start = (page - 1) * page_size
    end = start + page_size
    pacientes = pacientes_query[start:end]
    
    results = [
        {
            'id': p.id,
            'text': p.nome_completo,
            'escola': p.escola.nome if p.escola else ''
        }
        for p in pacientes
    ]
    
    return JsonResponse({
        'results': results,
        'total_count': total_count
    })


@login_required
def buscar_profissionais_api(request):
    """
    API para buscar profissionais de todas as fontes
    """
    from escola.models import Escola
    
    termo = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    page_size = 10
    
    results = []
    
    # 1. Buscar profissionais do app profissionais_app
    if len(termo) < 1:
        profissionais_app = Profissional.objects.all().select_related('user')
    else:
        profissionais_app = Profissional.objects.filter(
            Q(user__first_name__icontains=termo) |
            Q(user__last_name__icontains=termo) |
            Q(user__username__icontains=termo)
        ).select_related('user')
    
    for p in profissionais_app:
        results.append({
            'id': f'prof_{p.id}',
            'text': p.user.get_full_name() or p.user.username,
            'profissao': p.get_profissao_display() if p.profissao else 'Profissional'
        })
    
    # 2. Buscar profissionais de educação das escolas
    escolas = Escola.objects.all()
    for escola in escolas:
        for prof in escola.profissionais_educacao.all():
            if not termo or termo.lower() in (prof.user.get_full_name() or prof.user.username).lower():
                results.append({
                    'id': f'edu_{prof.id}',
                    'text': prof.user.get_full_name() or prof.user.username,
                    'profissao': prof.get_profissao_display() if prof.profissao else 'Educação'
                })
    
    # 3. Buscar profissionais de saúde das escolas
    for escola in escolas:
        for prof in escola.profissionais_saude.all():
            if not termo or termo.lower() in (prof.user.get_full_name() or prof.user.username).lower():
                results.append({
                    'id': f'saude_{prof.id}',
                    'text': prof.user.get_full_name() or prof.user.username,
                    'profissao': prof.get_profissao_display() if prof.profissao else 'Saúde'
                })
    
    # Remover duplicatas baseado no texto
    seen = set()
    unique_results = []
    for item in results:
        if item['text'] not in seen:
            seen.add(item['text'])
            unique_results.append(item)
    
    total_count = len(unique_results)
    
    # Paginação
    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = unique_results[start:end]
    
    return JsonResponse({
        'results': paginated_results,
        'total_count': total_count
    })
