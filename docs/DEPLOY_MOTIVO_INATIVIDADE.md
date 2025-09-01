# Deploy - Campo Motivo da Inatividade

## Resumo da Implementação
Adição do campo `motivo_inatividade` no cadastro de alunos/pacientes para registrar o motivo quando um aluno é marcado como inativo (ex: transferência de cidade, mudança de escola).

## Arquivos Alterados

### 1. Modelo de Dados
**Arquivo:** `neurodivergentes/models/base.py`
- **Linhas:** 170-185
- **Alteração:** Adicionado campo `motivo_inatividade` como `TextField` opcional
- **Código:**
```python
motivo_inatividade = models.TextField(
    blank=True, 
    null=True,
    help_text="Descreva o motivo da inatividade (ex: transferência de cidade, mudança de escola)"
)
```

### 2. Configuração do Admin
**Arquivo:** `neurodivergentes/admin.py`
- **Linhas:** 146-159
- **Alteração:** Incluído campo no fieldset "Informações Escolares"
- **Posição:** Após os campos `escola`, `ano_escolar` e `ativo`

### 3. Formulário Personalizado
**Arquivo:** `neurodivergentes/forms.py`
- **Linhas:** 34-44
- **Alteração:** Adicionado widget Textarea para o campo
- **Código:**
```python
'motivo_inatividade': forms.Textarea(attrs={
    'placeholder': 'Ex: Transferência para outra cidade, mudança de escola...',
    'style': 'width: 100%;'
}),
```

### 4. Template de Edição
**Arquivo:** `templates/admin/neurodivergentes/neurodivergente/change_form.html`
- **Linhas:** 454-467
- **Alteração:** Adicionado campo na seção "Informações Escolares"
- **Posição:** Logo após o switch Ativo/Inativo

### 5. Template do Relatório
**Arquivo:** `templates/neurodivergentes/relatorio_aluno.html`
- **Linhas:** 342-349
- **Alteração:** Exibição condicional do campo no relatório
- **Condição:** Só aparece quando aluno está inativo E motivo está preenchido

## Migração do Banco de Dados

### Arquivo de Migração Gerado
- **Arquivo:** `neurodivergentes/migrations/0024_neurodivergente_motivo_inatividade.py`
- **Comando para aplicar:** `python manage.py migrate`

### SQL da Migração
```sql
ALTER TABLE `neurodivergentes_neurodivergente` 
ADD COLUMN `motivo_inatividade` longtext NULL;
```

## Instruções para Deploy em Produção

### 1. Backup do Banco de Dados
```bash
# Fazer backup completo antes do deploy
mysqldump -u [usuario] -p [senha] [nome_banco] > backup_pre_motivo_inatividade.sql
```

### 2. Aplicar Arquivos
Copiar os seguintes arquivos para produção:
- `neurodivergentes/models/base.py`
- `neurodivergentes/admin.py`
- `neurodivergentes/forms.py`
- `templates/admin/neurodivergentes/neurodivergente/change_form.html`
- `templates/neurodivergentes/relatorio_aluno.html`

### 3. Executar Migração
```bash
# No servidor de produção
python manage.py migrate
```

### 4. Reiniciar Servidor
```bash
# Reiniciar o servidor Django para aplicar as mudanças
sudo systemctl restart [nome_do_servico]
```

### 5. Verificações Pós-Deploy
- [ ] Acessar cadastro de aluno/paciente
- [ ] Verificar se campo "Motivo da Inatividade" aparece na seção "Informações Escolares"
- [ ] Testar salvamento do campo
- [ ] Verificar exibição no relatório (apenas para alunos inativos com motivo preenchido)
- [ ] Confirmar que campo não é obrigatório

## Funcionalidades Implementadas

### Interface Administrativa
- Campo sempre visível na seção "Informações Escolares"
- Posicionado após o switch Ativo/Inativo
- Widget Textarea com placeholder explicativo
- Campo não obrigatório (opcional)

### Relatório de Alunos
- Exibição condicional: só aparece quando necessário
- Condição: `aluno.ativo == False AND aluno.motivo_inatividade != null/empty`
- Layout: ocupa toda largura para acomodar textos longos
- Posicionamento: logo após o status Ativo/Inativo

## Casos de Uso
- Transferência de cidade
- Mudança de escola
- Abandono do tratamento
- Conclusão do acompanhamento
- Outros motivos administrativos

## Observações Técnicas
- Campo implementado como `TextField` para suportar textos longos
- Configurado com `blank=True, null=True` para ser opcional
- Help text explicativo para orientar o usuário
- Integração completa com sistema existente
- Sem impacto em funcionalidades existentes

## Rollback (se necessário)
Em caso de problemas, reverter com:
```bash
# Reverter migração
python manage.py migrate neurodivergentes 0023

# Restaurar backup
mysql -u [usuario] -p [senha] [nome_banco] < backup_pre_motivo_inatividade.sql
```

---
**Data de Implementação:** 29/08/2025  
**Desenvolvedor:** Cascade AI  
**Status:** ✅ Pronto para Produção
