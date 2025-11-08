# Regras de Negócio: Habit Instances

- **Versão:** 1.0
- **Data:** 06 de Novembro de 2025
- **Status:** Especificação Formal

---

## Visão Geral

HabitInstances representam as ocorrências concretas de hábitos ao longo do tempo. Enquanto um Habit dentro de uma Routine define o plano ideal, as HabitInstances são as execuções reais que acontecem dia após dia. Este documento especifica como instâncias são geradas, ajustadas e rastreadas.

## Conceitos Fundamentais

### Routine: O Plano Ideal

Uma Routine contém Habits que definem o cenário ideal de execução. Quando o usuário cria uma rotina matinal com "Meditar às 6h por 20 minutos", ele está declarando sua intenção e objetivo. Esta é a referência contra a qual o progresso será medido.

### HabitInstance: A Realidade do Dia a Dia

Uma HabitInstance é uma ocorrência específica de um hábito em uma data particular. Se "Meditar" está planejado para segunda-feira dia 4 de novembro, existe uma HabitInstance representando especificamente essa execução. Esta instância pode ser cumprida no horário ideal, cumprida em outro horário, ou não cumprida.

### A Relação Entre Ideal e Real

O objetivo do TimeBlock é ajudar o usuário a aproximar a realidade do ideal. Os Habits na Routine representam o objetivo, as HabitInstances representam a jornada para alcançá-lo. Ajustes pontuais em instâncias são necessários e esperados, mas o norte permanece sendo retornar ao plano ideal sempre que possível.

## Regras de Negócio

### RN-HABIT-001: Criação de Habits em Routines

**Descrição:** O usuário cria Habits dentro de Routines especificando explicitamente dias da semana e horários para cada hábito.

**Informações Obrigatórias:**

- Título do hábito (ex: "Academia", "Meditar", "Estudar Inglês")
- Dias da semana em que o hábito deve ocorrer (ex: segunda, quarta, sexta)
- Horário de início (ex: 07:00)
- Duração em minutos (ex: 60)

**Exemplos de Definição:**

Um usuário pode criar hábito "Academia" que ocorre segundas, quartas e sextas às 7h com duração de 60 minutos. Outro exemplo seria "Inglês" que ocorre terças e quintas às 19h com duração de 45 minutos. Um terceiro caso seria "Meditar" que ocorre todos os dias da semana às 6h com duração de 20 minutos.

**Comportamento:** Após a criação do Habit na Routine, o sistema está pronto para gerar instâncias, mas não gera automaticamente até que o usuário execute o comando de geração ou especifique período durante a criação.

### RN-HABIT-002: Geração de Instâncias

**Descrição:** Após criar um Habit em uma Routine, o sistema gera HabitInstances baseado em um período especificado pelo usuário.

**Períodos Disponíveis:**

- Semanal: gera instâncias apenas para a próxima semana (7 dias)
- Mensal: gera instâncias para o próximo mês (aproximadamente 30 dias)
- Trimestral: gera instâncias para os próximos 3 meses (padrão)
- Semestral: gera instâncias para os próximos 6 meses
- Anual: gera instâncias para o próximo ano
- Dias específicos: gera instâncias apenas para dias da semana selecionados no período escolhido
- Finais de semana: gera instâncias apenas para sábados e domingos no período escolhido

**Comportamento Padrão:** Se o usuário não especificar período, o sistema gera instâncias para os próximos 3 meses (trimestral).

**Cálculo de Instâncias:** Para um hábito que ocorre 3 vezes por semana durante 3 meses, o cálculo seria aproximadamente 3 instâncias por semana multiplicado por 12 semanas, resultando em 36 instâncias. O sistema distribui estas instâncias nos dias da semana especificados pelo usuário ao criar o Habit.

**Exemplo Concreto:**

Um usuário cria hábito "Academia" para segundas, quartas e sextas às 7h. Ao gerar instâncias com período trimestral, o sistema cria uma HabitInstance para cada segunda-feira, quarta-feira e sexta-feira nos próximos 3 meses. Se hoje é 6 de novembro de 2025, o sistema gera instâncias até aproximadamente 6 de fevereiro de 2026, totalizando cerca de 36 instâncias.

