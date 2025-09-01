# Deploy - Campo Naturalidade no Cadastro de Alunos/Pacientes

## Resumo
Adição do campo `naturalidade` no cadastro de alunos/pacientes, permitindo o registro da cidade/local de nascimento como campo opcional na seção "Informações Complementares".

## Arquivos Alterados

### 1. Modelo - `/neurodivergentes/models/base.py`
**Linhas 64-84**: Adicionado campo `naturalidade`
```python
naturalidade = models.CharField(
    max_length=100, 
    blank=True, 
    null=True,
    help_text="Cidade ou local de nascimento (ex: Porto Alegre/RS, São Paulo/SP)"
)
```

### 2. Admin - `/neurodivergentes/admin.py`
**Linhas 127-148**: Incluído campo na seção "Informações Complementares"
```python
('Informações Complementares', {
    'fields': (
        ('nacionalidade', 'naturalidade'),
        ('estado_nascimento', 'cidade_nascimento'),
        # ... outros campos
    )
}),
```

### 3. Formulário - `/neurodivergentes/forms.py`
**Linhas 40-53**: Adicionado widget para o campo
```python
'naturalidade': forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Ex: Porto Alegre/RS, São Paulo/SP'
}),
```

### 4. Template Relatório - `/templates/neurodivergentes/relatorio_aluno.html`
**Linhas 339-349**: Atualizado para usar o novo campo
```html
<tr>
    <td><strong>Naturalidade:</strong></td>
    <td>{{ aluno.naturalidade|default:"Não informado" }}</td>
</tr>
```

### 5. Migração - `/neurodivergentes/migrations/0023_neurodivergente_naturalidade.py`
Nova migração criada para adicionar o campo no banco de dados.

## Instruções de Deploy

### 1. Backup
```bash
# Backup do banco de dados
mysqldump -u [usuario] -p [nome_banco] > backup_pre_naturalidade_$(date +%Y%m%d_%H%M%S).sql

# Backup dos arquivos alterados
cp neurodivergentes/models/base.py neurodivergentes/models/base.py.bak
cp neurodivergentes/admin.py neurodivergentes/admin.py.bak
cp neurodivergentes/forms.py neurodivergentes/forms.py.bak
cp templates/neurodivergentes/relatorio_aluno.html templates/neurodivergentes/relatorio_aluno.html.bak
```

### 2. Deploy dos Arquivos
```bash
# Copiar arquivos alterados para produção
scp neurodivergentes/models/base.py servidor:/caminho/projeto/neurodivergentes/models/
scp neurodivergentes/admin.py servidor:/caminho/projeto/neurodivergentes/
scp neurodivergentes/forms.py servidor:/caminho/projeto/neurodivergentes/
scp templates/neurodivergentes/relatorio_aluno.html servidor:/caminho/projeto/templates/neurodivergentes/
scp neurodivergentes/migrations/0023_neurodivergente_naturalidade.py servidor:/caminho/projeto/neurodivergentes/migrations/
```

### 3. Aplicar Migração
```bash
# No servidor de produção
cd /caminho/projeto
python manage.py migrate neurodivergentes
```

### 4. Reiniciar Serviços
```bash
# Reiniciar aplicação (exemplo com systemd)
sudo systemctl restart pia-app
sudo systemctl restart nginx  # se necessário
```

## Verificações Pós-Deploy

### 1. Verificar Estrutura do Banco
```sql
DESCRIBE neurodivergentes_neurodivergente;
-- Deve mostrar o campo 'naturalidade' varchar(100) NULL
```

### 2. Testar Interface Admin
- [ ] Acessar cadastro de novo aluno/paciente
- [ ] Verificar se campo "Naturalidade" aparece na seção "Informações Complementares"
- [ ] Testar preenchimento e salvamento do campo
- [ ] Verificar se o campo aceita valores em branco (opcional)

### 3. Testar Relatório
- [ ] Gerar relatório de aluno com campo naturalidade preenchido
- [ ] Verificar se exibe corretamente no relatório
- [ ] Testar aluno sem naturalidade (deve mostrar "Não informado")

### 4. Casos de Teste

#### Teste 1: Campo Preenchido
1. Cadastrar/editar aluno
2. Preencher naturalidade: "Porto Alegre/RS"
3. Salvar
4. Gerar relatório
5. **Esperado**: Campo exibe "Porto Alegre/RS"

#### Teste 2: Campo Vazio
1. Cadastrar/editar aluno
2. Deixar naturalidade em branco
3. Salvar
4. Gerar relatório
5. **Esperado**: Campo exibe "Não informado"

#### Teste 3: Compatibilidade
1. Verificar alunos existentes
2. **Esperado**: Campo naturalidade vazio, sem erros

## Rollback (se necessário)

### 1. Reverter Migração
```bash
python manage.py migrate neurodivergentes 0022
```

### 2. Restaurar Arquivos
```bash
cp neurodivergentes/models/base.py.bak neurodivergentes/models/base.py
cp neurodivergentes/admin.py.bak neurodivergentes/admin.py
cp neurodivergentes/forms.py.bak neurodivergentes/forms.py
cp templates/neurodivergentes/relatorio_aluno.html.bak templates/neurodivergentes/relatorio_aluno.html
```

### 3. Remover Migração
```bash
rm neurodivergentes/migrations/0023_neurodivergente_naturalidade.py
```

### 4. Reiniciar Serviços
```bash
sudo systemctl restart pia-app
```

## Observações Importantes

1. **Campo Opcional**: O campo naturalidade é opcional e não afeta registros existentes
2. **Compatibilidade**: Totalmente compatível com dados existentes
3. **Performance**: Não impacta performance (campo simples, sem índices especiais)
4. **Validação**: Aceita até 100 caracteres, permite valores em branco
5. **Help Text**: Interface fornece exemplo de preenchimento para o usuário

## Status
- [x] Desenvolvimento concluído
- [x] Migração aplicada em desenvolvimento
- [x] Testes locais realizados
- [ ] Deploy em produção
- [ ] Testes em produção
- [ ] Validação final

---
**Data de Criação**: $(date +%Y-%m-%d)  
**Responsável**: Sistema PIA - Desenvolvimento  
**Versão**: 1.0
