from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pia_config.views import custom_permission_denied_view

urlpatterns = [
    # Removido path('admin/', admin.site.urls) para evitar duplicação com pia_config.urls
    path('', include('institucional.urls')),
    path('', include('pia_config.urls')),  # Define a página inicial como a página de login
    path('agendamento/', include('agendamento.urls')),
    # Removendo URLs antigas que causavam redirecionamentos incorretos
    # path('profissionais/', include('profissionais.urls')),
    # path('escolas/', include('escola.urls')),
    path('admin/autocomplete/', admin.site.autocomplete_view),  # Adiciona URLs de autocomplete

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'pia_config.views.custom_permission_denied_view'