**Importante:** A geração respeita exatamente os dias da semana definidos pelo usuário. Se o usuário especificou apenas segunda, quarta e sexta, instâncias não serão criadas para terça, quinta, sábado ou domingo, independentemente do período escolhido.

### RN-HABIT-003: Identificação de Instâncias

**Descrição:** Cada HabitInstance possui um identificador único (ID) que permite operações específicas sobre aquela ocorrência particular do hábito.

**Uso do ID:** O ID da instância é usado para ajustar horários, marcar como complete, iniciar timer, ou dar skip naquela execução específica. Comandos que operam sobre instâncias sempre requerem o ID para garantir que apenas a instância desejada seja afetada.

**Diferenciação:** Múltiplas instâncias do mesmo hábito em dias diferentes possuem IDs diferentes. Por exemplo, "Academia" de segunda-feira dia 4 tem ID 42, enquanto "Academia" de quarta-feira dia 6 tem ID 43. Isto permite que o usuário ajuste cada dia independentemente.

### RN-HABIT-004: Ajuste de Horário de Instância

**Descrição:** O usuário pode ajustar o horário de uma HabitInstance específica através de seu ID. Este ajuste afeta apenas aquela instância, não o Habit na Routine nem outras instâncias futuras.

**Comportamento Padrão:**

Quando o usuário ajusta uma instância através do comando de ajuste especificando o ID, o novo horário é aplicado apenas àquela instância específica. Todas as outras instâncias do mesmo hábito mantêm o horário ideal definido na Routine. Na próxima ocorrência do hábito, o sistema gera ou utiliza a instância com o horário ideal, não o horário ajustado.

**Detecção de Ajuste:**

Para identificar se uma instância foi ajustada, basta comparar seus horários com os horários ideais do Habit na Routine. Se os horários diferem, a instância foi ajustada. Esta verificação é feita dinamicamente quando necessário, sem necessidade de campo adicional no modelo.

```python
def is_adjusted(instance: HabitInstance) -> bool:
    """Verifica se instância tem horário diferente do ideal."""
    return (
        instance.scheduled_start != instance.habit.scheduled_start or
        instance.scheduled_end != instance.habit.scheduled_end
    )
```

**Justificativa:** Ajustes pontuais são necessários devido a imprevistos do dia a dia, como reuniões inesperadas, compromissos médicos ou mudanças na rotina diária. No entanto, estes ajustes não devem alterar o plano ideal que o usuário estabeleceu na Routine. Cada dia é uma nova tentativa de seguir o plano ideal.

**Exemplo:**

O usuário tem "Academia" planejada para 7h todas as segundas, quartas e sextas. Na segunda-feira dia 4, surge uma reunião urgente às 7h. O usuário executa o comando ajustando a instância daquele dia específico para 18h. Na quarta-feira dia 6, o sistema apresenta "Academia" às 7h novamente, pois este é o horário ideal da Routine e o ajuste de segunda-feira foi pontual apenas para aquele dia.

**Mudanças Permanentes:** Se o usuário percebe que o horário ideal precisa ser alterado permanentemente, ele deve editar o Habit na Routine, não as instâncias individuais. Esta separação clara mantém a Routine como fonte de verdade do plano ideal.

### RN-HABIT-005: Tracking de Execução

**Descrição:** O sistema registra quando e como cada HabitInstance foi executada, independentemente do horário em que a execução ocorreu.

**Formas de Execução:**

Um hábito pode ser executado através de timer tracking. Neste caso, o usuário inicia um timer para a instância específica, o sistema registra o horário de início, a duração da execução e marca a instância como completa quando o timer é parado. Alternativamente, o usuário pode marcar diretamente como complete sem usar timer, simplesmente indicando que o hábito foi cumprido naquele dia. Por fim, o usuário pode marcar como skip, indicando que conscientemente decidiu não executar o hábito naquele dia específico.

**Execução Fora do Horário Ideal:**

O sistema registra a execução independentemente do horário. Se "Academia" está planejada para 7h mas o usuário só consegue executar às 18h, ao iniciar o timer às 18h, o sistema registra normalmente. A instância é marcada como completa, pois o hábito foi cumprido, mesmo que fora do horário ideal.

