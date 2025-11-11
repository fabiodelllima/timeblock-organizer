# TimeBlock Architecture - User Control Philosophy

- **Versão:** 2.0
- **Data:** 06 de Novembro de 2025
- **Status:** Especificação Arquitetural

---

## Filosofia Fundamental: Controle Explícito do Usuário

Esta seção documenta um dos princípios arquiteturais mais importantes do TimeBlock: o usuário mantém controle explícito e consciente sobre todos os aspectos de sua agenda. Esta filosofia permeia todas as decisões de design e implementação do sistema.

### O Problema que Evitamos

Muitos sistemas de produtividade modernos tentam ser "inteligentes" tomando decisões automáticas em nome do usuário. Eles reordenam tarefas, ajustam prioridades, movem eventos e fazem sugestões baseadas em algoritmos que presumem entender o contexto completo da vida do usuário. Esta abordagem frequentemente resulta em frustração porque o sistema não possui nem pode possuir o contexto completo necessário para tomar boas decisões sobre a agenda de uma pessoa.

Um exemplo concreto ilustra o problema. Imagine que um sistema detecta que o usuário frequentemente executa "Academia" às 18h em vez das 7h planejadas. Um sistema "inteligente" poderia automaticamente mover todas as futuras instâncias de "Academia" para 18h, presumindo que aprendeu a preferência do usuário. No entanto, esta automação ignora contexto crucial: talvez o usuário esteja temporariamente ajustando devido a um projeto com deadline apertado, mas seu objetivo real continua sendo acordar cedo e ir à academia de manhã. Ao automatizar a mudança, o sistema reforça o comportamento não desejado e dificulta o retorno ao plano ideal.

### Nossa Solução: Informação sem Imposição

O TimeBlock adota uma filosofia radicalmente diferente. O sistema é construído sobre o princípio de que sua função é informar, sugerir e facilitar, mas nunca decidir. Cada alteração na agenda do usuário requer aprovação explícita. O usuário sempre sabe o que está acontecendo e por quê.

Esta abordagem manifesta-se concretamente em várias decisões arquiteturais. Quando o sistema detecta conflitos temporais entre eventos, ele apresenta informações claras sobre a sobreposição, mas não propõe automaticamente uma solução. Quando o usuário ajusta o horário de um hábito em um dia específico, este ajuste afeta apenas aquele dia, preservando o plano ideal para todos os outros dias. Quando múltiplos eventos competem pelo mesmo horário, o sistema não aplica regras de priorização automática, mas sim apresenta os eventos e permite que o usuário escolha conscientemente qual executar.

### A Rotina como Norte Verdadeiro

Um conceito central na arquitetura do TimeBlock é a distinção entre o plano ideal (Routine) e a realidade da execução (HabitInstances). A Routine representa as intenções e objetivos do usuário. É o que o usuário aspira fazer consistentemente. As HabitInstances representam o que realmente acontece dia após dia, incluindo todos os ajustes, atrasos e adaptações necessárias.

Esta separação arquitetural é fundamental porque preserva claramente o objetivo mesmo quando a realidade diverge temporariamente. O usuário pode ajustar instâncias individuais quantas vezes necessário para lidar com imprevistos do dia a dia, mas o plano ideal permanece intocado na Routine, sempre disponível como referência e sempre guiando a geração de novas instâncias.

O sistema é projetado para facilitar o retorno ao plano ideal. Cada dia é uma nova oportunidade de seguir a Routine. Ajustes de ontem não contaminam as possibilidades de hoje. Esta arquitetura encoraja consistência e perseverança sem punir a flexibilidade necessária para viver no mundo real.

### Implicações Arquiteturais

Esta filosofia tem consequências concretas e mensuráveis na arquitetura do sistema que devem ser respeitadas em todas as implementações.

#### Princípio 1: Detecção sem Ação

Serviços de detecção de problemas (como EventReorderingService) devem apenas identificar e reportar situações. Eles não devem modificar dados. A separação entre detecção e ação deve ser absoluta no código. Métodos de detecção retornam informações, métodos de ação requerem confirmação explícita do usuário e são invocados separadamente.

Exemplo de implementação correta:

```python
# Correto: Detecta e retorna informações
def detect_conflicts(event_id: int) -> list[Conflict]:
    conflicts = query_overlapping_events(event_id)
    return conflicts  # Apenas retorna, não modifica nada

# Correto: Ação separada que requer confirmação do usuário
def apply_user_resolution(conflict_id: int, user_choice: Resolution):
    if user_choice.confirmed:
        apply_changes(user_choice.changes)
```

Exemplo de implementação incorreta:

```python
# Incorreto: Detecção e ação misturadas
def detect_and_resolve_conflicts(event_id: int):
    conflicts = query_overlapping_events(event_id)
    # ERRO: Não deve fazer isto automaticamente
    auto_resolve(conflicts)
    return conflicts
```

#### Princípio 2: Granularidade de Controle

