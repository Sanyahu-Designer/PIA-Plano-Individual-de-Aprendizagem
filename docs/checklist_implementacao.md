# Checklist de Implementação – PIA (Plano Individual de Aprendizagem)

Este documento serve como guia de acompanhamento do progresso do projeto, detalhando o status de cada funcionalidade e melhoria prevista no sistema. Atualize este checklist conforme novas entregas forem realizadas.

Legenda dos status:
- [x] Implementado/concluído
- [ ] Planejado, em andamento ou não iniciado

---

## 1. Dashboard e Métricas
- [x] Cards obrigatórios: Escolas com Maior Demanda, Alunos sem Atendimento Recente, Próximos Atendimentos
- [x] Gráfico "Neurodivergências por Escola" com popover ajustado (placement: left)
- [ ] Visão geral customizada por perfil (em andamento)
- [ ] Métricas avançadas e filtros dinâmicos (planejado)

## 2. Templates e Interface
- [x] Templates de listagem padronizados (Material Dashboard 3)
- [x] Templates de edição padronizados (fieldsets, botões, breadcrumbs, responsividade)
- [x] Página de perfil com abas (Perfil, Profissional, Configurações)
- [x] Botões "Adicionar Novo" nas páginas de listagem, com estilo outline
- [x] Breadcrumbs padronizados em todas as páginas
- [x] Cards "Grupo Familiar" com layout e interações documentados
- [x] Página de agrupamento de Usuários/Grupos seguindo padrão visual
- [x] Ocultação/renomeação de cards específicos (ex: "Atividade da Rotina", "Metas/Habilidades PEI")
- [x] Interface moderna para permissões (cards por app, busca, seleção em massa)
- [ ] Templates personalizados para relatórios (PEI, Evolução) (em andamento)

## 3. Campos e Componentes
- [x] Campos Select2 padronizados (bordas, altura, placeholder, sem botão X, sem seta)
- [x] Inicialização robusta do Select2 em campos críticos (Aluno/Paciente, Escola, Ano Escolar)
- [x] Botões de ação (Adicionar, Excluir) nos inlines de Metas/Habilidades corrigidos e padronizados
- [x] Prevenção de duplicação de campos ao adicionar novos itens
- [x] Coluna de anexo com ícone clicável nas listas
- [x] Indicação visual de campos obrigatórios

## 4. Segurança
- [ ] Auditoria de logs (em andamento)
- [ ] Criptografia de dados sensíveis além das senhas (em andamento)
- [ ] Autenticação 2FA (planejado)
- [ ] Rate limiting (planejado)
- [ ] Política de senhas aprimorada (planejado)

## 5. Performance
- [x] Paginação em todas as listagens
- [ ] Otimização de queries (em andamento)
- [ ] Lazy loading de imagens (planejado)
- [ ] Minificação de assets (CSS/JS) (planejado)
- [ ] CDN para arquivos estáticos (planejado)

## 6. Documentação
- [x] Guia de padronização visual (documentação interna)
- [x] Documentação de componentes visuais (ex: Grupo Familiar)
- [ ] Manual do usuário (em andamento)
- [ ] Documentação técnica (em andamento)
- [ ] Documentação da API (planejado)
- [ ] Guias de implantação (planejado)
- [ ] FAQ (planejado)

## 7. Suporte
- [ ] Sistema de tickets (planejado)
- [ ] Base de conhecimento (planejado)
- [ ] Chat de suporte (planejado)
- [ ] Treinamentos online (planejado)

## 8. Multilocação (Multi-tenant)
- [ ] Estrutura multi-tenant ([detalhes e etapas completas no checklist_multilocacao.md](./checklist_multilocacao.md)) (em andamento)
- [x] Modelos principais mapeados para isolamento por prefeitura
- [ ] Migração para PostgreSQL (opcional, para isolamento avançado) (planejado)
- [ ] Personalização visual por prefeitura (planejado)
- [ ] Testes de isolamento e performance multi-tenant (planejado)

## 9. LGPD e Conformidade
- [ ] Adequação à LGPD ([detalhes e etapas completas no LGPD_CHECKLIST.md](./LGPD_CHECKLIST.md)) (em andamento)
- [x] Base legal, controlador e canal do titular definidos
- [x] HTTPS implementado
- [ ] Criptografia de dados sensíveis em repouso (em andamento)
- [ ] Controle de acesso rigoroso e revisão de permissões (em andamento)
- [ ] Autenticação 2FA para administradores (planejado)
- [ ] Página interna para auditoria de logs (planejado)
- [x] Política de privacidade publicada

## 10. Arquitetura e Escalabilidade
- [ ] Implementar cache distribuído (Redis/Memcached)
- [ ] Adicionar balanceamento de carga para distribuição de acessos
- [ ] Conteinerização da aplicação usando Docker
- [x] Implementar CI/CD (Integração e Entrega Contínuas) com GitHub Actions (em andamento)
- [x] Separação de ambientes (dev/staging/prod)

---

## Observações Gerais
- A fonte padrão é Roboto, com fallback para Helvetica e Arial (Material Dashboard 3)
- Todos os estilos seguem a identidade visual do Material Dashboard 3
- Melhorias e correções são registradas em MEMÓRIAS e documentações internas para rastreabilidade
- **Para detalhes técnicos e etapas completas de LGPD e Multilocação, consulte os arquivos dedicados em `/docs`.**

---

*Última atualização: 25/04/2025*
