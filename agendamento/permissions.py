from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps
from profissionais_app.models import Profissional


def is_profissional(user):
    """Verifica se o usuário é um profissional"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profissional') or user.is_superuser


def is_gestor_or_admin(user):
    """Verifica se o usuário é gestor ou admin"""
    if not user.is_authenticated:
        return False
    return (user.is_superuser or 
            user.groups.filter(name__in=['Gestor', 'Admin']).exists())


def is_secretario(user):
    """Verifica se o usuário é secretário (função futura)"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Secretario').exists()


def can_view_agenda(user):
    """Verifica se o usuário pode visualizar a agenda"""
    return is_profissional(user) or is_gestor_or_admin(user) or is_secretario(user)


def can_create_agendamento(user):
    """Verifica se o usuário pode criar agendamentos"""
    return is_profissional(user) or is_gestor_or_admin(user) or is_secretario(user)


def can_edit_agendamento(user, agendamento):
    """Verifica se o usuário pode editar um agendamento específico"""
    if is_gestor_or_admin(user):
        return True
    
    # Verifica se tem a permissão especial para gerenciar todas as agendas
    if user.has_perm('agendamento.can_manage_all_schedules'):
        return True
    
    if is_profissional(user):
        try:
            profissional = user.profissional
            return agendamento.profissional == profissional
        except Profissional.DoesNotExist:
            return False
    
    if is_secretario(user):
        # Lógica futura para secretários gerenciarem grupos específicos
        return False
    
    return False


def can_delete_agendamento(user, agendamento):
    """Verifica se o usuário pode excluir um agendamento específico"""
    return can_edit_agendamento(user, agendamento)


def require_agenda_access(view_func):
    """Decorator que requer acesso à agenda"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not can_view_agenda(request.user):
            raise PermissionDenied("Você não tem permissão para acessar a agenda.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_create_permission(view_func):
    """Decorator que requer permissão para criar agendamentos"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not can_create_agendamento(request.user):
            raise PermissionDenied("Você não tem permissão para criar agendamentos.")
        return view_func(request, *args, **kwargs)
    return wrapper


def get_user_permissions(user):
    """Retorna as permissões do usuário em formato de dicionário"""
    return {
        'can_view_agenda': can_view_agenda(user),
        'can_create_agendamento': can_create_agendamento(user),
        'is_profissional': is_profissional(user),
        'is_gestor_or_admin': is_gestor_or_admin(user),
        'is_secretario': is_secretario(user),
    }


def get_user_profile_type(user):
    """Retorna o tipo de perfil do usuário"""
    if is_gestor_or_admin(user):
        return 'gestor_admin'
    elif is_secretario(user):
        return 'secretario'
    elif is_profissional(user):
        return 'profissional'
    else:
        return 'sem_permissao'