O usuário deve ter controle granular sobre cada elemento da sua agenda. Isto significa que operações devem sempre trabalhar com identificadores específicos (IDs de instâncias individuais, não apenas IDs de hábitos genéricos). Mudanças em uma instância não devem propagar automaticamente para outras instâncias sem confirmação explícita. O sistema deve sempre perguntar antes de aplicar mudanças em lote.

Esta granularidade manifesta-se no design das APIs. Métodos de serviço aceitam IDs específicos de instâncias. Comandos CLI requerem que o usuário especifique exatamente qual instância está ajustando. Prompts de confirmação deixam claro o escopo da mudança que será aplicada.

#### Princípio 3: Transparência de Operações

O usuário deve sempre entender o que o sistema está fazendo. Operações não devem ter efeitos colaterais ocultos. Mudanças devem ser explícitas e previsíveis. Logs e feedback devem claramente indicar o que foi modificado.

Esta transparência é implementada através de feedback rico nos comandos CLI. Quando o usuário ajusta uma instância, o sistema confirma exatamente o que foi alterado. Quando conflitos são detectados, o sistema apresenta informações completas sobre todos os eventos envolvidos. Quando uma ação é aplicada, o sistema lista explicitamente todas as mudanças que foram feitas.

#### Princípio 4: Facilidade de Reversão

Decisões do usuário devem ser facilmente reversíveis. O sistema não deve tornar difícil desfazer uma escolha. Histórico de mudanças deve ser mantido quando apropriado. Estados anteriores devem ser recuperáveis.

Esta reversibilidade é suportada por design de dados que preserva histórico. Soft deletes são preferidos sobre hard deletes quando apropriado. Ajustes manuais podem ser identificados comparando com o horário ideal da Routine. O usuário pode sempre voltar ao plano ideal regenerando instâncias ou editando ajustes manuais. Tasks e HabitInstances podem ter seus horários ajustados múltiplas vezes antes de serem concluídos.

### Casos de Uso Arquiteturais

Para ilustrar como estes princípios se manifestam concretamente, vamos examinar alguns casos de uso importantes e como a arquitetura os suporta.

#### Caso de Uso 1: Conflito de Horários

Situação: O usuário tem "Academia" planejada para 7h e uma "Reunião urgente" surge também às 7h.

Fluxo Arquitetural:

1. Sistema detecta sobreposição temporal ao criar a reunião
2. EventReorderingService.detect_conflicts() retorna lista com o conflito
3. CLI apresenta informação clara: "Conflito detectado entre Academia (7h) e Reunião (7h)"
4. Sistema aguarda instrução do usuário
5. Usuário pode escolher: ajustar Academia para outro horário, marcar Academia como skip, ou manter ambos e decidir no momento
6. Qualquer que seja a escolha, usuário confirma explicitamente através de comando específico
7. Sistema executa apenas a ação confirmada, nada mais

Pontos Arquiteturais Importantes:

- Detecção e resolução são completamente separadas
- Nenhuma ação automática ocorre
- Múltiplas opções são apresentadas
- Usuário controla a resolução
- Confirmação explícita é requerida

#### Caso de Uso 2: Ajuste de Instância

Situação: Usuário precisa ajustar "Meditar" de 6h para 6h30 apenas na terça-feira.

Fluxo Arquitetural:

1. Usuário identifica ID da instância específica através de listagem
2. Executa comando: `timeblock habit adjust 42 --start 06:30`
3. HabitInstanceService.adjust_instance_time() modifica apenas instância 42
4. Habit na Routine permanece inalterado (continua marcando 6h como ideal)
5. Outras instâncias de "Meditar" não são afetadas
6. Na quarta-feira, "Meditar" aparece às 6h novamente (horário ideal da Routine)
7. Se necessário, o usuário pode ajustar a mesma instância novamente antes de executá-la

Pontos Arquiteturais Importantes:

- Operação usa ID específico, não genérico
- Apenas instância alvo é modificada
- Plano ideal (Routine) é preservado
- Verificação de ajuste é feita por comparação dinâmica
- Granularidade é respeitada
- Ajustes múltiplos são permitidos

#### Caso de Uso 3: Múltiplos Conflitos

Situação: Três eventos se sobrepõem no período 14h-17h.

Fluxo Arquitetural:

1. Sistema detecta três sobreposições distintas
2. EventReorderingService retorna lista completa de conflitos
3. CLI apresenta visualização estruturada de todos os eventos e sobreposições
4. Sistema não sugere ordem, não calcula prioridades, não propõe horários alternativos
5. Usuário visualiza e entende a situação completa
6. Usuário decide estratégia (pode executar apenas um, pode dividir tempo entre eles, pode mover alguns)
7. Usuário executa comandos específicos para implementar sua estratégia
8. Cada comando requer confirmação

Pontos Arquiteturais Importantes:

- Apresentação completa sem opinião
- Sem automação de priorização
- Sem sugestões não solicitadas
- Usuário desenvolve e executa estratégia
- Sistema facilita mas não decide

### Implementação em Código

A filosofia de controle do usuário deve ser evidente na estrutura do código. Aqui estão padrões específicos que devem ser seguidos.

