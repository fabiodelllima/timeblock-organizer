# Regras de Negócio: Tasks

- **Versão:** 1.0
- **Data:** 06 de Novembro de 2025
- **Status:** Especificação Formal

---

## Visão Geral

Tasks representam atividades únicas e pontuais que possuem um horário específico mas não são parte de uma rotina recorrente. Diferentemente de hábitos que se repetem seguindo padrões, tasks são eventos isolados que precisam ser concluídos uma única vez.

## Conceitos Fundamentais

### Task vs Habit

Uma Task é fundamentalmente diferente de um Habit em termos de recorrência e objetivo. Um Habit visa construir comportamento consistente ao longo do tempo através de repetição regular. Exemplos incluem meditar diariamente, ir à academia três vezes por semana ou estudar inglês todas as terças e quintas. Em contraste, uma Task é uma atividade pontual com começo e fim definidos. Exemplos incluem enviar relatório até sexta-feira, preparar apresentação para reunião de segunda ou comprar presente de aniversário.

### Simplicidade Intencional

Nesta versão do TimeBlock, Tasks mantêm propositalmente uma implementação simples. O foco está em criar, visualizar e marcar como completas. Funcionalidades avançadas como timer tracking, subtarefas, dependências entre tasks ou tracking detalhado de tempo são intencionalmente deixadas de fora para manter a complexidade gerenciável e o sistema focado em seu objetivo principal de organização de rotinas e hábitos.

## Regras de Negócio

### BR-TASK-001: Criação de Tasks

**Descrição:** O usuário cria uma Task especificando informações básicas sobre a atividade a ser realizada.

**Informações Obrigatórias:**

- Título da task (ex: "Enviar relatório", "Preparar apresentação")
- Data e horário planejado para execução

**Informações Opcionais:**

- Descrição detalhada da task
- Tag para categorização
- Deadline se diferente do horário planejado

**Comportamento:** Ao criar uma Task, o sistema registra todas as informações e a task fica visível na agenda do usuário para o dia e horário especificados. A task é criada com status "planned" por padrão.

**Exemplo:**

Um usuário precisa enviar um relatório até sexta-feira às 17h. Cria uma Task com título "Enviar relatório Q4", data sexta-feira 8 de novembro, horário 16h (uma hora antes do deadline para ter margem). Opcionalmente adiciona descrição "Compilar dados de vendas e enviar para gerência" e tag "trabalho".

### BR-TASK-002: Agendamento Temporal

**Descrição:** Tasks possuem um horário planejado de execução que é usado para organização temporal na agenda e detecção de conflitos.

**Horário Planejado vs Deadline:**

O horário planejado (scheduled_datetime) representa quando o usuário pretende trabalhar na task. O deadline representa até quando a task precisa estar completa. Estes podem ser diferentes. Por exemplo, uma task pode ter horário planejado às 14h de segunda-feira mas deadline até final de quarta-feira.

**Uso na Agenda:**

O horário planejado determina onde a task aparece na visualização da agenda do usuário. Se o usuário visualiza compromissos do dia, a task aparece no horário planejado, permitindo que o usuário veja todos seus compromissos temporais incluindo hábitos, tasks e eventos em uma única linha do tempo.

**Detecção de Conflitos:**

Tasks participam da detecção de conflitos temporais junto com HabitInstances e Events. Se uma task está planejada para 14h às 15h e há um hábito também planejado para 14h30, o sistema detecta e apresenta o conflito ao usuário conforme regras definidas no documento de Event Reordering.

### BR-TASK-003: Marcação como Completa

**Descrição:** O usuário marca uma Task como completa quando termina de executá-la. Esta é a forma principal de interação com tasks nesta versão do sistema.

**Comportamento:**

Quando o usuário executa o comando para marcar uma task como completa, o sistema atualiza o status da task para "completed" e registra o timestamp da conclusão. A task deixa de aparecer na lista de tasks pendentes e passa a aparecer em visualizações de histórico e relatórios de produtividade.

**Timing de Conclusão:**

A marcação como completa pode acontecer a qualquer momento. O usuário não precisa executar a task exatamente no horário planejado. Se a task estava planejada para 14h mas o usuário só consegue executar às 18h, ao terminar marca como completa e o sistema registra normalmente. O horário de conclusão é registrado mas não há validação contra o horário planejado.

**Exemplo de Comando:**

```bash
# Listar tasks pendentes para identificar ID
timeblock task list --status planned

# Marcar task específica como completa
timeblock task complete 42
```

### BR-TASK-004: Status de Tasks

**Descrição:** Tasks possuem status que indica seu estado atual no ciclo de vida.

**Status Disponíveis:**

O status "planned" indica que a task foi criada mas ainda não foi executada. Este é o estado inicial de toda task recém-criada. O status "in_progress" é reservado para uso futuro quando timer tracking for implementado. Nesta versão, tasks não transitam por este status. O status "completed" indica que a task foi marcada como concluída pelo usuário. O status "cancelled" permite que o usuário cancele uma task que não será mais necessária, diferenciando de conclusão normal.

