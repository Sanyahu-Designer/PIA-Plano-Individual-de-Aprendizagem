# 📅 SISTEMA DE AGENDAMENTO PIA
## Proposta de Implementação - Versão Básica

---

## 🎯 **OBJETIVO**

Desenvolver um sistema básico de **controle e gestão de atendimentos** realizados pelos profissionais da equipe PIA, permitindo o registro, acompanhamento e relatórios de atendimentos tanto individuais quanto em grupo/escola.

---

## 📋 **FUNCIONALIDADES ESSENCIAIS**

### **1. Registro de Atendimentos**
- ✅ **Atendimentos Individuais**: Profissional + Aluno/Paciente
- ✅ **Atendimentos em Grupo**: Profissional + Escola (avaliações, reuniões)
- ✅ **Data e Hora**: Agendamento flexível
- ✅ **Duração Personalizada**: 45 min padrão para individual, tempo livre para grupo/escola

### **2. Controle de Status**
- **Agendado**: Atendimento marcado
- **Confirmado**: Atendimento confirmado pelo paciente/escola
- **Realizado**: Atendimento concluído com sucesso
- **Cancelado**: Atendimento cancelado
- **Não Compareceu**: Paciente/escola faltou

### **3. Tipos de Atendimento**
- **Individual**: Atendimento 1:1 com aluno/paciente
- **Grupo**: Atendimento com múltiplos alunos
- **Avaliação na Escola**: Visitas para avaliação institucional
- **Reunião/Orientação**: Reuniões com equipe escolar

### **4. Relatórios Gerenciais**
- **Por Período**: Dia, semana, mês, ano
- **Por Profissional**: Produtividade individual
- **Por Tipo**: Separação individual vs. grupo/escola
- **Estatísticas**: Total de atendimentos, tempo investido, taxa de comparecimento

---

## 🛠️ **ESPECIFICAÇÕES TÉCNICAS**

### **Plataforma**
- **Sistema**: Integração com o sistema PIA existente
- **Interface**: Django Admin customizado (familiar à equipe)
- **Banco de Dados**: MySQL (já em uso)
- **Relatórios**: Exportação para Excel/PDF

### **Validações Inteligentes**
- **Conflito de Horários**: Impede duplo agendamento do profissional
- **Campos Obrigatórios**: Validação de dados essenciais
- **Sugestões Automáticas**: Duração baseada no tipo de atendimento

---

## 📊 **BENEFÍCIOS ESPERADOS**

### **Para a Gestão**
- ✅ **Controle Total** dos atendimentos realizados
- ✅ **Relatórios Precisos** para tomada de decisão
- ✅ **Acompanhamento** da produtividade dos profissionais
- ✅ **Histórico Completo** de atendimentos por aluno/escola

### **Para os Profissionais**
- ✅ **Organização** da agenda de trabalho
- ✅ **Controle** de comparecimento dos pacientes
- ✅ **Registro** de observações importantes
- ✅ **Interface Simples** e intuitiva

### **Para a Instituição**
- ✅ **Profissionalização** do processo de agendamento
- ✅ **Dados Confiáveis** para relatórios institucionais
- ✅ **Base Sólida** para futuras expansões
- ✅ **Melhoria** na qualidade do atendimento

---

## ⏱️ **CRONOGRAMA DE IMPLEMENTAÇÃO**

### **Fase 1: Desenvolvimento Base (2 semanas)**
- Criação dos modelos de dados
- Interface básica no Django Admin
- Validações essenciais
- Testes iniciais

### **Fase 2: Interface e Relatórios (1 semana)**
- Customização da interface
- Implementação dos relatórios
- Filtros e buscas avançadas
- Testes de usabilidade

### **Fase 3: Refinamentos e Deploy (3-5 dias)**
- Ajustes finais baseados em feedback
- Documentação do usuário
- Deploy em produção
- Treinamento da equipe

**⏰ PRAZO TOTAL: 3-4 semanas**

---

## 💰 **INVESTIMENTO**

### **Desenvolvimento**
- **Custo**: Apenas tempo de desenvolvimento interno
- **Infraestrutura**: Utiliza recursos já existentes
- **Manutenção**: Integrada ao sistema atual

### **ROI (Retorno sobre Investimento)**
- **Economia de Tempo**: Automatização do controle manual
- **Redução de Erros**: Eliminação de planilhas e anotações
- **Melhoria na Gestão**: Decisões baseadas em dados reais
- **Profissionalização**: Imagem mais profissional da instituição

---

## 🚀 **EXPANSÕES FUTURAS**

### **Fase 2 (Futuro)**
- **Notificações SMS/WhatsApp**: Lembretes automáticos
- **Calendário Visual**: Interface mais moderna
- **App Mobile**: Acesso via smartphone
- **Integração Externa**: Google Calendar, etc.

### **Fase 3 (Futuro)**
- **Inteligência Artificial**: Sugestão automática de horários
- **Relatórios Avançados**: Business Intelligence
- **Portal do Paciente**: Agendamento online
- **Integração Financeira**: Controle de pagamentos

---

## 📊 **STATUS ATUAL DE IMPLEMENTAÇÃO**

### **✅ IMPLEMENTADO (100% Funcional)**
- ✅ Modelo de dados completo
- ✅ Interface Django Admin customizada
- ✅ Calendário visual com FullCalendar
- ✅ Sistema de permissões por perfil
- ✅ APIs CRUD completas
- ✅ Controle de status e validações
- ✅ Busca de pacientes e profissionais
- ✅ Filtros e relatórios básicos

### **❌ PENDENTE DE IMPLEMENTAÇÃO**
- ❌ **Envio de E-mails**: Campo `enviar_copia_gestor` existe mas funcionalidade não implementada
  - Falta: Signals automáticos
  - Falta: Templates de e-mail
  - Falta: Configuração SMTP
  - Falta: Lógica de envio baseada no checkbox

### **🎯 OBSERVAÇÕES**
- Sistema está **pronto para uso em produção** nas funcionalidades principais
- **Integração PDI e Agenda**: Removida conforme solicitação
- **Envio de e-mail**: Funcionalidade preparada mas não implementada

---

## ✅ **PRÓXIMOS PASSOS**

1. **Implementar envio de e-mails** (se necessário)
2. **Testes** com usuários reais
3. **Treinamento** da equipe
4. **Deploy em produção** (funcionalidades principais)
5. **Coleta de feedback** para melhorias

---

## 📞 **CONTATO PARA DÚVIDAS**

Para esclarecimentos adicionais sobre esta proposta, funcionalidades específicas ou cronograma, entre em contato com a equipe de desenvolvimento.

---

**Data**: 14 de Agosto de 2025  
**Versão**: 1.0 - Proposta Básica  
**Status**: Aguardando Aprovação

---

> 💡 **Nota**: Esta é uma proposta de sistema básico e funcional. Funcionalidades adicionais podem ser implementadas em fases futuras conforme necessidade e orçamento disponível.