**Métricas de Tracking:**

O sistema rastreia duas dimensões distintas. A primeira é consistência, que mede se o hábito foi executado ou não, independentemente do horário. A segunda é pontualidade, que compara horário de execução com horário ideal. Esta distinção permite que o usuário observe dois aspectos do seu progresso: está mantendo o hábito consistentemente e está conseguindo executar no horário ideal planejado.

**Exemplo de Visualização:**

Para o hábito "Academia" na última semana, o usuário poderia ver que teve 100% de consistência (executou todos os dias planejados) mas apenas 66% de pontualidade (apenas 2 de 3 dias foram no horário ideal). Esta informação ajuda o usuário a entender seus padrões e ajustar expectativas ou rotinas conforme necessário.

### RN-HABIT-006: Skip vs Complete

**Descrição:** O sistema diferencia entre não executar um hábito (skip) e executá-lo fora do horário planejado (complete late).

**Skip:** Quando o usuário marca uma instância como skip, ele indica conscientemente que decidiu não executar o hábito naquele dia. Pode ser por escolha deliberada (dia de descanso planejado), por impossibilidade (doença, viagem) ou por priorização de outros compromissos. O skip é registrado no tracking e impacta a métrica de consistência.

**Complete:** Quando o usuário executa o hábito, seja no horário ideal ou em outro horário, e registra via timer ou marcação direta, a instância é marcada como complete. Impacta positivamente a métrica de consistência. Se executado fora do horário ideal, impacta negativamente a métrica de pontualidade, mas ainda conta como dia cumprido.

**Ausência de Registro:** Se o usuário não registra nada sobre uma instância (nem skip, nem complete), o sistema considera como falha não intencional. Diferente do skip consciente, esta situação pode indicar esquecimento ou falta de engajamento, e é tratada diferentemente nas métricas e visualizações.

### RN-HABIT-007: Relação com Routine

**Descrição:** A Routine é a fonte de verdade para o plano ideal. HabitInstances referenciam o Habit na Routine mas não modificam este plano.

**Propagação de Mudanças:** Se o usuário edita o Habit na Routine alterando o horário ideal, esta mudança afeta apenas instâncias futuras ainda não ajustadas manualmente. Instâncias já ajustadas pelo usuário mantêm seus horários ajustados. Instâncias passadas mantêm os horários que tinham quando foram geradas, preservando o histórico.

**Exemplo:**

O usuário tem "Meditar" às 6h definido na Routine e 50 instâncias geradas para os próximos meses. Decide que 6h30 seria melhor e edita o Habit na Routine. Instâncias futuras que ainda não foram ajustadas individualmente passam a refletir 6h30. Instâncias de dias que já passaram mantêm 6h para preservar histórico. Instâncias futuras que o usuário já havia ajustado manualmente para outro horário (por exemplo, 7h em datas específicas por conflitos conhecidos) mantêm seus ajustes manuais.

**Deletar Habit:** Se o usuário deleta um Habit da Routine, todas as HabitInstances futuras daquele hábito são também deletadas. Instâncias passadas já executadas são mantidas para preservar histórico de tracking.

### RN-HABIT-008: Geração Adicional de Instâncias

**Descrição:** O usuário pode gerar instâncias adicionais a qualquer momento se perceber que as instâncias atuais estão terminando.

**Comportamento:** Se o usuário gerou inicialmente apenas 1 mês de instâncias e percebe que este período está chegando ao fim, pode executar novamente o comando de geração especificando um novo período. O sistema verifica quais instâncias já existem e gera apenas as novas, evitando duplicatas.

**Exemplo:**

Em 6 de novembro, o usuário gera instâncias para 1 mês (até 6 de dezembro). Em 25 de novembro, percebe que faltam poucas instâncias e decide gerar mais. Executa comando gerando instâncias para mais 2 meses. O sistema identifica que já existem instâncias até 6 de dezembro e gera apenas de 7 de dezembro até 7 de fevereiro, evitando criar instâncias duplicadas para dezembro.

## Implementação

### Modelo de Dados

