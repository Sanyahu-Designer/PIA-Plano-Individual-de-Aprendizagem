# Plano de Análise de Problema de Gráficos no Parecer

## Notes
- O usuário relatou que os gráficos aparecem corretamente na versão de desenvolvimento, mas não na produção.
- Os arquivos em produção estão em /home/sanyahu/Downloads/pia-prod-atual.
- Não é para alterar nada ainda, apenas localizar o erro e sugerir solução simples.
- Os arquivos de modelo, geração de gráficos e JS são idênticos nas duas versões.
- Templates de gráficos/administração também são idênticos nas duas versões.
- Não há diferenças aparentes nas views/admin.
- Não foram encontrados arquivos JS de gráficos (graficos_parecer.js) nos diretórios estáticos da produção.
- Diretório staticfiles não existe na produção, sugerindo possível problema na coleta/serviço de arquivos estáticos.
- Arquivos JS/CSS dos gráficos estão presentes em staticfiles na dev, mas ausentes na produção.
- Causa provável: falta de execução do comando collectstatic ou configuração incorreta do serviço de arquivos estáticos na produção.
- Usuário baixou arquivos estáticos reais da produção para /home/sanyahu/Downloads/pia-static-prod-atual para análise.
- Teste de acesso à CDN realizado via terminal no servidor: acesso ao Chart.js pela CDN está funcionando normalmente (HTTP 200).
- Usuário relatou que o problema ocorre na página de cadastro/edição do parecer, onde os gráficos e campos de data não aparecem na produção, mas aparecem em dev.
- É necessário investigar o template/formulário dessa página na produção e comparar com o da dev.
- Templates e JavaScript dos gráficos na página de cadastro/edição do parecer são idênticos entre produção e desenvolvimento.
- Problema pode estar relacionado ao contexto do Django Admin na produção, permissões, carregamento dinâmico dos campos ou algum bloqueio específico do ambiente produtivo.
- Problema de erro 500 ao salvar parecer na produção: coluna 'grafico_data_inicio' ausente no banco de dados (ProgrammingError 1054). É necessário rodar as migrations para criar os campos faltantes.
- As migrations executadas não criaram as colunas de gráfico; é preciso garantir que as migrations corretas para os campos de gráfico existam e sejam aplicadas.
- Solução mais simples no momento: criar manualmente as colunas no banco de dados de produção usando ALTER TABLE, já que o modelo está correto e as migrations não estão sendo detectadas/aplicadas automaticamente.
- Problema foi resolvido com sucesso após a criação manual das colunas no banco de dados de produção (ALTER TABLE).
- Novo problema relatado: não é possível adicionar mais de uma Meta/Habilidade na seção de cadastro do PDI, tanto em produção quanto em desenvolvimento. Usuário precisa inserir várias de uma vez sem ter que salvar e editar novamente. Investigar causa sem alterar nada ainda.
- Causa identificada: template customizado não estava sendo usado, apenas herdando o padrão do Django, por isso só era possível adicionar uma meta/habilidade por vez. Admin estava referenciando o template correto, mas sem customização. Solução de aumentar o parâmetro `extra` para 10 aplicada para teste.
- Solução mais elegante aplicada: admin agora usa o template customizado avançado (`novo_card_meta_habilidades.html`) com JavaScript dinâmico e `extra = 1`, permitindo adicionar até 10 ou mais Metas/Habilidades conforme necessidade do usuário, sem poluir visualmente a tela.
- Solução final adotada: admin usa template tabular padrão e `extra = 5` para garantir funcionalidade estável, mesmo que visualmente não seja ideal. Alteração simples e eficaz, pronta para produção.
- Novo objetivo: iniciar planejamento de módulo de agendamento de profissionais para atendimento de alunos/pacientes.
- Iniciar planejamento de módulo de agendamento de profissionais com foco em controle interno: registro de atendimentos por profissional, dia, hora, tempo de atendimento (45 minutos), confirmação de atendimento, relatórios básicos (dia, semana, mês, ano). Futuras integrações (SMS/WhatsApp) podem ser consideradas depois.
- Novo requisito: o agendamento deve permitir registrar atendimentos tanto para alunos/pacientes (individual) quanto para escolas (grupo), com tempo de atendimento flexível para escolas.
- Novo requisito: o agendamento deve permitir registrar atendimentos tanto para alunos/pacientes (individual) quanto para escolas (grupo), com tempo de atendimento flexível para escolas.

## Task List
- [x] Comparar arquivos relevantes entre produção e desenvolvimento.
- [x] Verificar presença e coleta correta dos arquivos estáticos (JS/CSS) de gráficos na produção.
- [x] Identificar diferenças em dependências, configurações de ambiente ou dados que possam afetar a renderização dos gráficos.
- [x] Apontar o que pode estar causando o problema.
- [x] Verificar se arquivos necessários realmente estão presentes em /home/sanyahu/Downloads/pia-static-prod-atual.
- [x] Verificar permissões dos arquivos estáticos, URLs de acesso e erros de JavaScript no console do navegador para identificar o motivo dos gráficos não aparecerem.
- [x] Verificar erros de JavaScript no console do navegador e permissões dos arquivos para identificar o motivo dos gráficos não aparecerem.
- [x] Sugerir a forma mais simples de corrigir.
- [x] Comparar template/formulário de cadastro/edição do parecer entre produção e dev e sugerir correção para garantir que os gráficos fiquem visíveis.
- [x] Sugerir correção do banco de dados (rodar migrations para criar as colunas faltantes).
- [x] Sugerir a solução final para o problema dos gráficos não aparecerem.
- [x] Investigar por que não é possível adicionar múltiplas Metas/Habilidades de uma só vez no cadastro de PDI (tanto em dev quanto produção).
- [x] Identificar a causa do problema de não conseguir adicionar múltiplas Metas/Habilidades no PDI (inline admin/formset).
- [x] Aplicar solução de aumentar o parâmetro `extra` para 10 no inline do admin e testar.
- [x] Ajustar admin para usar template tabular padrão e extra=5, solução estável e funcional, pronta para produção.
- [ ] Planejar módulo de agendamento básico para controle interno (atendimentos, confirmações, relatórios simples, suporte a atendimentos individuais e em grupo com tempo flexível).
- [ ] Planejar módulo de agendamento híbrido para atendimentos individuais, em grupo e escolas com tempo flexível.

## Current Goal
Planejar módulo de agendamento híbrido com suporte a atendimentos individuais, em grupo e escolas.