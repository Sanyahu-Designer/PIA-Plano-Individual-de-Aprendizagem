from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User, Group
from .views import CustomLoginView, dashboard_gerente, dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Importante: a ordem das URLs importa!
# Colocamos as URLs do realtime antes das URLs do admin
# para garantir que nossas URLs personalizadas tenham precedência
urlpatterns = [
    # URLs do realtime (devem vir antes do admin)
    path('dashboard/realtime/', include('realtime.urls', namespace='realtime')),
    
    # Dashboard do Gerente - Tem precedência sobre o admin.site.urls
    path('dashboard/gerente/', dashboard_gerente, name='dashboard_gerente'),
    path('dashboard/', admin.site.urls, name='dashboard'),  # Usar o admin site diretamente
    
    # O Django Admin já gerencia automaticamente as URLs para todos os modelos registrados
    # Não é necessário incluir admin.site.urls múltiplas vezes
    # A linha 'path('dashboard/', admin.site.urls, name='dashboard')' acima já inclui o admin site
    
    # URLs personalizadas para usar os templates do Material Dashboard 3
    path('dashboard/adaptacao_curricular/', staff_member_required(lambda request: TemplateResponse(request, 'admin/neurodivergentes/aci/change_list_material_dashboard.html', {'title': 'ACI', 'cl': {'opts': {'verbose_name_plural': 'Adaptações Curriculares Individualizadas', 'app_label': 'adaptacao_curricular', 'app_config': {'verbose_name': 'Adaptação Curricular'}}}})), name='aci_dashboard'),
    path('dashboard/neurodivergentes/', staff_member_required(lambda request: TemplateResponse(request, 'admin/neurodivergentes/neurodivergente/change_list_material_dashboard.html', {'title': 'Neurodivergentes'})), name='neurodivergentes_dashboard'),
    path('dashboard/neurodivergentes/neurodivergencia/', staff_member_required(lambda request: TemplateResponse(request, 'admin/neurodivergentes/neurodivergencia/change_list_material_dashboard.html', {'title': 'Neurodivergências', 'cl': {'opts': {'verbose_name_plural': 'Neurodivergências', 'app_label': 'neurodivergentes', 'app_config': {'verbose_name': 'Neurodivergentes'}}}})), name='neurodivergencia_dashboard'),
    path('dashboard/bncc/codigobncc/', staff_member_required(lambda request: TemplateResponse(request, 'admin/bncc/codigobncc/change_list_material_dashboard.html', {'title': 'Códigos BNCC'})), name='codigobncc_dashboard'),
    path('dashboard/bncc/disciplinabncc/', staff_member_required(lambda request: TemplateResponse(request, 'admin/bncc/disciplinabncc/change_list_material_dashboard.html', {'title': 'Disciplinas BNCC'})), name='disciplinabncc_dashboard'),
    path('dashboard/cid10/categoriacid10/', staff_member_required(lambda request: TemplateResponse(request, 'admin/cid10/categoriacid10/change_list_material_dashboard.html', {'title': 'Categorias CID-10'})), name='categoriacid10_dashboard'),
    path('dashboard/cid10/condicaocid10/', staff_member_required(lambda request: TemplateResponse(request, 'admin/cid10/condicaocid10/change_list_material_dashboard.html', {'title': 'Condições CID-10'})), name='condicaocid10_dashboard'),
    path('dashboard/metashabilidades/metahabilidade/', staff_member_required(lambda request: TemplateResponse(request, 'admin/metashabilidades/metahabilidade/change_list_material_dashboard.html', {'title': 'Metas/Habilidades'})), name='metahabilidade_dashboard'),
    path('dashboard/auth/', staff_member_required(lambda request: TemplateResponse(request, 'admin/auth/app_index.html', {
        'title': 'Autenticação e Autorização',
        'app_label': 'auth',
        'app_list': [{
            'name': 'Autenticação e Autorização',
            'app_label': 'auth',
            'app_url': '/dashboard/auth/',
            'has_module_perms': True,
            'models': [
                {
                    'name': 'Grupos',
                    'object_name': 'group',
                    'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                    'admin_url': '/dashboard/auth/group/',
                    'add_url': '/dashboard/auth/group/add/'
                },
                {
                    'name': 'Usuários',
                    'object_name': 'person',
                    'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                    'admin_url': '/dashboard/auth/user/',
                    'add_url': '/dashboard/auth/user/add/'
                }
            ]
        }]
    })), name='auth_dashboard'),
    path('dashboard/auth/user/', staff_member_required(lambda request: TemplateResponse(request, 'admin/auth/app_index_material_dashboard.html', {
        'title': 'Usuários',
        'app_label': 'auth',
        'users': User.objects.all().order_by('first_name', 'last_name')
    })), name='usuarios_dashboard'),
    
    path('dashboard/auth/group/', staff_member_required(lambda request: TemplateResponse(request, 'admin/auth/group/change_list_material_dashboard.html', {
        'title': 'Grupos',
        'app_label': 'auth',
        'cl': {
            'result_list': Group.objects.all().order_by('name'),
            'result_count': Group.objects.count(),
            'full_result_count': Group.objects.count(),
            'opts': {
                'verbose_name': 'grupo',
                'verbose_name_plural': 'Grupos',
                'app_label': 'auth',
                'app_config': {'verbose_name': 'Autenticação e Autorização'}
            },
            'query': request.GET.get('q', '')
        }
    })), name='grupos_dashboard'),
    
    # Outras URLs
    path('', CustomLoginView.as_view(
        template_name='pia_config/login.html',
        next_page='/dashboard/'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    path('escolas/', include('escola.urls')),
    path('profissionais/', include('profissionais_app.urls')),
    path('neurodivergentes/', include('neurodivergentes.urls')),
    path('adaptacao-curricular/', include('adaptacao_curricular.urls')),
    
    # Adicionar uma URL para a página de teste de WebSocket
    path('websocket-test/', lambda request: serve(request, 'websocket-test.html', document_root=settings.STATIC_ROOT)),
]

# Servir arquivos estáticos e de mídia
# Isso é necessário para o Daphne servir arquivos estáticos
urlpatterns += [
    # Rota para servir arquivos estáticos
    path('static/<path:path>', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
    
    # Rota para servir arquivos de mídia
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Adicionar as rotas padrão do Django para arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)