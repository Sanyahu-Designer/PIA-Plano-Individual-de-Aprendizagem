# ANÁLISE DE COMPATIBILIDADE - CAMPOS MODELO vs PRODUÇÃO

## COMPARAÇÃO DETALHADA DOS CAMPOS

### ✅ CAMPOS COMPATÍVEIS (NOT NULL em produção = obrigatório no modelo)

| Campo | Produção | Modelo Atual | Status |
|-------|----------|--------------|--------|
| `primeiro_nome` | `varchar(50) NOT NULL` | `CharField(max_length=50)` | ✅ OK |
| `ultimo_nome` | `varchar(50) NOT NULL` | `CharField(max_length=50)` | ✅ OK |
| `data_nascimento` | `date NOT NULL` | `DateField()` | ✅ OK |
| `genero` | `varchar(1) NOT NULL` | `CharField(max_length=1, choices=...)` | ✅ OK |
| `cpf` | `varchar(14) NOT NULL` | `CharField(max_length=14)` | ✅ OK |
| `estado_nascimento` | `varchar(2) NOT NULL` | `CharField(max_length=2, choices=...)` | ✅ OK |
| `cidade_nascimento` | `varchar(100) NOT NULL` | `CharField(max_length=100)` | ✅ OK |
| `cep` | `varchar(9) NOT NULL` | `CharField(max_length=9)` | ✅ OK (CORRIGIDO) |
| `endereco` | `varchar(255) NOT NULL` | `CharField(max_length=255)` | ✅ OK |
| `numero` | `varchar(10) NOT NULL` | `CharField(max_length=10)` | ✅ OK |
| `bairro` | `varchar(100) NOT NULL` | `CharField(max_length=100)` | ✅ OK |
| `cidade` | `varchar(100) NOT NULL` | `CharField(max_length=100)` | ✅ OK |
| `estado` | `varchar(2) NOT NULL` | `CharField(max_length=2, choices=...)` | ✅ OK |
| `ativo` | `tinyint(1) NOT NULL DEFAULT 0` | `BooleanField(default=False)` | ✅ OK |

### ✅ CAMPOS NOT NULL MAS COM STRINGS VAZIAS EM PRODUÇÃO

| Campo | Produção | Dados Reais | Modelo Atual | Status |
|-------|----------|-------------|--------------|--------|
| `cor_pele` | `varchar(10) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |
| `nacionalidade` | `varchar(20) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |
| `pais_origem` | `varchar(50) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |
| `tipo_sanguineo` | `varchar(3) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |
| `estado_nascimento` | `varchar(2) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |
| `cidade_nascimento` | `varchar(100) NOT NULL` | `''` (string vazia) | `CharField(blank=True)` | ✅ OK |

### ✅ CAMPOS OPCIONAIS (DEFAULT NULL em produção = opcional no modelo)

| Campo | Produção | Modelo Atual | Status |
|-------|----------|--------------|--------|
| `rg` | `varchar(20) DEFAULT NULL` | `CharField(blank=True, null=True)` | ✅ OK |
| `complemento` | `varchar(100) DEFAULT NULL` | `CharField(blank=True, null=True)` | ✅ OK |
| `celular` | `varchar(15) DEFAULT NULL` | `CharField(blank=True, null=True)` | ✅ OK |
| `email` | `varchar(254) DEFAULT NULL` | `EmailField(blank=True, null=True)` | ✅ OK |
| `foto_perfil` | `varchar(100) DEFAULT NULL` | `ImageField(blank=True, null=True)` | ✅ OK |
| `escola_id` | `bigint(20) DEFAULT NULL` | `ForeignKey(null=True, blank=True)` | ✅ OK |
| `ano_escolar_id` | `bigint(20) DEFAULT NULL` | `CharField(blank=True)` | ✅ OK |

## ✅ ANÁLISE CORRIGIDA

**IMPORTANTE**: Campos `NOT NULL` no banco podem ter strings vazias (`''`) nos dados reais.

**CORREÇÕES APLICADAS**:
1. **cep**: Removido `blank=True, null=True` - campo realmente obrigatório
2. **estado_nascimento**: Adicionado `blank=True` - dados têm strings vazias
3. **cidade_nascimento**: Adicionado `blank=True` - dados têm strings vazias
4. **cor_pele**: Mantido `blank=True` - dados têm strings vazias
5. **nacionalidade**: Mantido `blank=True` - dados têm strings vazias
6. **pais_origem**: Mantido `blank=True` - dados têm strings vazias
7. **tipo_sanguineo**: Mantido `blank=True` - dados têm strings vazias

## CAMPOS NOVOS (não existem em produção)

- `naturalidade`: Campo novo, pode ser opcional

## OBSERVAÇÕES

- Campo `ano_escolar` em produção é ForeignKey (`ano_escolar_id`), no modelo é CharField
- Todos os campos de endereço são obrigatórios em produção
- Campos de contato (celular, email) são opcionais
- Campos de identificação (cor_pele, nacionalidade, etc.) são obrigatórios em produção

## RISCO

❌ **ALTO RISCO**: Deploy falhará se os campos obrigatórios não forem corrigidos antes do deploy.
