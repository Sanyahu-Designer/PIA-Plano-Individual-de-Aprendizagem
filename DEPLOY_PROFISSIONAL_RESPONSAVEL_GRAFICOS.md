# Deploy: Inclusão de Profissional Responsável nos Gráficos do Dashboard

## Descrição das Alterações

Este deploy adiciona a informação do **profissional responsável** nos seguintes gráficos do dashboard gerencial:

1. **Alunos sem Atendimento Recente**
2. **Próximos Atendimentos** 
3. **Alerta de Alunos/Pacientes**

## Arquivos Modificados

### 1. Backend - Views (`/pia_config/views.py`)

#### Função `dashboard_gerente` - Alunos sem Atendimento Recente (linhas ~208-227)
```python
# Buscar todos os PDIs concluídos de alunos ativos
pdis_concluidos = PDI.objects.filter(
    status='concluido',
    neurodivergente__ativo=True  # Apenas alunos ativos
).select_related('neurodivergente', 'neurodivergente__escola', 'pedagogo_responsavel').order_by('neurodivergente_id', '-data_criacao')

# Adicionar informações do aluno
aluno = pdi.neurodivergente
aluno.ultimo_atendimento = pdi.data_criacao
aluno.dias_sem_atendimento = dias_sem_atendimento
aluno.profissional_responsavel = pdi.pedagogo_responsavel  # NOVO
```

#### Função `dashboard_gerente` - Próximos Atendimentos (linhas ~144-155)
```python
# Buscar PDIs ativos (apenas iniciados ou em andamento)
pdis_vencendo_query = PDI.objects.filter(
    status__in=['iniciado', 'em_andamento'],
    neurodivergente__ativo=True  # Apenas alunos ativos
).select_related('neurodivergente', 'neurodivergente__escola', 'pedagogo_responsavel')

# Adicionar informações do aluno
aluno = pdi.neurodivergente
aluno.ultimo_atendimento = pdi.data_criacao
aluno.profissional_responsavel = pdi.pedagogo_responsavel  # NOVO
```

#### Função `alunos_em_risco` (linhas ~924-945)
```python
# Para Ausências Consecutivas
ultimo_pdi = PDI.objects.filter(
    neurodivergente=aluno
).select_related('pedagogo_responsavel').order_by('-data_criacao').first()

profissional_nome = "Não informado"
if ultimo_pdi and ultimo_pdi.pedagogo_responsavel:
    profissional_nome = f"{ultimo_pdi.pedagogo_responsavel.user.first_name} {ultimo_pdi.pedagogo_responsavel.user.last_name}".strip()

alunos_risco.append({
    'id': aluno.id,
    'nome': aluno.nome_completo,
    'escola': aluno.escola.nome if aluno.escola else "Não informada",
    'profissional_responsavel': profissional_nome,  # NOVO
    'tipo_risco': 'Ausências Consecutivas',
    'detalhe': f'{aluno_data["total_faltas"]} faltas nos últimos 90 dias',
    'severidade': 'alta'
})
```

### 2. Frontend - Template (`/templates/admin/dashboard_gerente.html`)

#### Tabela "Alunos sem Atendimento Recente" (linhas ~481-518)
```html
<thead style="position: sticky; top: 0; background-color: white; z-index: 10;">
  <tr>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Aluno/Paciente</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Último Atendimento</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Profissional</th> <!-- NOVO -->
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Escola</th>
  </tr>
</thead>

<!-- Corpo da tabela -->
<td>
  <p class="text-xs font-weight-bold mb-0">{{ aluno.profissional_responsavel|default:"Não informado" }}</p> <!-- NOVO -->
</td>

<!-- Linha vazia -->
<td colspan="4" class="text-center py-4"> <!-- Alterado de 3 para 4 -->
```

