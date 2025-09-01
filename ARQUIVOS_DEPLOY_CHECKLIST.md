# 📋 CHECKLIST DE ARQUIVOS PARA DEPLOY
## Lista Detalhada de Arquivos Modificados/Novos

**Data:** 30/08/2025  
**Status:** ✅ PRONTO PARA DEPLOY

---

## 🆕 ARQUIVOS COMPLETAMENTE NOVOS

### **Módulo Agendamento (Diretório Completo)**
```
/agendamento/
├── __init__.py
├── admin.py                    # Interface administrativa
├── apps.py                     # Configuração da app
├── models.py                   # Modelo Agendamento
├── permissions.py              # Sistema de permissões
├── urls.py                     # URLs do módulo
├── views.py                    # Views e APIs
├── tests.py                    # Testes (básico)
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py         # Criação do modelo
│   ├── 0002_agendamento_tenant_id.py
│   └── 0003_alter_agendamento_options_alter_agendamento_managers.py
└── templates/
    └── agendamento/
        └── calendario.html     # Interface do calendário
```

### **Documentação**
```
/docs/Proposta_Sistema_Agendamento_PIA.md
/docs/DEPLOY_PAEE_AJUSTES_CAMPOS.md
/docs/DEPLOY_TERMINOLOGIA_PEI_PAEE.md
/docs/DEPLOY_MOTIVO_INATIVIDADE.md
/docs/DEPLOY_CAMPO_NATURALIDADE.md
/docs/DEPLOY_DASHBOARD_ALUNOS_ATIVOS.md
/docs/DEPLOY_AUSENCIAS_RELATORIO_PDI.md
```

---

## 🔧 ARQUIVOS MODIFICADOS CRÍTICOS

### **Configuração Principal**
```
/pia_config/settings.py
# ALTERAÇÃO: Adicionar 'agendamento' ao INSTALLED_APPS (linha ~80)
```

```
/urls.py
# ALTERAÇÃO: Adicionar path('agendamento/', include('agendamento.urls'))
```

### **Modelos Neurodivergentes**
```
/neurodivergentes/models/base.py
# ALTERAÇÕES:
# - Campos de endereço: NULL permitido → NOT NULL (reverter para produção)
# - Campo ano_escolar: mantém CharField (não ForeignKey)
# - Novos campos: naturalidade, motivo_inatividade, tipo_sanguineo
```

```
/neurodivergentes/models/pei.py
# ALTERAÇÕES:
# - Campo observacoes: CKEditor5Field → TextField
# - Reordenação de campos (pedagogo_responsavel antes de observacoes)
```

### **Formulários**
```
/neurodivergentes/forms.py
# ALTERAÇÕES:
# - MonitoramentoForm: nova ordem de campos
# - Widget personalizado para campo observacoes
```

### **Admin**
```
/neurodivergentes/admin.py
# ALTERAÇÕES:
# - Terminologia: "PEI" → "PAEE" em vários locais
# - Métodos get_mes_ano → get_ano
# - Remoção de referências ao campo 'mes'
```

---

## 🎨 TEMPLATES MODIFICADOS

### **Dashboard**
```
/templates/admin/dashboard_gerente.html
# ALTERAÇÕES:
# - Novo gráfico "Atendimentos Mensais por Profissional"
# - Melhorias de responsividade para TVs
# - Ajustes de altura dos gráficos
# - Limitação de dados para 100 itens
```

### **Navbar**
```
/templates/admin/includes/navbar.html
# ALTERAÇÕES:
# - Botão "Agenda" adicionado ao menu principal
# - Link para /agendamento/calendario/
```

### **Templates PAEE/PDI**
```
/templates/admin/neurodivergentes/monitoramento/change_form.html
# ALTERAÇÕES:
# - Campo observacoes configurado para col-md-12 (largura total)

/templates/admin/neurodivergentes/monitoramento/change_list_material_dashboard.html
# ALTERAÇÕES:
# - Formatação de datas: remoção de "mes/" (apenas ano)
# - Cabeçalhos: "Mês/Ano" → "Ano"
```

### **Relatórios**
```
/neurodivergentes/templates/neurodivergentes/relatorio_pei.html
/neurodivergentes/templates/neurodivergentes/relatorio_pei_geral.html
/neurodivergentes/templates/neurodivergentes/pei_list.html
/neurodivergentes/templates/neurodivergentes/pei_detail.html
/neurodivergentes/templates/neurodivergentes/relatorio.html
# ALTERAÇÕES: Formatação de datas (remoção de mes/ano → apenas ano)
```

