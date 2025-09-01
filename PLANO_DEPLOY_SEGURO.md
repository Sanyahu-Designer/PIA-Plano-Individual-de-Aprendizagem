# 🚨 PLANO DE DEPLOY SEGURO - PIA SISTEMA
## Análise Crítica e Estratégia de Migração

**Data:** 30/08/2025  
**Responsável:** Sanyahu  
**Status:** ⚠️ DEPLOY CRÍTICO - REQUER ATENÇÃO ESPECIAL

---

## ⚠️ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **INCOMPATIBILIDADE ESTRUTURAL DO BANCO**
- **PRODUÇÃO:** Campo `ano_escolar_id` (ForeignKey)
- **DESENVOLVIMENTO:** Campo `ano_escolar` (CharField)
- **RISCO:** Erro fatal ao aplicar migrações

### 2. **CAMPOS OBRIGATÓRIOS DIVERGENTES**
- **PRODUÇÃO:** Campos de endereço são NOT NULL
- **DESENVOLVIMENTO:** Campos de endereço permitem NULL
- **RISCO:** Violação de constraint ao salvar dados

### 3. **MÓDULO AGENDAMENTO INEXISTENTE**
- **PRODUÇÃO:** Não possui o módulo
- **DESENVOLVIMENTO:** Módulo completo implementado
- **RISCO:** Erro ao carregar aplicação

---

## 📋 ESTRATÉGIA SEGURA DE DEPLOY

### **FASE 1: PREPARAÇÃO (CRÍTICA)**

#### 1.1 Backup Completo
```bash
# Backup do banco de dados
mysqldump -u usuario -p netsarim_caraapiaweb > backup_pre_deploy_$(date +%Y%m%d_%H%M%S).sql

# Backup dos arquivos
tar -czf backup_arquivos_$(date +%Y%m%d_%H%M%S).tar.gz /caminho/para/aplicacao/
```

#### 1.2 Verificação de Migrações
```bash
# Verificar estado atual das migrações em produção
python manage.py showmigrations

# Última migração em produção: neurodivergentes.0021_alter_monitoramento_mes
```

### **FASE 2: CORREÇÕES PRÉ-DEPLOY**

#### 2.1 Ajustar Modelo Neurodivergente
**ARQUIVO:** `/neurodivergentes/models/base.py`

**ALTERAÇÕES NECESSÁRIAS:**
```python
# Reverter campos de endereço para obrigatórios
estado_nascimento = models.CharField('Estado de Nascimento', max_length=2, choices=ESTADOS_CHOICES)
cidade_nascimento = models.CharField('Cidade de Nascimento', max_length=100)
endereco = models.CharField('Endereço', max_length=255)
numero = models.CharField('Número', max_length=10)
bairro = models.CharField('Bairro', max_length=100)

# Manter ano_escolar como CharField (não reverter para ForeignKey)
ano_escolar = models.CharField(
    'Ano Escolar',
    max_length=50,
    choices=[item for group in SERIES_CHOICES[1:] for item in group[1]],
    blank=True,
    null=True
)
```

#### 2.2 Criar Migração de Transição
```bash
python manage.py makemigrations neurodivergentes --name="preparar_deploy_producao"
```

### **FASE 3: DEPLOY SEQUENCIAL**

#### 3.1 Arquivos de Aplicação (SEM migrações)
**ORDEM DE UPLOAD:**

1. **Módulo Agendamento Completo:**
   ```
   /agendamento/
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── models.py
   ├── permissions.py
   ├── urls.py
   ├── views.py
   └── templates/
   ```

2. **Settings.py Atualizado:**
   ```python
   INSTALLED_APPS = [
       # ... apps existentes ...
       'agendamento',  # ADICIONAR
   ]
   ```

3. **URLs Principal:**
   ```python
   # Adicionar em urls.py
   path('agendamento/', include('agendamento.urls')),
   ```

4. **Templates e Arquivos Estáticos:**
   ```
   /templates/admin/dashboard_gerente.html
   /static/admin/css/
   /static/admin/js/
   ```