#### Padrão 1: Separação de Concerns

Serviços devem ser claramente separados entre detecção, sugestão e ação. Nunca misture estas responsabilidades.

```python
# BOM: Serviços separados e focados
class ConflictDetectionService:
    """Apenas detecta conflitos, não resolve."""
    @staticmethod
    def detect_conflicts(event_id: int) -> list[Conflict]:
        pass

class UserResolutionService:
    """Aplica resoluções escolhidas pelo usuário."""
    @staticmethod
    def apply_resolution(resolution: UserResolution):
        if not resolution.user_confirmed:
            raise ValueError("Resolução requer confirmação do usuário")
        # Aplica apenas após confirmação
        pass
```

#### Padrão 2: Confirmação Explícita

Operações que modificam dados devem sempre verificar confirmação explícita do usuário.

```python
# BOM: Requer confirmação explícita
def adjust_instance(instance_id: int, new_time: time, confirmed: bool):
    if not confirmed:
        raise ValueError("Ajuste requer confirmação explícita")
    # Procede apenas se confirmado
    apply_adjustment(instance_id, new_time)

# RUIM: Confirmação implícita ou ausente
def adjust_instance(instance_id: int, new_time: time):
    # Aplica sem verificar confirmação
    apply_adjustment(instance_id, new_time)
```

#### Padrão 3: Retorno de Informações

Métodos de detecção retornam objetos de dados ricos que podem ser apresentados ao usuário, não instruções de ação.

```python
# BOM: Retorna informações estruturadas
def detect_conflicts(event_id: int) -> ConflictReport:
    conflicts = find_overlapping_events(event_id)
    return ConflictReport(
        conflicts=conflicts,
        affected_events=[...],
        time_overlaps=[...]
    )

# RUIM: Retorna ações ou comandos
def detect_conflicts(event_id: int) -> list[Action]:
    conflicts = find_overlapping_events(event_id)
    # ERRO: Não deve retornar ações automáticas
    return [MoveEvent(...), CancelEvent(...)]
```

### Testes da Filosofia

A aderência a esta filosofia deve ser validada através de testes específicos que garantem que o sistema não toma decisões automáticas.

```python
def test_conflict_detection_does_not_modify_data():
    """Verifica que detecção não modifica nenhum dado."""
    # Arrange
    event = create_test_event()
    original_state = get_all_events()

    # Act
    conflicts = EventReorderingService.detect_conflicts(event.id)

    # Assert
    current_state = get_all_events()
    assert original_state == current_state, "Detecção não deve modificar dados"

def test_adjustment_requires_explicit_confirmation():
    """Verifica que ajustes requerem confirmação."""
    instance = create_test_instance()

    # Sem confirmação deve falhar
    with pytest.raises(ValueError):
        HabitInstanceService.adjust_instance_time(
            instance.id,
            new_time=time(18, 0),
            confirmed=False
        )

def test_routine_unchanged_after_instance_adjustment():
    """Verifica que ajuste de instância não afeta Routine."""
    habit = create_test_habit(scheduled_start=time(7, 0))
    instance = create_test_instance(habit_id=habit.id)

    # Ajusta instância
    HabitInstanceService.adjust_instance_time(
        instance.id,
        new_time=time(18, 0),
        confirmed=True
    )

    # Verifica que Habit na Routine não mudou
    refreshed_habit = get_habit(habit.id)
    assert refreshed_habit.scheduled_start == time(7, 0)

def test_multiple_adjustments_allowed():
    """Verifica que instância pode ser ajustada múltiplas vezes."""
    instance = create_test_instance(scheduled_start=time(7, 0))

    # Primeiro ajuste
    HabitInstanceService.adjust_instance_time(
        instance.id,
        new_time=time(18, 0),
        confirmed=True
    )

    # Segundo ajuste
    HabitInstanceService.adjust_instance_time(
        instance.id,
        new_time=time(19, 0),
        confirmed=True
    )

    # Verifica que segundo ajuste foi aplicado
    refreshed = get_instance(instance.id)
    assert refreshed.scheduled_start == time(19, 0)
```

## Conclusão

A filosofia de controle explícito do usuário não é apenas um princípio de design, mas sim uma decisão arquitetural fundamental que permeia todo o sistema TimeBlock. Esta filosofia reconhece que organização pessoal é profundamente contextual e que apenas o usuário possui o contexto completo necessário para tomar boas decisões sobre sua própria agenda.

Ao manter esta filosofia consistentemente em todas as camadas do sistema, desde modelos de dados até interface de usuário, criamos um sistema que empodera ao invés de presumir, que facilita ao invés de impor, e que respeita a autonomia individual enquanto fornece suporte inteligente.

Toda decisão de implementação deve ser avaliada contra esta filosofia. Funcionalidades que automatizam sem confirmação, que tomam decisões sem consultar o usuário, ou que obscurecem o que está acontecendo, devem ser rejeitadas por não alinharem com os princípios arquiteturais fundamentais do TimeBlock.

---

**Próxima Revisão:** Após implementação completa da versão 2.0
