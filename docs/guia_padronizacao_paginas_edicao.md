# Guia de Padronização das Páginas de Edição

Este documento descreve como implementar o padrão visual em todas as páginas de edição do sistema, seguindo o modelo estabelecido para a página de Alunos/Pacientes.

## Arquivos Criados

1. **CSS Centralizado**: `/static/admin/css/edit_form_standard.css`
   - Contém todos os estilos necessários para padronizar as páginas de edição
   - Inclui os estilos dos menus suspensos (Select2)

2. **Template Base**: `/templates/admin/change_form_standard.html`
   - Template base que todas as páginas de edição devem estender
   - Implementa a estrutura padrão e os scripts necessários

## Como Implementar em uma Página

Para padronizar uma página de edição, siga estes passos:

### 1. Modificar o Template da Página

Substitua:
```html
{% extends "admin/change_form_material.html" %}
```

Por:
```html
{% extends "admin/change_form_standard.html" %}
```

### 2. Implementar os Estilos Corretamente

Utilize o bloco `extrahead` para adicionar estilos, não o bloco `extrastyle`. Isso garante que os estilos sejam carregados na ordem correta e não sejam sobrescritos por outros estilos do sistema.

```html
{% block extrahead %}
{{ block.super }}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
<style>
  /* Estilos específicos para esta página */
  .fieldset-container {
    background-color: #f8f9fa;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
  }
</style>
{% endblock %}
```

Pontos importantes:
- O CSS base já está incluído no template base, não adicione novamente
- Adicione apenas estilos específicos para a página em questão
- Inclua os ícones do Material Symbols para manter a consistência visual
- Use `{{ block.super }}` para manter os estilos do template pai

### 3. Ajustar o Breadcrumb (se necessário)

Mantenha o bloco de breadcrumb específico para cada página:

```html
{% block breadcrumbs %}
<nav aria-label="breadcrumb">
  <ol class="breadcrumb bg-transparent mb-0 pb-0 pt-1 px-0 me-sm-6 me-5">
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url 'admin:index' %}">{% translate 'Início' %}</a></li>
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url 'admin:app_list' app_label='app_name' %}">App Name</a></li>
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url 'admin:app_name_model_name_changelist' %}">{{ opts.verbose_name_plural|capfirst }}</a></li>
    <li class="breadcrumb-item text-sm text-dark active" aria-current="page">
      {% if add %}{% blocktranslate with name=opts.verbose_name %}Adicionar {{ name }}{% endblocktranslate %}
      {% else %}{{ original|truncatewords:"18" }}
      {% endif %}
    </li>
  </ol>
</nav>
{% endblock %}
```

### 4. Implementar Labels Acima dos Campos (IMPORTANTE)

Para garantir que os labels apareçam corretamente acima dos campos, é necessário sobrescrever o bloco `field_sets` do template base. Nunca use apenas `{{ block.super }}` dentro deste bloco, pois isso não modificará a estrutura dos campos e labels.

Implementação correta:

```html
{% block field_sets %}
  {% for fieldset in adminform %}
    <div class="fieldset-container mb-4">
      <h5 class="text-dark mb-3">
        {% if fieldset.name %}{{ fieldset.name }}{% else %}Informações Gerais{% endif %}
      </h5>
      {% if fieldset.description %}
        <div class="description mb-3 text-secondary">{{ fieldset.description|safe }}</div>
      {% endif %}
      
      <div class="row">
        {% for line in fieldset %}
          {% for field in line %}
            <div class="{% if field.field.name == 'id' %}d-none{% else %}col-md-6 mb-3{% endif %}">
              <div class="form-group{% if field.field.required %} required{% endif %}">
                <label for="{{ field.field.id_for_label }}">{{ field.field.label }}</label>
                {{ field.field }}
                
                {% if field.field.help_text %}
                  <div class="help-text text-muted mt-1 small">{{ field.field.help_text|safe }}</div>
                {% endif %}
                
                {% if field.field.errors %}
                  <div class="error-message text-danger mt-1 small">{{ field.field.errors }}</div>
                {% endif %}
              </div>
            </div>
          {% endfor %}
        {% endfor %}
      </div>
    </div>
  {% endfor %}
{% endblock %}
```

