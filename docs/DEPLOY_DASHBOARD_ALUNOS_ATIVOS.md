# Deploy - Correção Dashboard para Mostrar Apenas Alunos Ativos

## Resumo
Correção dos gráficos e estatísticas do dashboard gerencial para exibir apenas alunos/pacientes com status "Ativo", excluindo automaticamente os inativos de todos os cálculos.

## Problema Identificado
O dashboard estava incluindo alunos inativos em diversos gráficos e estatísticas, causando inconsistência nos dados apresentados aos gestores.

## Arquivo Alterado

### `/pia_config/views.py`
Função `dashboard_gerente` e funções auxiliares de gráficos

## Alterações Detalhadas

### 1. Total de Alunos (linha 82)
**Antes:**
```python
total_alunos = Neurodivergente.objects.count()
```
**Depois:**
```python
total_alunos = Neurodivergente.objects.filter(ativo=True).count()
```

### 2. Novos Alunos no Mês (linha 86)
**Antes:**
```python
novos_alunos_mes = Neurodivergente.objects.filter(created_at__gte=um_mes_atras).count()
```
**Depois:**
```python
novos_alunos_mes = Neurodivergente.objects.filter(created_at__gte=um_mes_atras, ativo=True).count()
```

### 3. Distribuição por Gênero (linhas 92-93)
**Antes:**
```python
total_masculino = Neurodivergente.objects.filter(genero='M').count()
total_feminino = Neurodivergente.objects.filter(genero='F').count()
```
**Depois:**
```python
total_masculino = Neurodivergente.objects.filter(genero='M', ativo=True).count()
total_feminino = Neurodivergente.objects.filter(genero='F', ativo=True).count()
```

### 4. Alunos em Investigação (linhas 128-130)
**Antes:**
```python
total_alunos_investigacao = Neurodivergente.objects.exclude(
    id__in=alunos_com_neurodivergencia
).count()
```
**Depois:**
```python
total_alunos_investigacao = Neurodivergente.objects.exclude(
    id__in=alunos_com_neurodivergencia
).filter(ativo=True).count()
```

### 5. Distribuição por Idade (linha 258)
**Antes:**
```python
for aluno in Neurodivergente.objects.all():
```
**Depois:**
```python
for aluno in Neurodivergente.objects.filter(ativo=True):
```

### 6. Dados Mensais (linhas 303-306)
**Antes:**
```python
count = Neurodivergente.objects.filter(
    created_at__gte=inicio_mes,
    created_at__lte=fim_mes
).count()
```
**Depois:**
```python
count = Neurodivergente.objects.filter(
    created_at__gte=inicio_mes,
    created_at__lte=fim_mes,
    ativo=True
).count()
```

### 7. Gráfico Gênero por Neurodivergência (linhas 566-568)
**Adicionado filtro:**
```python
# Verificar se o aluno está ativo
if not neurodivergente.ativo:
    continue
```

### 8. Distribuição por Neurodivergência (linhas 688-691)
**Adicionado filtro:**
```python
# Verificar se o aluno está ativo
neurodivergente = diagnostico.neurodivergencia.neurodivergente
if not neurodivergente.ativo:
    continue
```

### 9. Análise de Alunos em Risco (linhas 940-945)
**Antes:**
```python
todos_alunos = Neurodivergente.objects.all()
for aluno in Neurodivergente.objects.all():
```
**Depois:**
```python
todos_alunos = Neurodivergente.objects.filter(ativo=True)
for aluno in Neurodivergente.objects.filter(ativo=True):
```

## Instruções de Deploy

### 1. Backup
```bash
# Backup do banco de dados
mysqldump -u [usuario] -p [nome_banco] > backup_pre_dashboard_ativos_$(date +%Y%m%d_%H%M%S).sql

# Backup do arquivo alterado
cp pia_config/views.py pia_config/views.py.bak
```

### 2. Deploy do Arquivo
```bash
# Copiar arquivo alterado para produção
scp pia_config/views.py servidor:/caminho/projeto/pia_config/
```

### 3. Reiniciar Serviços
```bash
# No servidor de produção
cd /caminho/projeto
sudo systemctl restart pia-app
sudo systemctl restart nginx  # se necessário
```

## Verificações Pós-Deploy

### 1. Testar Dashboard
- [ ] Acessar dashboard gerencial
- [ ] Verificar se total de alunos mostra apenas ativos
- [ ] Confirmar que gráficos excluem alunos inativos
- [ ] Validar estatísticas de distribuição por gênero
- [ ] Testar gráfico de alunos em investigação

### 2. Casos de Teste

#### Teste 1: Total de Alunos
1. Contar alunos ativos manualmente no banco
2. Comparar com valor exibido no dashboard
3. **Esperado**: Valores devem ser iguais

#### Teste 2: Distribuição por Gênero
1. Verificar percentuais no dashboard
2. Calcular manualmente com base em alunos ativos
3. **Esperado**: Percentuais corretos apenas para ativos

#### Teste 3: Alunos em Investigação
1. Verificar valor no dashboard
2. Contar alunos ativos sem neurodivergência
3. **Esperado**: Apenas alunos ativos sem diagnóstico

#### Teste 4: Gráficos de Neurodivergência
1. Verificar gráficos por gênero e distribuição
2. Confirmar que não incluem diagnósticos de inativos
3. **Esperado**: Dados consistentes apenas para ativos

## Rollback (se necessário)

### 1. Restaurar Arquivo
```bash
cp pia_config/views.py.bak pia_config/views.py
```

### 2. Reiniciar Serviços
```bash
sudo systemctl restart pia-app
```

## Impacto das Alterações

### Positivo
- **Consistência**: Todos os gráficos agora mostram dados consistentes
- **Precisão**: Estatísticas refletem apenas alunos em atendimento ativo
- **Gestão**: Melhor visibilidade para tomada de decisões
- **Performance**: Não há impacto negativo na performance

### Observações
- **Compatibilidade**: Totalmente compatível com dados existentes
- **Reversibilidade**: Alterações podem ser revertidas facilmente
- **Sem Migração**: Não requer alterações no banco de dados

## Validação de Dados

### Consultas SQL para Verificação
```sql
-- Total de alunos ativos
SELECT COUNT(*) FROM neurodivergentes_neurodivergente WHERE ativo = 1;

-- Distribuição por gênero (apenas ativos)
SELECT genero, COUNT(*) FROM neurodivergentes_neurodivergente 
WHERE ativo = 1 GROUP BY genero;

-- Alunos ativos sem neurodivergência
SELECT COUNT(*) FROM neurodivergentes_neurodivergente n
WHERE ativo = 1 AND NOT EXISTS (
    SELECT 1 FROM neurodivergentes_neurodivergencia nd 
    WHERE nd.neurodivergente_id = n.id
);
```

## Status
- [x] Desenvolvimento concluído
- [x] Testes locais realizados
- [x] Documentação criada
- [ ] Deploy em produção
- [ ] Testes em produção
- [ ] Validação final

---
**Data de Criação**: 2025-08-29  
**Responsável**: Sistema PIA - Desenvolvimento  
**Versão**: 1.0  
**Prioridade**: Alta