**Transições de Status:**

Tasks normalmente transitam diretamente de "planned" para "completed" quando o usuário marca como concluída. Alternativamente, podem transitar de "planned" para "cancelled" se o usuário decidir que a task não é mais necessária ou relevante.

### BR-TASK-005: Visualização e Listagem

**Descrição:** O usuário pode visualizar tasks através de diferentes filtros e agrupamentos.

**Filtros Disponíveis:**

- Por status (planned, completed, cancelled)
- Por data (tasks de um dia específico, semana ou mês)
- Por tag (se tags foram atribuídas)
- Sem filtro para ver todas as tasks

**Ordenação:**

Tasks são ordenadas por horário planejado por padrão. Tasks do mesmo dia aparecem em ordem cronológica. Tasks sem horário definido aparecem no final da lista.

**Exemplo de Comandos:**

```bash
# Listar todas tasks pendentes
timeblock task list --status planned

# Listar tasks de hoje
timeblock task list --today

# Listar tasks da semana
timeblock task list --week

# Listar todas tasks incluindo completas
timeblock task list --all
```

### BR-TASK-006: Atualização de Tasks

**Descrição:** O usuário pode atualizar informações de uma Task enquanto ela ainda está pendente. Diferentemente de HabitInstances, uma Task pode ter seu horário ajustado múltiplas vezes antes de ser concluída.

**Campos Atualizáveis:**

- Título
- Descrição
- Horário planejado
- Data planejada
- Tag
- Deadline

**Comportamento de Atualização:**

Quando o usuário atualiza uma task, especialmente se altera horário ou data, o sistema detecta potenciais conflitos com outros eventos conforme regras de Event Reordering. Se conflitos são detectados, o sistema apresenta as informações ao usuário mas não impede a atualização. O usuário decide como proceder.

**Restrições:**

Tasks já marcadas como completed ou cancelled não podem ser editadas. Esta restrição preserva a integridade do histórico. Se o usuário precisa reativar uma task, deve criar uma nova task com as informações desejadas.

### BR-TASK-007: Cancelamento de Tasks

**Descrição:** O usuário pode cancelar uma Task que não será mais executada.

**Diferença entre Cancelar e Deletar:**

Cancelar uma task (status "cancelled") mantém o registro no sistema mas marca como não executada intencionalmente. Isto é útil para tracking e análise posterior de quantas tasks foram criadas versus quantas foram realmente necessárias. Deletar uma task remove completamente o registro do sistema, como se nunca tivesse existido.

**Quando Cancelar:**

Tasks devem ser canceladas quando deixam de ser necessárias ou relevantes. Exemplos incluem tasks que se tornaram obsoletas devido a mudanças de prioridade, tasks duplicadas que foram criadas por engano ou tasks que foram absorvidas por outras atividades.

**Quando Deletar:**

Deletar deve ser usado apenas para tasks criadas por engano absoluto e que nunca tiveram qualquer validade. Por exemplo, uma task criada no dia errado ou com informações completamente incorretas que não têm valor para histórico.

### BR-TASK-008: Relação com Agenda

**Descrição:** Tasks integram-se à visualização geral da agenda do usuário junto com HabitInstances e Events.

**Visualização Unificada:**

Quando o usuário visualiza sua agenda para um dia específico, deve ver todos os compromissos temporais em ordem cronológica. Isto inclui instâncias de hábitos da rotina, tasks criadas manualmente e eventos genéricos do calendário. Esta visualização unificada permite que o usuário tenha uma visão completa de suas responsabilidades temporais.

**Exemplo de Visualização:**

Para segunda-feira 4 de novembro, a agenda pode mostrar seis horas da manhã com meditação vinte minutos, sete horas com academia sessenta minutos, nove horas com reunião de equipe noventa minutos, onze horas com task enviar relatório sessenta minutos, quatorze horas com estudar inglês quarenta e cinco minutos, dezoito horas com jantar em família.

### BR-TASK-009: Simplicidade Mantida

**Descrição:** Esta regra documenta explicitamente funcionalidades que NÃO estão implementadas nesta versão.

**Funcionalidades Ausentes Intencionalmente:**

Timer tracking para tasks não está implementado. Tasks não podem ter um timer iniciado e parado para medir tempo de execução. A marcação é binária: não completa ou completa. Subtarefas ou decomposição hierárquica não existe. Cada task é atômica. Dependências entre tasks não são modeladas. Uma task não pode estar bloqueada aguardando conclusão de outra. Priorização explícita não está implementada. Todas as tasks têm igual importância do ponto de vista do sistema. Checklist ou items dentro de uma task não existem. O título e descrição capturam todo o conteúdo.

**Justificativa:**