Esta implementação garante que:
- Cada campo tenha seu label posicionado explicitamente acima dele
- Os campos sejam organizados em duas colunas para melhor aproveitamento do espaço
- Mensagens de erro e textos de ajuda sejam formatados corretamente
- O layout seja responsivo para diferentes tamanhos de tela

### 5. Manter Outros Blocos Específicos (se necessário)

Se a página tiver outros blocos específicos como `inline_field_sets` personalizados, mantenha-os conforme necessário.

### 6. Padronização do Título "Informações Gerais" e Layout de Campos

Para garantir a consistência visual entre todas as páginas de edição, é importante padronizar o título "Informações Gerais" e o layout dos campos, especialmente para campos de texto longo como descrições.

#### 6.1 Padronização do Título "Informações Gerais"

1. **Defina explicitamente o fieldset no arquivo admin.py**:

```python
@admin.register(MeuModelo)
class MeuModeloAdmin(admin.ModelAdmin):
    # outras configurações...
    fieldsets = [
        ('Informações Gerais', {
            'fields': ['campo1', 'campo2', 'descricao']
        }),
    ]
```

2. **Garanta a formatação correta do título no template**:

```html
<style>
  .fieldset-container h5 {
    font-weight: 600;
    color: #344767;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 0.75rem;
    padding-top: 0; /* Remove o padding superior */
    margin-top: 0; /* Remove a margem superior */
    margin-bottom: 1.25rem;
    text-transform: none; /* Garante que o texto não seja transformado em maiúsculas */
    font-size: 1.25rem; /* Garante o tamanho adequado da fonte */
  }
</style>
```

#### 6.2 Layout para Campos de Texto Longo (Descrição)

Para campos de texto longo como descrições, é recomendado usar a largura total da página (12 colunas) em vez de meia largura (6 colunas):

```html
<div class="{% if field.field.name == 'id' %}d-none{% elif field.field.name == 'descricao' %}col-md-12 mb-3{% else %}col-md-6 mb-3{% endif %}">
  <div class="form-group{% if field.field.required %} required{% endif %}">
    <label for="{{ field.field.id_for_label }}">{{ field.field.label }}</label>
    {{ field.field }}
    
    {% if field.field.help_text %}
      <div class="help-text text-muted mt-1 small">{{ field.field.help_text|safe }}</div>
    {% endif %}
    
    {% if field.field.errors %}
      <div class="error-message text-danger mt-1 small">{{ field.field.errors }}</div>
    {% endif %}
  </div>
</div>
```

Esta abordagem garante que campos de texto longo tenham espaço suficiente para exibir seu conteúdo sem quebrar o layout da página.

### 7. Ocultar Campos e Torná-los Automáticos

Para ocultar campos específicos da interface de administração e defini-los automaticamente, siga estas etapas:

1. **No arquivo admin.py, adicione o campo à lista `exclude`**:

```python
@admin.register(MeuModelo)
class MeuModeloAdmin(admin.ModelAdmin):
    exclude = ['campo_a_ocultar']
    # outras configurações...
```

2. **Implemente o método `save_model` para definir o valor automaticamente**:

```python
def save_model(self, request, obj, form, change):
    # Definir valor automático para o campo
    if not change or obj.campo_a_ocultar == 0:  # para novos objetos ou valores zerados
        # Lógica para definir o valor automático
        obj.campo_a_ocultar = valor_calculado
    super().save_model(request, obj, form, change)
```

Esta abordagem é útil para campos como "ordem de exibição" ou "status" que devem ser gerenciados automaticamente pelo sistema.

### 7. Personalizar o Título Dinâmico da Página

O título da página de edição é determinado pelo método `__str__` do modelo. Para personalizar como o título é exibido:

1. **Modifique o método `__str__` no arquivo models.py**:

```python
def __str__(self):
    # Retorne um texto fixo
    return "Título Personalizado"
    
    # Ou combine campos
    # return f"{self.nome} - {self.codigo}"
```

2. **O título será exibido automaticamente no template base**:

```html
<h6 class="text-white text-capitalize ps-3">
  {% if add %}{% blocktranslate with name=opts.verbose_name %}Adicionar {{ name }}{% endblocktranslate %}
  {% else %}{{ original|truncatewords:"18" }}
  {% endif %}
</h6>
```

