-- =====================================================
-- SCRIPT DE CONVERSÃO DO BANCO PARA COMPATIBILIDADE
-- Sistema PIA - Deploy Seguro
-- Data: 30/08/2025
-- =====================================================

-- IMPORTANTE: Execute este script ANTES de aplicar as migrações!

-- =====================================================
-- 1. CONVERSÃO DO CAMPO ano_escolar (ForeignKey → CharField)
-- =====================================================

-- Passo 1: Adicionar nova coluna temporária
ALTER TABLE neurodivergentes_neurodivergente 
ADD COLUMN ano_escolar_temp VARCHAR(50) DEFAULT '';

-- Passo 2: Mapear IDs para strings baseado nos dados da produção
-- Mapeamento baseado na tabela neurodivergentes_seriescursadas da produção:
UPDATE neurodivergentes_neurodivergente 
SET ano_escolar_temp = CASE 
    WHEN ano_escolar_id = 1 THEN 'bercario1'     -- Berçário I
    WHEN ano_escolar_id = 2 THEN 'bercario2'     -- Berçário II
    WHEN ano_escolar_id = 3 THEN 'maternal1'     -- Maternal I
    WHEN ano_escolar_id = 4 THEN 'maternal2'     -- Maternal II
    WHEN ano_escolar_id = 5 THEN 'pre1'          -- Pré I
    WHEN ano_escolar_id = 6 THEN 'pre2'          -- Pré II
    WHEN ano_escolar_id = 7 THEN '1ano'          -- 1º Ano
    WHEN ano_escolar_id = 8 THEN '2ano'          -- 2º Ano
    WHEN ano_escolar_id = 9 THEN '3ano'          -- 3º Ano
    WHEN ano_escolar_id = 10 THEN '4ano'         -- 4º Ano
    WHEN ano_escolar_id = 11 THEN '5ano'         -- 5º Ano
    WHEN ano_escolar_id = 12 THEN '6ano'         -- 6º Ano
    WHEN ano_escolar_id = 13 THEN '7ano'         -- 7º Ano
    WHEN ano_escolar_id = 14 THEN '8ano'         -- 8º Ano
    WHEN ano_escolar_id = 15 THEN '9ano'         -- 9º Ano
    ELSE ''
END;

-- Passo 3: Remover coluna antiga
ALTER TABLE neurodivergentes_neurodivergente 
DROP FOREIGN KEY IF EXISTS neurodivergentes_neurodivergente_ano_escolar_id_fkey;

ALTER TABLE neurodivergentes_neurodivergente 
DROP COLUMN ano_escolar_id;

-- Passo 4: Renomear coluna temporária
ALTER TABLE neurodivergentes_neurodivergente 
CHANGE COLUMN ano_escolar_temp ano_escolar VARCHAR(50) DEFAULT '';

-- =====================================================
-- 2. VERIFICAÇÃO DOS RESULTADOS
-- =====================================================

-- Verificar se a conversão foi bem-sucedida
SELECT 
    ano_escolar,
    COUNT(*) as quantidade
FROM neurodivergentes_neurodivergente 
GROUP BY ano_escolar
ORDER BY quantidade DESC;

-- Verificar se não há valores NULL
SELECT COUNT(*) as registros_com_ano_escolar_null
FROM neurodivergentes_neurodivergente 
WHERE ano_escolar IS NULL;

-- =====================================================
-- 3. COMANDOS PARA DESCOBRIR MAPEAMENTOS (EXECUTAR ANTES)
-- =====================================================

-- Execute este comando ANTES da conversão para ver todos os IDs:
-- SELECT DISTINCT ano_escolar_id, COUNT(*) as quantidade
-- FROM neurodivergentes_neurodivergente 
-- WHERE ano_escolar_id IS NOT NULL
-- GROUP BY ano_escolar_id
-- ORDER BY ano_escolar_id;

-- =====================================================
-- OBSERVAÇÕES IMPORTANTES:
-- =====================================================

-- 1. Execute o backup ANTES deste script
-- 2. Teste em ambiente de desenvolvimento primeiro
-- 3. Verifique se todos os IDs estão mapeados
-- 4. Após este script, as migrações Django funcionarão normalmente
-- 5. Este script resolve a incompatibilidade ForeignKey vs CharField

-- =====================================================
-- ROLLBACK (caso necessário):
-- =====================================================

-- Para reverter (só execute se algo der errado):
-- ALTER TABLE neurodivergentes_neurodivergente ADD COLUMN ano_escolar_id BIGINT(20) DEFAULT NULL;
-- -- Recriar os mapeamentos inversos
-- -- Recriar a foreign key constraint