Esta simplicidade é intencional. O foco do TimeBlock está em hábitos e rotinas. Tasks são um complemento para capturar atividades pontuais, mas não são o core da aplicação. Manter tasks simples reduz complexidade do código, facilita manutenção e mantém o usuário focado no que realmente importa: construir hábitos consistentes.

**Futuro:**

Se houver demanda validada por uso real, funcionalidades mais avançadas para tasks podem ser consideradas em versões futuras. No entanto, qualquer adição deve ser avaliada cuidadosamente para não desviar o foco principal da aplicação.

## Implementação

### Modelo de Dados

```python
class Task(SQLModel, table=True):
    """Representa uma atividade pontual com horário específico."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str | None = None
    scheduled_datetime: datetime  # Quando usuário planeja executar
    deadline: datetime | None = None  # Quando precisa estar completo
    status: str = Field(default="planned")  # planned, completed, cancelled
    completed_at: datetime | None = None
    tag_id: int | None = Field(default=None, foreign_key="tag.id")

    # Relacionamentos
    tag: Optional[Tag] = Relationship(back_populates="tasks")
```

**Nota sobre Timer:** O modelo não possui campos relacionados a timer tracking como `started_at` ou relação com `TimeLog`. Esta ausência é intencional conforme BR-TASK-009.

### Serviços

```python
class TaskService:
    """Gerencia operações sobre Tasks."""

    @staticmethod
    def create(
        title: str,
        scheduled_datetime: datetime,
        description: str = None,
        deadline: datetime = None,
        tag_id: int = None,
    ) -> Task:
        """Cria uma nova task."""
        pass

    @staticmethod
    def update(
        task_id: int,
        title: str = None,
        scheduled_datetime: datetime = None,
        description: str = None,
        deadline: datetime = None,
        tag_id: int = None,
    ) -> Task:
        """
        Atualiza task existente.

        Se scheduled_datetime for alterado, detecta conflitos e
        retorna informações para o usuário, mas não bloqueia a atualização.
        Tasks podem ter horário ajustado múltiplas vezes.
        """
        pass

    @staticmethod
    def mark_complete(task_id: int) -> Task:
        """
        Marca task como completa.

        Atualiza status para 'completed' e registra timestamp.
        """
        pass

    @staticmethod
    def cancel(task_id: int) -> Task:
        """Marca task como cancelada."""
        pass

    @staticmethod
    def list_tasks(
        status: str = None,
        date: date = None,
        tag_id: int = None,
    ) -> list[Task]:
        """Lista tasks com filtros opcionais."""
        pass
```

### Comandos CLI

```bash
# Criar task
timeblock task create "Enviar relatório" \
  --datetime "2025-11-08 16:00" \
  --description "Compilar dados Q4" \
  --deadline "2025-11-08 17:00" \
  --tag trabalho

# Listar tasks
timeblock task list                    # Todas pendentes
timeblock task list --today            # Apenas de hoje
timeblock task list --status completed # Apenas completas
timeblock task list --tag trabalho     # Apenas com tag específica

# Atualizar task (pode ser feito múltiplas vezes)
timeblock task update 42 \
  --datetime "2025-11-08 18:00" \
  --title "Enviar relatório revisado"

# Marcar como completa
timeblock task complete 42

# Cancelar task
timeblock task cancel 42

# Deletar task (uso raro)
timeblock task delete 42 --confirm
```

## Testes

Os testes para Tasks devem validar:

**Criação:**

- Task é criada com informações corretas
- Status inicial é "planned"
- Campos opcionais funcionam corretamente
- Validações de campos obrigatórios

**Atualização:**

- Apenas task "planned" pode ser editada
- Tasks completed ou cancelled não são editáveis
- Atualização de horário detecta conflitos mas não bloqueia
- Task pode ser atualizada múltiplas vezes

**Conclusão:**

- Status muda para "completed"
- Timestamp de conclusão é registrado
- Task desaparece de listagens de pendentes

**Listagem:**

- Filtros funcionam corretamente
- Ordenação cronológica é respeitada
- Tasks aparecem na agenda do dia correto

**Cancelamento:**

- Status muda para "cancelled"
- Task mantém registro no histórico
- Diferenciação de delete total

**Integração:**

- Tasks participam de detecção de conflitos
- Tasks aparecem em visualização de agenda
- Relação com tags funciona corretamente

## Conclusão

Tasks no TimeBlock são intencionalmente simples e diretas. Servem como complemento para capturar atividades pontuais que não fazem parte da rotina regular de hábitos. Ao manter esta simplicidade, o sistema permanece focado em seu objetivo principal: ajudar o usuário a construir e manter hábitos consistentes.

A filosofia é clara: tasks são suporte, hábitos são protagonistas. Esta priorização guia todas as decisões de implementação e funcionalidades relacionadas a tasks.

---

**Próxima Revisão:** Após implementação da versão 2.0
