# Deploy - Campo Ausências no Relatório Geral PDI

## Resumo da Implementação
Adição do campo "Ausências" no Relatório Geral do PDI, posicionado logo abaixo da "Frequência Média", mostrando a soma total de ausências no período solicitado.

## Arquivos Alterados

### 1. Template do Relatório PDF
**Arquivo:** `neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html`
- **Linhas:** 206-209
- **Alteração:** Adicionado campo "Ausências" após "Frequência Média"
- **Código:**
```html
<div class="info-item">
    <span class="info-label">Ausências:</span>
    {{ total_ausencias|default:0 }}
</div>
```

### 2. Template do Relatório HTML
**Arquivo:** `neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html`
- **Linhas:** 428-431
- **Alteração:** Adicionado campo "Ausências" após "Frequência Média"
- **Código:**
```html
<div class="info-item">
    <span class="info-label">Ausências:</span>
    <span>{{ total_ausencias|default:0 }}</span>
</div>
```

### 3. View de Geração do Relatório PDF
**Arquivo:** `neurodivergentes/views.py`
- **Linhas:** 394-395 e 410
- **Alteração:** Adicionado cálculo de ausências e inclusão no contexto
- **Código:**
```python
# Calcula total de ausências no período
total_ausencias = pdis.filter(status='ausente').count()

# No contexto:
'total_ausencias': total_ausencias,  # Adicionando total de ausências
```

### 4. View de Geração do Relatório HTML
**Arquivo:** `neurodivergentes/views.py`
- **Linhas:** 585-590 e 607
- **Alteração:** Adicionado cálculo de ausências e inclusão no contexto
- **Código:**
```python
# Calcula total de ausências no período
total_ausencias = PDI.objects.filter(
    neurodivergente=neurodivergente,
    data_criacao__range=(data_inicial_dt, data_final_dt),
    status='ausente'
).count()

# No contexto:
'total_ausencias': total_ausencias,  # Adicionando total de ausências
```

## Funcionalidades Implementadas

### Cálculo de Ausências
- **Critério:** PDIs com `status='ausente'` no período selecionado
- **Método:** Contagem direta via `.count()` no QuerySet filtrado
- **Período:** Respeitando as datas inicial e final do filtro do relatório

### Exibição no Relatório
- **Posição:** Logo abaixo da "Frequência Média"
- **Formato:** "Ausências: X" (onde X é o número total)
- **Valor padrão:** 0 (quando não há ausências)
- **Compatibilidade:** Funciona em ambas as versões (PDF e HTML)

### Layout Visual
- **PDF:** Segue o mesmo padrão dos outros campos informativos
- **HTML:** Mantém consistência visual com spans estruturadas
- **Responsivo:** Adapta-se ao layout existente do relatório

## Instruções para Deploy em Produção

### 1. Backup Preventivo
```bash
# Fazer backup dos templates antes da alteração
cp neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html.bak
cp neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html.bak
cp neurodivergentes/views.py neurodivergentes/views.py.bak
```

### 2. Aplicar Arquivos
Copiar os seguintes arquivos para produção:
- `neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html`
- `neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html`
- `neurodivergentes/views.py`

### 3. Reiniciar Servidor
```bash
# Reiniciar o servidor Django para aplicar as mudanças
sudo systemctl restart [nome_do_servico]
```

### 4. Verificações Pós-Deploy
- [ ] Acessar um aluno com PDIs no sistema
- [ ] Gerar Relatório Geral (versão PDF)
- [ ] Verificar se campo "Ausências" aparece após "Frequência Média"
- [ ] Gerar Relatório Geral (versão HTML)
- [ ] Confirmar que o cálculo está correto
- [ ] Testar com período que contenha ausências
- [ ] Testar com período sem ausências (deve mostrar 0)

## Casos de Teste

### Teste 1: Período com Ausências
- **Cenário:** Aluno com 3 PDIs no período, sendo 1 ausente
- **Resultado Esperado:** "Ausências: 1"

### Teste 2: Período sem Ausências
- **Cenário:** Aluno com PDIs apenas concluídos
- **Resultado Esperado:** "Ausências: 0"

### Teste 3: Período sem PDIs
- **Cenário:** Período sem nenhum PDI registrado
- **Resultado Esperado:** "Ausências: 0"

## Impacto no Sistema

### Alterações Mínimas
- **Sem migração de banco:** Não altera estrutura de dados
- **Sem quebra de compatibilidade:** Usa dados existentes
- **Performance:** Impacto mínimo (uma consulta adicional simples)

### Benefícios
- **Visibilidade:** Professores podem ver rapidamente quantas ausências o aluno teve
- **Análise:** Facilita identificação de padrões de frequência
- **Relatório completo:** Informação complementar à frequência média

## Status dos PDIs Considerados

### Para Ausências
- `status='ausente'` - Contabilizado como ausência

### Para Frequência Média (existente)
- `status='concluido'` - Contabilizado como atendimento realizado

### Outros Status (não afetados)
- `status='em_andamento'`
- `status='iniciado'`
- `status='suspenso'`
- `status='cancelado'`

## Rollback (se necessário)
Em caso de problemas, restaurar com:
```bash
# Restaurar backups
cp neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html.bak neurodivergentes/templates/neurodivergentes/relatorio_geral_aluno.html
cp neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html.bak neurodivergentes/templates/neurodivergentes/relatorio_geral_html.html
cp neurodivergentes/views.py.bak neurodivergentes/views.py

# Reiniciar servidor
sudo systemctl restart [nome_do_servico]
```

---
**Data de Implementação:** 29/08/2025  
**Desenvolvedor:** Cascade AI  
**Status:** ✅ Pronto para Produção  
**Dependências:** Nenhuma (usa estrutura existente)