Esta técnica permite controlar como os objetos são identificados em toda a interface de administração.

## Exemplo de Implementação Completa

Aqui está um exemplo de como implementar o padrão em uma página:

```html
{% extends "admin/change_form_standard.html" %}
{% load i18n admin_urls static %}

{% block extrahead %}{{ block.super }}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
<style>
  /* Estilos específicos para esta página */
  .fieldset-container {
    background-color: #f8f9fa;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
  }
  .fieldset-container:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
</style>
{% endblock %}

{% block breadcrumbs %}
<nav aria-label="breadcrumb">
  <ol class="breadcrumb bg-transparent mb-0 pb-0 pt-1 px-0 me-sm-6 me-5">
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url 'admin:index' %}">{% translate 'Início' %}</a></li>
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url 'admin:app_list' app_label=opts.app_label %}">{{ opts.app_config.verbose_name }}</a></li>
    <li class="breadcrumb-item text-sm"><a class="opacity-5 text-dark" href="{% url opts|admin_urlname:'changelist' %}">{{ opts.verbose_name_plural|capfirst }}</a></li>
    <li class="breadcrumb-item text-sm text-dark active" aria-current="page">{% if add %}{% blocktranslate with name=opts.verbose_name %}Adicionar {{ name }}{% endblocktranslate %}{% else %}{{ original|truncatewords:18 }}{% endif %}</li>
  </ol>
</nav>
{% endblock %}

{% block field_sets %}
  {% for fieldset in adminform %}
    <div class="fieldset-container mb-4">
      <h5 class="text-dark mb-3">
        {% if fieldset.name %}{{ fieldset.name }}{% else %}Informações Gerais{% endif %}
      </h5>
      {% if fieldset.description %}
        <div class="description mb-3 text-secondary">{{ fieldset.description|safe }}</div>
      {% endif %}
      
      <div class="row">
        {% for line in fieldset %}
          {% for field in line %}
            <div class="{% if field.field.name == 'id' %}d-none{% else %}col-md-6 mb-3{% endif %}">
              <div class="form-group{% if field.field.required %} required{% endif %}">
                <label for="{{ field.field.id_for_label }}">{{ field.field.label }}</label>
                {{ field.field }}
                
                {% if field.field.help_text %}
                  <div class="help-text text-muted mt-1 small">{{ field.field.help_text|safe }}</div>
                {% endif %}
                
                {% if field.field.errors %}
                  <div class="error-message text-danger mt-1 small">{{ field.field.errors }}</div>
                {% endif %}
              </div>
            </div>
          {% endfor %}
        {% endfor %}
      </div>
    </div>
  {% endfor %}
{% endblock %}

{% block extrajs %}
{{ block.super }}
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Ocultar botões de edição relacionados
  const relatedButtons = document.querySelectorAll('.related-widget-wrapper-link, .related-lookup');
  relatedButtons.forEach(button => {
    button.style.display = 'none';
  });
});
</script>
{% endblock %}
```

## Características do Padrão Visual

### Elementos Visuais

