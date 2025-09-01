# DEPLOY - Correção de Terminologia PEI/PAEE

## Resumo das Alterações

Este deploy corrige a terminologia utilizada no sistema, alterando:
- **PAEE**: Lista de alunos do Público-Alvo da Educação Especial (anteriormente "PEI")
- **PEI**: Lista de Adaptação Curricular Individualizada (anteriormente "Adaptações")

## Arquivos Alterados

### 1. Módulo PAEE (Público-Alvo da Educação Especial)

#### `/neurodivergentes/models/pei.py`
**Alterações:**
- Linha 16: `help_text='Selecione o mês do PAEE'` (era "do PEI")
- Linha 35: `help_text='Selecione o ano do PAEE'` (era "do PEI")
- Linha 69: `return f"PAEE de {self.neurodivergente} - {self.get_mes_display()}/{self.ano}"` (era "PEI de")

#### `/neurodivergentes/admin.py`
**Alterações:**
- Linha 762: Comentário "Lista de PAEEs do aluno" (era "PEIs")
- Linha 763: Comentário "Detalhe do PAEE" (era "PEI")
- Linha 769: Comentário "Lista de PAEEs do aluno" (era "PEIs")
- Linha 772: Comentário "Detalhe do PAEE" (era "PEI")
- Linha 830: Docstring "Retorna as metas do PAEE" (era "PEI")

#### `/templates/admin/neurodivergentes/monitoramento/change_list_material_dashboard.html`
**Alterações:**
- Linha 108: Comentário "Cabeçalho para lista de PAEEs de um aluno específico" (era "PEIs")
- Linha 114: Comentário "Cabeçalho para lista geral de PAEEs" (era "PEIs")
- Linha 117: Cabeçalho da tabela "Total de PAEEs" (era "PEIs")
- Linha 118: Cabeçalho da tabela "Último PAEE" (era "PEI")
- Linha 162: Comentário "Dados para lista de PAEEs de um aluno específico" (era "PEIs")
- Linha 185: Comentário "Dados para lista geral de PAEEs" (era "PEIs")

### 2. Módulo PEI (Plano Educacional Individualizado)

#### `/adaptacao_curricular/admin.py`
**Alterações:**
- Linha 314: `get_total_adaptacoes.short_description = 'Total de PEIs'` (era "Adaptações")
- Linha 329: `get_ultima_adaptacao.short_description = 'Último PEI'` (era "Adaptação")
- Linha 341: Botão HTML "Ver PEIs" (era "Adaptações")
- Linha 344: `get_view_button.short_description = 'Ver PEIs'` (era "Adaptações")
- **Correção de sintaxe:** Linha 341-342: Adicionada vírgula faltante no `format_html()`

#### `/templates/admin/adaptacao_curricular/adaptacaocurricularindividualizada/change_list_material_dashboard.html`
**Alterações:**
- Linha 116: Cabeçalho da tabela "Total de PEIs" (era "Adaptações")
- Linha 117: Cabeçalho da tabela "Último PEI" (era "Adaptação")
- Linha 198: Botão de ação "Ver PEIs" (era "PEI")

## Instruções de Deploy

### 1. Backup
Faça backup dos arquivos antes de aplicar as alterações:
```bash
# Backup dos arquivos principais
cp neurodivergentes/models/pei.py neurodivergentes/models/pei.py.bak
cp neurodivergentes/admin.py neurodivergentes/admin.py.bak
cp adaptacao_curricular/admin.py adaptacao_curricular/admin.py.bak
```

### 2. Aplicação das Alterações
Substitua os arquivos pelos novos conteúdos conforme as alterações listadas acima.

### 3. Verificação
Após o deploy, verifique:
- [ ] Lista PAEE exibe "Total de PAEEs" e "Último PAEE"
- [ ] Lista PEI exibe "Total de PEIs" e "Último PEI"
- [ ] Botões de ação exibem "Ver PAEEs" e "Ver PEIs" respectivamente
- [ ] Não há erros de sintaxe no código

### 4. Reinicialização
Reinicie o servidor Django para aplicar as alterações:
```bash
# Em desenvolvimento
python manage.py runserver

# Em produção (exemplo com gunicorn)
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## Impacto

### Positivo
- ✅ Terminologia educacional correta e consistente
- ✅ Interface mais clara para usuários
- ✅ Conformidade com nomenclatura oficial

### Riscos
- ⚠️ Usuários podem precisar de orientação sobre a nova terminologia
- ⚠️ Documentação existente pode precisar de atualização

## Validação

Após o deploy, teste:
1. Acesse a lista PAEE e verifique os cabeçalhos das colunas
2. Acesse a lista PEI e verifique os cabeçalhos das colunas
3. Teste os botões "Ver PAEEs" e "Ver PEIs"
4. Verifique se não há erros no console do navegador

## Data do Deploy
**Data:** 29/08/2025  
**Responsável:** Sanyahu  
**Versão:** 1.0  

## Rollback
Em caso de problemas, restaure os arquivos de backup:
```bash
cp neurodivergentes/models/pei.py.bak neurodivergentes/models/pei.py
cp neurodivergentes/admin.py.bak neurodivergentes/admin.py
cp adaptacao_curricular/admin.py.bak adaptacao_curricular/admin.py
```