```python
class HabitInstance(SQLModel, table=True):
    """Representa ocorrência específica de um hábito em uma data."""

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id")
    date: date  # Data específica desta ocorrência
    scheduled_start: time  # Horário planejado (pode diferir do ideal)
    scheduled_end: time
    status: str  # "planned", "in_progress", "completed", "skipped"

    # Relacionamentos
    habit: Habit = Relationship(back_populates="instances")
    timelogs: list[TimeLog] = Relationship(back_populates="habit_instance")
```

**Nota sobre Campos Removidos:** Os campos `user_override` e `manually_adjusted` foram removidos por serem redundantes. Para verificar se uma instância foi ajustada, basta comparar seus horários com os horários ideais do Habit na Routine. Esta verificação dinâmica é mais simples e não adiciona complexidade desnecessária ao modelo.

### Serviços

```python
class HabitInstanceService:
    """Gerencia operações sobre HabitInstances."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        period: str = "trimestral",
        start_date: date = None,
    ) -> list[HabitInstance]:
        """
        Gera instâncias para um hábito no período especificado.

        Verifica instâncias existentes e gera apenas as faltantes.
        Respeita dias da semana definidos no Habit.
        """
        pass

    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time,
        new_end: time,
    ) -> HabitInstance:
        """
        Ajusta horário de uma instância específica.

        Retorna a instância atualizada.
        Não afeta outras instâncias do mesmo hábito.
        Para verificar se foi ajustada, compare com horário ideal do Habit.
        """
        pass

    @staticmethod
    def mark_complete(instance_id: int) -> HabitInstance:
        """Marca instância como completa sem timer."""
        pass

    @staticmethod
    def mark_skip(instance_id: int, reason: str = None) -> HabitInstance:
        """Marca instância como skip com razão opcional."""
        pass

    @staticmethod
    def is_adjusted(instance: HabitInstance) -> bool:
        """
        Verifica se instância tem horário diferente do ideal.

        Compara horários da instância com horários do Habit na Routine.
        """
        return (
            instance.scheduled_start != instance.habit.scheduled_start or
            instance.scheduled_end != instance.habit.scheduled_end
        )
```

### Comandos CLI

```bash
# Criar hábito e gerar instâncias
timeblock habit create "Academia" \
  --routine 1 \
  --days monday,wednesday,friday \
  --start 07:00 \
  --duration 60 \
  --period trimestral

# Ajustar instância específica
timeblock habit adjust 42 --start 18:00

# Marcar como completa
timeblock habit complete 42

# Marcar como skip
timeblock habit skip 42 --reason "viagem"

# Gerar instâncias adicionais
timeblock habit generate 1 --period mensal
```

## Testes

Os testes para HabitInstances devem validar:

**Geração:**

- Instâncias são criadas apenas nos dias especificados
- Quantidade correta baseada em período escolhido
- Não gera duplicatas ao executar comando múltiplas vezes
- Respeita data de início se especificada

**Ajuste:**

- Apenas instância especificada é modificada
- Outras instâncias do mesmo hábito não são afetadas
- Horário ideal na Routine permanece inalterado
- Verificação dinâmica de ajuste funciona corretamente

**Tracking:**

- Complete registra execução corretamente
- Skip registra com status apropriado
- Timer integration funciona independente do horário
- Métricas de consistência e pontualidade calculadas corretamente

**Relação com Routine:**

- Mudanças na Routine afetam apenas instâncias futuras não ajustadas
- Deleção de Habit remove instâncias futuras mas preserva passadas
- Instâncias referenciam Habit corretamente
- Comparação com horário ideal identifica ajustes

## Conclusão

HabitInstances são a ponte entre o plano ideal (Routine) e a realidade da execução. Ao separar claramente estes conceitos e permitir ajustes pontuais sem alterar o plano de referência, o TimeBlock ajuda o usuário a manter o foco no objetivo de longo prazo enquanto adapta-se às necessidades do dia a dia.

O sistema deve sempre facilitar o retorno ao plano ideal, mas reconhecer que a vida real requer flexibilidade. Esta filosofia guia todas as decisões de implementação relacionadas a HabitInstances.

---

**Próxima Revisão:** Após implementação da versão 2.0
