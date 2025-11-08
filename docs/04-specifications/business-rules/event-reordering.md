# Regras de Negócio: Event Reordering

- **Versão:** 1.0
- **Data:** 06 de Novembro de 2025
- **Status:** Especificação Formal

---

## Visão Geral

O Event Reordering System é responsável por detectar conflitos temporais entre eventos da agenda do usuário e apresentar estas informações de forma clara. O sistema segue um princípio fundamental: nunca tomar decisões automáticas sobre a agenda do usuário, apenas informar e sugerir quando solicitado.

## Princípios Fundamentais

### Princípio 1: Controle Explícito do Usuário

O TimeBlock é uma ferramenta de sugestão e organização, não um sistema de decisão autônoma. Em nenhum momento o sistema deve alterar a agenda do usuário sem aprovação explícita. O usuário mantém controle total sobre sua agenda em todos os momentos.

### Princípio 2: Informação sem Imposição

O sistema pode e deve apresentar informações sobre conflitos, sobreposições e possíveis ajustes. No entanto, estas informações são sempre apresentadas como sugestões que o usuário pode aceitar ou rejeitar, nunca como ações automáticas.

### Princípio 3: Rotina como Ideal

A rotina definida pelo usuário representa o cenário ideal de execução dos hábitos. Ajustes pontuais em instâncias específicas são adaptações necessárias devido a imprevistos do dia a dia, mas o objetivo permanente é retornar ao plano ideal da rotina.

## Regras de Negócio

### RN-EVENT-001: Detecção de Conflitos Temporais

**Descrição:** O sistema detecta quando dois ou mais eventos se sobrepõem no tempo, independentemente do tipo de evento.

**Condição de Conflito:** Dois eventos A e B estão em conflito se há sobreposição entre seus intervalos temporais. Formalmente, existe conflito quando:

```terminal
(A.scheduled_start < B.scheduled_end) E (B.scheduled_start < A.scheduled_end)
```

**Tipos de Eventos Monitorados:**

- HabitInstances (instâncias de hábitos geradas a partir de routines)
- Tasks (tarefas únicas com horário definido)
- Events (eventos genéricos do calendário)

**Comportamento:** O sistema apenas identifica e registra o conflito. Nenhuma ação automática é tomada para resolver o conflito. A detecção ocorre em tempo real sempre que um evento é criado, atualizado ou ajustado.

**Implementação Esperada:**
O método `EventReorderingService.detect_conflicts()` retorna uma lista de conflitos detectados. Cada conflito contém informações sobre os eventos envolvidos, seus horários e o tipo de sobreposição. Este método não modifica nenhum dado no banco, apenas realiza consultas e retorna informações.

### RN-EVENT-002: Apresentação de Conflitos

**Descrição:** Quando conflitos são detectados, o sistema apresenta estas informações ao usuário de forma clara e estruturada.

**Quando Apresentar:** A apresentação de conflitos ocorre nos seguintes momentos:

1. Após o usuário criar ou ajustar um evento que resulta em conflito
2. Quando o usuário solicita explicitamente visualização de conflitos (comando específico)
3. Antes de iniciar timer para um habit ou marcar uma task como complete, se houver conflitos no período

**Formato de Apresentação:** A informação deve incluir:

- Lista de todos os eventos conflitantes
- Horários de cada evento
- Tipo de cada evento (HabitInstance, Task ou Event)
- Duração da sobreposição temporal

**Comportamento:** Após apresentar os conflitos, o sistema aguarda instrução do usuário. Não há sugestões automáticas de reordenamento neste momento. O usuário decide como proceder baseado nas informações apresentadas.

### RN-EVENT-003: Resolução de Conflitos Controlada pelo Usuário

**Descrição:** A resolução de conflitos é sempre iniciada e controlada pelo usuário. O sistema pode apresentar opções, mas nunca aplica mudanças sem confirmação explícita.

**Fluxo de Resolução:**

Primeiro, o usuário visualiza os conflitos conforme RN-EVENT-002. Em seguida, o usuário pode escolher entre diversas ações. Ele pode ajustar manualmente o horário de um dos eventos através dos comandos específicos de cada tipo de evento. Alternativamente, pode marcar um dos eventos como skip, indicando que não será executado naquele dia. Outra opção é executar um dos eventos fora do horário ideal e registrar via timer ou complete. Por fim, o usuário pode simplesmente manter os conflitos e decidir no momento da execução qual evento terá prioridade.

**Importante:** O sistema nunca deve apresentar um conflito e automaticamente aplicar uma resolução sem que o usuário tenha explicitamente confirmado a ação desejada. Mesmo operações aparentemente óbvias requerem confirmação do usuário.

### RN-EVENT-004: Sugestões de Reordenamento (Futuro)

**Descrição:** Esta regra está planejada para versão futura e atualmente não deve ser implementada.

**Comportamento Futuro Planejado:** Em versões futuras, quando o usuário solicitar explicitamente, o sistema poderá sugerir possíveis reordenamentos que eliminam conflitos. Estas sugestões serão baseadas em análise de padrões históricos do usuário, prioridades definidas e disponibilidade de horários alternativos.

**Estado Atual:** Por enquanto, o sistema apenas detecta e apresenta conflitos conforme RN-EVENT-001 e RN-EVENT-002. Não há lógica de sugestão de reordenamento implementada. Qualquer código que implemente sugestões automáticas deve ser removido ou desabilitado.

### RN-EVENT-005: Escopo Temporal de Detecção

**Descrição:** O sistema detecta conflitos dentro do escopo de um dia completo, do início da madrugada (00:00) até o fim do dia (23:59).

**Justificativa:** Eventos de dias diferentes não podem conflitar temporalmente mesmo que horários se sobreponham numericamente, pois ocorrem em momentos distintos do calendário.

