from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Personaliza o UserAdmin para usar o template do Material Dashboard 3
class CustomUserAdmin(UserAdmin):
    # Mantém as configurações padrão do UserAdmin
    pass

# Personaliza o GroupAdmin para usar os templates personalizados
class CustomGroupAdmin(GroupAdmin):
    change_list_template = 'admin/auth/group/change_list_material_dashboard.html'
    change_form_template = 'admin/auth/group/change_form.html'

# Desregistra os admins padrão e registra os nossos personalizados
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Desregistra o GroupAdmin padrão e registra o nosso personalizado
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