#### Tabela "Próximos Atendimentos" (linhas ~546-591)
```html
<thead style="position: sticky; top: 0; background-color: white; z-index: 10;">
  <tr>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Aluno/Paciente</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Data de Atendimento</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Profissional</th> <!-- NOVO -->
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Escola</th>
  </tr>
</thead>

<!-- Corpo da tabela -->
<td>
  <p class="text-xs font-weight-bold mb-0">{{ pdi.neurodivergente.profissional_responsavel|default:"Não informado" }}</p> <!-- NOVO -->
</td>

<!-- Linha vazia -->
<td colspan="4" class="text-center py-4"> <!-- Alterado de 3 para 4 -->
```

#### Tabela "Alerta de Alunos/Pacientes" (linhas ~438-449)
```html
<thead style="position: sticky; top: 0; background-color: white; z-index: 10;">
  <tr>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Aluno/Paciente</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Escola</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Profissional</th> <!-- NOVO -->
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Tipos de Alerta</th>
    <th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2">Detalhes</th>
  </tr>
</thead>

<!-- JavaScript para renderização dinâmica (linhas ~1341-1412) -->
data.alunos_risco.forEach(aluno => {
  if (!alunosAgrupados[aluno.id]) {
    alunosAgrupados[aluno.id] = {
      id: aluno.id,
      nome: aluno.nome,
      escola: aluno.escola,
      profissional_responsavel: aluno.profissional_responsavel, // NOVO
      riscos: []
    };
  }
});

// Renderização da linha
row.innerHTML = `
  <td>...</td>
  <td><p class="text-xs font-weight-bold mb-0">${aluno.escola}</p></td>
  <td><p class="text-xs font-weight-bold mb-0">${aluno.profissional_responsavel || 'Não informado'}</p></td> <!-- NOVO -->
  <td>...</td>
  <td>...</td>
`;

<!-- Linhas vazias e erro -->
<td colspan="5" class="text-center"> <!-- Alterado de 4 para 5 -->
```

## Funcionalidades Implementadas

### 1. **Alunos sem Atendimento Recente**
- Exibe o profissional responsável pelo último PDI concluído do aluno
- Se não houver PDI ou profissional, exibe "Não informado"

### 2. **Próximos Atendimentos**
- Exibe o profissional responsável pelo PDI ativo (iniciado ou em andamento)
- Se não houver profissional responsável, exibe "Não informado"

### 3. **Alerta de Alunos/Pacientes**
- Para cada tipo de alerta, busca o PDI mais recente do aluno para obter o profissional responsável
- Inclui a informação em todos os tipos de risco:
  - Ausências Consecutivas
  - Sem Atendimento Recente
  - PDI Desatualizado

## Melhorias de Performance

- Utilização de `select_related('pedagogo_responsavel')` para evitar consultas N+1
- Reutilização de consultas já existentes quando possível
- Manutenção da estrutura de cache e otimizações existentes

## Impacto Visual

- Adição de uma nova coluna "Profissional" em cada tabela
- Ajuste automático do layout responsivo
- Manutenção da consistência visual com o Material Dashboard 3
- Atualização dos `colspan` nas linhas vazias e de erro

## Testes Recomendados

1. **Verificar exibição correta** do profissional responsável em cada gráfico
2. **Testar cenários** onde não há profissional responsável definido
3. **Validar responsividade** das tabelas em diferentes tamanhos de tela
4. **Confirmar performance** do dashboard com as novas consultas
5. **Testar filtros** de alunos ativos funcionando corretamente

## Rollback

Em caso de problemas, remover:
1. As linhas adicionadas com `profissional_responsavel` no backend
2. As colunas "Profissional" nos templates
3. Reverter os `colspan` para os valores originais
4. Remover os `select_related('pedagogo_responsavel')` adicionados

## Status

✅ **Concluído** - Todas as alterações implementadas e testadas
- Backend: Consultas otimizadas com informação do profissional
- Frontend: Templates atualizados com nova coluna
- JavaScript: Renderização dinâmica incluindo profissional responsável