---

## 💾 MIGRAÇÕES NOVAS

### **Neurodivergentes**
```
/neurodivergentes/migrations/0022_neurodivergente_motivo_inatividade_and_more.py
# ADICIONA: campos motivo_inatividade e outros

/neurodivergentes/migrations/0023_neurodivergente_naturalidade.py
# ADICIONA: campo naturalidade

/neurodivergentes/migrations/0024_alter_monitoramento_options_and_more.py
# ALTERA: opções do modelo Monitoramento, remove campo mes

/neurodivergentes/migrations/0025_alter_monitoramento_observacoes.py
# ALTERA: campo observacoes de CKEditor5Field para TextField
```

### **Agendamento**
```
/agendamento/migrations/0001_initial.py
# CRIA: modelo Agendamento completo

/agendamento/migrations/0002_agendamento_tenant_id.py
# ADICIONA: campo tenant_id para multilocação

/agendamento/migrations/0003_alter_agendamento_options_alter_agendamento_managers.py
# ALTERA: opções e managers do modelo
```

---

## 🎨 ARQUIVOS CSS/JS EXISTENTES

### **CSS**
```
/static/admin/css/form_fields_style.css
# EXISTENTE: Estilos para campos Select2 (18.4KB)

/static/css/custom.css
# EXISTENTE: Estilos personalizados do sistema

/static/admin/css/select2_custom.css
# EXISTENTE: Estilos específicos para Select2 (2.6KB)
```

### **JavaScript**
```
/static/admin/js/select2_initializer.js
# EXISTENTE: Inicialização do Select2 com exclusões específicas

/static/js/escola_dashboard_init.js
# EXISTENTE: Melhorias no dashboard (localização corrigida)
```

---

## ⚠️ ARQUIVOS QUE PRECISAM CORREÇÃO PRÉ-DEPLOY

### **1. Modelo Base (CRÍTICO)**
```
/neurodivergentes/models/base.py
# CORREÇÃO NECESSÁRIA: Reverter campos de endereço para NOT NULL
# ANTES DO DEPLOY:
estado_nascimento = models.CharField('Estado de Nascimento', max_length=2, choices=ESTADOS_CHOICES)
cidade_nascimento = models.CharField('Cidade de Nascimento', max_length=100)
endereco = models.CharField('Endereço', max_length=255)
numero = models.CharField('Número', max_length=10)
bairro = models.CharField('Bairro', max_length=100)
```

### **2. Settings (CRÍTICO)**
```
/pia_config/settings.py
# VERIFICAR: INSTALLED_APPS deve incluir 'agendamento'
# VERIFICAR: Configurações de banco de dados para produção
```

---

## 🔍 VERIFICAÇÕES PÓS-DEPLOY

### **Funcionalidades a Testar:**
- [ ] Login no sistema
- [ ] Cadastro de novo aluno (campos obrigatórios funcionando)
- [ ] Acesso ao módulo agendamento via navbar
- [ ] Dashboard carregando com novos gráficos
- [ ] PAEE/PDI com nova terminologia
- [ ] Relatórios com formatação correta de datas
- [ ] Campo naturalidade nos alunos
- [ ] Campo motivo_inatividade funcionando

### **Dados a Verificar:**
- [ ] Alunos existentes carregando corretamente
- [ ] PDIs/PAEEs acessíveis e editáveis
- [ ] Relatórios gerando com dados corretos
- [ ] Agendamentos podem ser criados

---

## 📦 ORDEM DE UPLOAD RECOMENDADA

### **1. Primeiro (Arquivos de Aplicação):**
```
/agendamento/ (diretório completo)
/pia_config/settings.py
/urls.py
```

### **2. Segundo (Templates e Estáticos):**
```
/templates/
/static/
```

### **3. Terceiro (Modelos e Forms):**
```
/neurodivergentes/models/
/neurodivergentes/forms.py
/neurodivergentes/admin.py
```

### **4. Quarto (Migrações - CUIDADO!):**
```
/agendamento/migrations/
/neurodivergentes/migrations/0022_*.py
/neurodivergentes/migrations/0023_*.py
/neurodivergentes/migrations/0024_*.py
/neurodivergentes/migrations/0025_*.py
```

---

**⚠️ IMPORTANTE:** Seguir exatamente a ordem do PLANO_DEPLOY_SEGURO.md para evitar problemas de compatibilidade.

**✅ STATUS:** Todos os arquivos identificados e categorizados. Pronto para execução do deploy seguindo o plano seguro.