#### Fieldsets
- Fundo claro (#f8f9fa)
- Bordas arredondadas (border-radius: 0.75rem)
- Sombras suaves (box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06))
- Efeitos de hover para melhor feedback visual
- Títulos com estilo consistente (fonte mais grossa, cor #344767)
- Padding interno adequado (padding: 1.5rem)
- Margem inferior para separação (margin-bottom: 1.5rem)

#### Títulos dos Fieldsets
- Peso da fonte: 600
- Cor: #344767
- Borda inferior: 1px solid #dee2e6
- Padding inferior: 0.75rem
- Margem inferior: 1.25rem

### Posicionamento dos Labels

- Labels devem estar **sempre posicionados acima** dos campos de entrada
- Cada label deve ter uma margem inferior adequada para separação visual do campo (margin-bottom: 0.5rem)
- Labels devem ter estilo consistente (cor #344767, peso da fonte 500, tamanho 0.875rem)
- Campos obrigatórios devem ter indicação visual clara (asterisco vermelho)

### Menus Suspensos (Select2)

Os menus suspensos seguem estas características:

#### Configurações do Select2:
- width: 100%
- placeholder personalizado
- allowClear: false (sem botão X para limpar)
- minimumResultsForSearch: 0 (sempre mostra o campo de pesquisa)
- mensagens em português ("Nenhum resultado encontrado", "Buscando...")

#### Estilos CSS:
- Bordas arredondadas (border-radius: 0.5rem)
- Altura adequada (min-height: 38px)
- Padding interno (padding: 0.25rem 0.5rem)
- Texto centralizado verticalmente (padding: 0.375rem 0.5rem no .select2-selection__rendered)
- Sem seta para baixo (display: none no .select2-selection__arrow)
- Sem botão X para limpar (display: none no .select2-selection__clear)
- Cor rosa (#e91e63) para o contorno e foco do campo
- Cores neutras dentro do menu suspenso (cinza #f8f9fa para itens normais, #e9ecef para hover e selecionado)
- Dropdown com sombra suave
- Campo de pesquisa com bordas arredondadas e foco estilizado

#### Ocultação de botões de ação:
- Botões de editar, incluir e visualizar ocultados (.related-widget-wrapper-link com display: none)
- Implementação via CSS e JavaScript para garantir consistência

#### Exemplo de código para ocultar botões relacionados:
```javascript
document.addEventListener('DOMContentLoaded', function() {
  // Ocultar botões de edição relacionados
  const relatedButtons = document.querySelectorAll('.related-widget-wrapper-link, .related-lookup');
  relatedButtons.forEach(button => {
    button.style.display = 'none';
  });
});
```

#### Arquivo CSS de referência:
Os estilos completos para os campos Select2 estão definidos no arquivo `/static/admin/css/form_fields_style.css`

### Campos de Formulário

- Bordas arredondadas
- Efeito de foco com contorno rosa
- Indicação clara para campos obrigatórios (asterisco vermelho)
- Textos de ajuda formatados com estilo sutil abaixo dos campos

### Botões

- Estilo outline para botões de ação
- Ícones do Material Symbols
- Efeitos de hover com elevação suave

## Terminologia Padronizada

Para manter a consistência em todas as páginas, use a seguinte terminologia em português:

- "Adicionar" em vez de "Add" no título e breadcrumb
- "Salvar" em vez de "Save" no botão principal
- "Salvar e continuar editando" em vez de "Save and continue editing"
- "Salvar e adicionar outro" em vez de "Save and add another"
- "Excluir" em vez de "Delete" no botão de exclusão
- "Início" em vez de "Home" no breadcrumb

### Exemplo de implementação dos botões:

```html
<button type="submit" class="btn btn-primary mb-0" name="_save">
  <i class="material-symbols-rounded opacity-10" style="font-size: 16px;">save</i> {% translate 'Salvar' %}
</button>

<button type="submit" class="btn btn-outline-primary mb-0" name="_continue">
  <i class="material-symbols-rounded opacity-10" style="font-size: 16px;">save</i> {% translate 'Salvar e continuar editando' %}
</button>

<button type="submit" class="btn btn-outline-primary mb-0" name="_addanother">
  <i class="material-symbols-rounded opacity-10" style="font-size: 16px;">add</i> {% translate 'Salvar e adicionar outro' %}
</button>

<a href="delete/" class="btn btn-outline-danger mb-0">
  <i class="material-symbols-rounded opacity-10" style="font-size: 16px;">delete</i> {% translate 'Excluir' %}
</a>
```

## Organização dos Elementos

- **Botões de ação**: Agrupados logicamente (ações de salvar à esquerda, excluir à direita)
- **Campos**: Organizados em fieldsets com títulos descritivos
- **Textos de ajuda**: Formatados com estilo sutil abaixo dos campos
- **Layout responsivo**: Colunas que se adaptam a dispositivos móveis
- **Feedback visual**: Botões desabilitados e spinner ao enviar o formulário

## Lista de Páginas a Padronizar

- [x] Anamnese
- [x] Registro de Evolução
- [x] Neurodivergência
- [ ] Adaptação Curricular Individualizada
- [ ] PDI
- [ ] Parecer
- [ ] Escola
- [ ] Profissional
- [ ] Meta/Habilidade
- [ ] Categoria CID-10
- [x] Condição CID-10
- [ ] Código BNCC
- [ ] Disciplina BNCC