#### 3.2 Aplicação de Migrações (SEQUENCIAL)
```bash
# 1. Migrar apenas o módulo agendamento
python manage.py migrate agendamento

# 2. Verificar se não há erros
python manage.py check

# 3. Aplicar migrações neurodivergentes uma por vez
python manage.py migrate neurodivergentes 0022
python manage.py migrate neurodivergentes 0023
python manage.py migrate neurodivergentes 0024
python manage.py migrate neurodivergentes 0025

# 4. Verificar integridade
python manage.py check --deploy
```

### **FASE 4: VERIFICAÇÕES PÓS-DEPLOY**

#### 4.1 Testes Funcionais
- [ ] Login no sistema
- [ ] Cadastro de novo aluno (campos obrigatórios)
- [ ] Acesso ao módulo agendamento
- [ ] Dashboard carregando corretamente
- [ ] Relatórios funcionando

#### 4.2 Testes de Dados
- [ ] Alunos existentes carregando
- [ ] PDIs/PAEEs acessíveis
- [ ] Relatórios com dados corretos

---

## 🔄 PLANO DE ROLLBACK

### **SE ALGO DER ERRADO:**

#### 1. Rollback do Banco
```bash
# Parar aplicação
sudo systemctl stop gunicorn

# Restaurar backup
mysql -u usuario -p netsarim_caraapiaweb < backup_pre_deploy_TIMESTAMP.sql

# Reiniciar aplicação
sudo systemctl start gunicorn
```

#### 2. Rollback dos Arquivos
```bash
# Restaurar arquivos
tar -xzf backup_arquivos_TIMESTAMP.tar.gz -C /

# Reiniciar serviços
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 📁 ARQUIVOS PARA DEPLOY

### **NOVOS ARQUIVOS:**
```
/agendamento/ (diretório completo)
/docs/Proposta_Sistema_Agendamento_PIA.md
/docs/DEPLOY_*.md (documentações)
```

### **ARQUIVOS MODIFICADOS:**
```
/pia_config/settings.py (INSTALLED_APPS)
/urls.py (nova rota agendamento)
/templates/admin/dashboard_gerente.html
/templates/admin/includes/navbar.html
/neurodivergentes/models/base.py
/neurodivergentes/admin.py
/neurodivergentes/forms.py
/static/admin/css/ (arquivos de estilo)
/static/admin/js/ (arquivos JavaScript)
```

### **MIGRAÇÕES:**
```
/neurodivergentes/migrations/0022_neurodivergente_motivo_inatividade_and_more.py
/neurodivergentes/migrations/0023_neurodivergente_naturalidade.py
/neurodivergentes/migrations/0024_alter_monitoramento_options_and_more.py
/neurodivergentes/migrations/0025_alter_monitoramento_observacoes.py
/agendamento/migrations/ (todas)
```

---

## ⚡ COMANDOS DE DEPLOY

### **SEQUÊNCIA EXATA:**
```bash
# 1. Backup
mysqldump -u usuario -p netsarim_caraapiaweb > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Upload dos arquivos (SEM migrações ainda)
# Fazer upload manual via FTP/cPanel

# 3. Adicionar agendamento ao INSTALLED_APPS
# Editar settings.py

# 4. Aplicar migrações sequencialmente
python manage.py migrate agendamento
python manage.py migrate neurodivergentes 0022
python manage.py migrate neurodivergentes 0023
python manage.py migrate neurodivergentes 0024
python manage.py migrate neurodivergentes 0025

# 5. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 6. Reiniciar serviços
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 7. Verificar logs
tail -f /var/log/gunicorn/error.log
```

---

## 🎯 PONTOS DE ATENÇÃO

### **CRÍTICOS:**
1. **NÃO aplicar migração 0021 modificada** - usar apenas as novas (0022+)
2. **Verificar campos obrigatórios** antes de aplicar migrações
3. **Testar módulo agendamento** após cada etapa
4. **Monitorar logs** durante todo o processo

### **RECOMENDAÇÕES:**
1. Fazer deploy em horário de menor movimento
2. Ter equipe técnica disponível para rollback
3. Comunicar usuários sobre possível indisponibilidade
4. Manter backups por pelo menos 7 dias

---

**⚠️ ESTE DEPLOY REQUER MÁXIMA ATENÇÃO DEVIDO ÀS INCOMPATIBILIDADES ESTRUTURAIS**

**✅ DEPLOY APROVADO APENAS COM EXECUÇÃO SEQUENCIAL E MONITORAMENTO CONTÍNUO**
