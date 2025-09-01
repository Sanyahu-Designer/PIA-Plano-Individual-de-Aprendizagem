# Deploy Completo - Todas as Correções do Sistema

## Arquivos para Upload (Deploy Seguro)

### **GRUPO FAMILIAR - Correções Principais**

#### 1. Admin Configuration
```
neurodivergentes/admin.py
```
**Mudança**: `extra = 2` para múltiplos membros

#### 2. Template Grupo Familiar
```
templates/admin/neurodivergentes/edit_inline/stacked_grupo_familiar.html
```
**Mudança**: JavaScript melhorado + prevenção Select2

#### 3. Script Select2 Global
```
static/admin/js/select2_initializer.js
```
**Mudança**: Exclusão selects de vínculo

#### 4. **CRÍTICO** - Modelo Grupo Familiar
```
neurodivergentes/models/grupo_familiar.py
```
**Mudança**: Signal corrigido (erro 500)

### **NEURODIVERGENTES - Outras Correções**

#### 5. Formulários
```
neurodivergentes/forms.py
```
**Mudança**: Correções de validação e formatação

#### 6. Views
```
neurodivergentes/views.py
```
**Mudança**: Correções de impressão e relatórios

#### 7. Modelos Base
```
neurodivergentes/models/__init__.py
neurodivergentes/models/base.py
neurodivergentes/models/historico_escolar.py
neurodivergentes/models/pdi.py
```
**Mudança**: Estrutura de modelos reorganizada

### **SISTEMA GERAL**

#### 8. URLs Principal
```
urls.py
```
**Mudança**: Rotas atualizadas

#### 9. Configurações
```
pia_config/settings.py
pia_config/urls.py
pia_config/views.py
```
**Mudança**: Configurações de sistema

#### 10. Templates Base
```
templates/admin/base_material.html
templates/admin/base_site.html
templates/admin/change_list_material_dashboard_base.html
templates/admin/dashboard_gerente.html
templates/admin/includes/navbar.html
templates/dashboard/base.html
```
**Mudança**: Interface e navegação

#### 11. Profissionais
```
profissionais_app/admin.py
```
**Mudança**: Administração de profissionais

#### 12. Institucional
```
institucional/urls.py
institucional/views.py
templates/institucional/lgpd.html
```
**Mudança**: Páginas institucionais e LGPD

## Instruções de Deploy

### Passo 1: Backup
- Fazer backup dos arquivos originais em produção antes de substituir

### Passo 2: Upload dos Arquivos
1. Substituir `neurodivergentes/admin.py`
2. Substituir `templates/admin/neurodivergentes/edit_inline/stacked_grupo_familiar.html`
3. Substituir `static/admin/js/select2_initializer.js`
4. **CRÍTICO**: Substituir `neurodivergentes/models/grupo_familiar.py`

### Passo 3: Reiniciar Servidor
- Reiniciar o servidor Django para aplicar as mudanças
- Limpar cache se necessário

### Passo 4: Teste
- Acessar cadastro de Neurodivergente
- Testar adição de múltiplos membros do Grupo Familiar
- Verificar se campos de vínculo funcionam corretamente

## ⚠️ Importante

**NÃO aplicar migrações** - Este deploy não requer mudanças no banco de dados.
As alterações são apenas de configuração e interface.

## Resultado Esperado

- Usuários podem adicionar múltiplos membros da família simultaneamente
- Campos de vínculo/parentesco funcionam imediatamente
- Salvamento de múltiplos membros funciona corretamente

## Rollback

Em caso de problemas, restaurar os arquivos de backup originais e reiniciar o servidor.