**Comportamento:** Ao detectar conflitos para um evento específico, o sistema busca todos os outros eventos do mesmo dia e verifica sobreposições temporais apenas dentro deste escopo diário.

### RN-EVENT-006: Persistência de Conflitos

**Descrição:** Conflitos não são persistidos no banco de dados como entidades separadas. São calculados dinamicamente sempre que necessário.

**Justificativa:** Como conflitos são resultado da relação temporal entre eventos, e eventos podem ser ajustados a qualquer momento, não faz sentido armazenar conflitos como dados persistentes. Cada operação que precisa conhecer conflitos deve calculá-los em tempo real.

**Implementação:** O EventReorderingService calcula conflitos sob demanda através de queries que buscam eventos do mesmo dia e verificam sobreposições temporais.

### RN-EVENT-007: Interação com Timer e Complete

**Descrição:** Quando o usuário inicia um timer para um habit ou marca uma task como complete, e existem conflitos no horário atual, o sistema apresenta os conflitos mas não impede a ação.

**Comportamento Esperado:**

O usuário executa o comando para iniciar timer ou marcar como complete. O sistema detecta se há outros eventos no mesmo horário. Se há conflitos, o sistema apresenta uma lista dos eventos conflitantes e pergunta ao usuário se deseja prosseguir mesmo assim. O usuário confirma explicitamente que deseja prosseguir. O sistema então registra a execução normalmente.

**Importante:** O sistema nunca deve bloquear a execução de um evento devido a conflitos. Conflitos são informativos, não impeditivos. O usuário sempre pode escolher executar um evento mesmo que conflite com outros.

## Exemplos de Uso

### Exemplo 1: Detecção Simples de Conflito

Cenário: O usuário tem dois eventos no mesmo horário.

```terminal
Evento A: Academia - 07:00 às 08:00
Evento B: Reunião - 07:30 às 08:30
```

Comportamento do Sistema:
O sistema detecta que há sobreposição entre 07:30 e 08:00. Ao criar ou visualizar qualquer um destes eventos, o sistema apresenta: "Conflito detectado entre Academia (07:00-08:00) e Reunião (07:30-08:30). Sobreposição de 30 minutos."

O sistema então aguarda. Não propõe ajustes, não move eventos, não sugere novos horários. Apenas informa o conflito e permite que o usuário decida como proceder.

### Exemplo 2: Múltiplos Conflitos

Cenário: O usuário tem três eventos sobrepostos.

```terminal
Evento A: Estudar - 14:00 às 16:00
Evento B: Ligação - 15:00 às 15:30
Evento C: Projeto - 15:15 às 17:00
```

Comportamento do Sistema:
O sistema detecta múltiplos conflitos. A apresenta: "Três eventos em conflito no período 14:00-17:00. Sobreposições detectadas. Evento A vs B (30 min). Evento A vs C (1 hora). Evento B vs C (15 min)."

O usuário visualiza as informações e decide sua estratégia. Talvez escolha fazer a ligação no horário planejado e ajustar os outros. Talvez decida focar apenas no projeto e dar skip nos demais. O sistema não opina sobre qual escolha é melhor, apenas apresenta os fatos.

### Exemplo 3: Início de Timer com Conflito

Cenário: Usuário quer iniciar timer para Academia às 07:00, mas há Reunião também às 07:00.

```terminal
$ timeblock timer start --habit-instance 42

Conflito detectado:
  - Academia: 07:00-08:00 (você está iniciando agora)
  - Reunião: 07:00-08:30 (também agendada)

Iniciar timer mesmo assim? [Y/n]
```

Se o usuário responder Y, o timer inicia normalmente. Se responder n, o comando é cancelado. O sistema não tenta resolver o conflito automaticamente, não sugere novo horário, não move a reunião. Apenas informa e pergunta.

## Implementação

### Estrutura de Código

O EventReorderingService deve ter a seguinte estrutura minimalista:

```python
class EventReorderingService:
    """Serviço para detecção de conflitos temporais."""

    @staticmethod
    def detect_conflicts(
        triggered_event_id: int,
        event_type: str,
    ) -> list[Conflict]:
        """
        Detecta conflitos com outros eventos.

        Retorna lista de conflitos detectados baseado em sobreposição
        temporal. Não modifica nenhum dado, apenas consulta e retorna
        informações.
        """
        pass

    @staticmethod
    def get_conflicts_for_day(date: date) -> list[Conflict]:
        """
        Retorna todos os conflitos detectados em um dia específico.

        Útil para visualização geral da agenda do dia.
        """
        pass
```

Qualquer método que implemente lógica de priorização automática, cálculo de novos horários ou aplicação de mudanças deve ser removido ou movido para um serviço futuro separado.

### Testes

Os testes para EventReorderingService devem validar:

1. Detecção correta de sobreposições temporais
2. Identificação de todos os eventos conflitantes em um dia
3. Não modificação de dados durante detecção
4. Retorno de lista vazia quando não há conflitos
5. Tratamento correto de eventos adjacentes (que não se sobrepõem)

Os testes não devem validar:

- Reordenamento automático de eventos
- Cálculo de prioridades
- Aplicação de mudanças sem confirmação do usuário
- Sugestões de novos horários

## Conclusão

O Event Reordering System do TimeBlock é fundamentalmente um sistema de informação e detecção, não de decisão automática. Esta abordagem respeita a autonomia do usuário e reconhece que apenas o usuário possui o contexto completo necessário para tomar decisões sobre sua agenda.

O sistema deve sempre priorizar clareza na apresentação de informações e facilidade para o usuário executar as ações que decidir, mas nunca deve presumir conhecer a melhor solução para conflitos de agenda do usuário.

---

**Próxima Revisão:** Após implementação da versão 2.0
