# Deploy - Ajustes nos Campos do PAEE

## Resumo das Alterações
Este documento descreve as alterações realizadas no módulo PAEE para:
1. Inverter a posição dos campos Planejamento e Profissional Responsável
2. Configurar o campo Planejamento para largura total
3. Corrigir a formatação das datas anuais (remover "/" desnecessário)

## Data do Deploy
**Data:** 29/08/2025  
**Responsável:** Sanyahu  
**Versão:** 1.0  

## Arquivos Alterados

### 1. Modelo e Formulário

#### `/neurodivergentes/models/pei.py`
**Alterações:**
- Linha 25-30: Campo `observacoes` (Planejamento) convertido de `CKEditor5Field` para `TextField`
- Linha 31-39: Campo `pedagogo_responsavel` (Profissional Responsável) movido para depois do Planejamento
- Removida importação: `from django_ckeditor_5.fields import CKEditor5Field`

#### `/neurodivergentes/forms.py`
**Alterações:**
- Linha 249: Ordem dos campos alterada para `['neurodivergente', 'ano', 'metas', 'pedagogo_responsavel', 'observacoes']`
- Linhas 252-257: Widget do campo `observacoes` configurado com:
  - `'class': 'form-control'`
  - `'style': 'width: 100%;'`
  - Placeholder atualizado

### 2. Template de Formulário

#### `/templates/admin/neurodivergentes/monitoramento/change_form.html`
**Alterações:**
- Linha 141: Campo `observacoes` configurado para usar `col-md-12` (largura total)
- Outros campos mantêm `col-md-6` (meia largura)

### 3. Templates de Listagem e Relatórios

#### `/templates/admin/neurodivergentes/monitoramento/change_list_material_dashboard.html`
**Alterações:**
- Linha 165: `{{ obj.get_mes_display }}/{{ obj.ano }}` → `{{ obj.ano }}`
- Linha 204: `{{ obj.get_mes_display }}/{{ obj.ano }}` → `{{ obj.ano }}`

#### `/neurodivergentes/templates/neurodivergentes/relatorio_pei.html`
**Alterações:**
- Linha 237: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`
- Linha 247: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`

#### `/neurodivergentes/templates/neurodivergentes/relatorio_pei_geral.html`
**Alterações:**
- Linha 155: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`

#### `/neurodivergentes/templates/neurodivergentes/pei_list.html`
**Alterações:**
- Linha 91: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`

#### `/neurodivergentes/templates/neurodivergentes/pei_detail.html`
**Alterações:**
- Linha 114: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`
- Linha 118: `{{ pei.get_mes_display }}/{{ pei.ano }}` → `{{ pei.ano }}`

#### `/neurodivergentes/templates/neurodivergentes/relatorio.html`
**Alterações:**
- Linha 160: Cabeçalho da tabela "Mês/Ano" → "Ano"
- Linha 167: `{{ frequencia.get_mes_display }}/{{ frequencia.ano }}` → `{{ frequencia.ano }}`

### 4. Migração de Banco de Dados

#### Migração Criada
- `neurodivergentes/migrations/0025_alter_monitoramento_observacoes.py`
- Converte campo `observacoes` de `CKEditor5Field` para `TextField`

## Comandos para Deploy

### 1. Aplicar Migração
```bash
python manage.py migrate neurodivergentes
```

### 2. Coletar Arquivos Estáticos (se necessário)
```bash
python manage.py collectstatic --noinput
```

### 3. Reiniciar Servidor
```bash
# Para desenvolvimento
python manage.py runserver

# Para produção (exemplo com gunicorn)
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## Verificações Pós-Deploy

### 1. Interface do PAEE
- [ ] Campo "Planejamento" aparece após "Profissional Responsável"
- [ ] Campo "Planejamento" ocupa largura total (100%)
- [ ] Campo "Planejamento" é um textarea simples (não CKEditor)

### 2. Listagens
- [ ] Coluna "Último PAEE" exibe apenas o ano (ex: "2025")
- [ ] Lista de PAEEs de um aluno exibe apenas o ano
- [ ] Não aparece "/" antes do ano

### 3. Relatórios
- [ ] Relatório Individual PAEE exibe apenas o ano
- [ ] Relatório Geral PAEE exibe apenas o ano
- [ ] Tabela de frequência exibe "Ano" como cabeçalho

## Rollback (se necessário)

### Para reverter as alterações:

1. **Reverter migração:**
```bash
python manage.py migrate neurodivergentes 0024
```

2. **Restaurar arquivos originais:**
- Restaurar `CKEditor5Field` no modelo
- Restaurar ordem original dos campos no formulário
- Restaurar formatação `get_mes_display()/ano` nos templates

## Observações Técnicas

- **Campo Planejamento:** Convertido de `CKEditor5Field` para `TextField` para permitir controle total da largura
- **Formatação de Data:** Removidas todas as referências a `get_mes_display()` pois o campo mês foi removido anteriormente
- **Compatibilidade:** Alterações são compatíveis com dados existentes
- **Performance:** Remoção do CKEditor melhora o carregamento da página

## Dependências
- Nenhuma nova dependência adicionada
- Dependência `django_ckeditor_5` pode ser removida se não usada em outros locais

---

**Status:** ✅ Pronto para Produção  
**Testado em:** Ambiente de Desenvolvimento  
**Impacto:** Baixo (apenas melhorias de UX)
