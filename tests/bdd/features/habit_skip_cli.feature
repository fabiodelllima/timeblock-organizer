# language: en
# BR-CLI-HABIT-SKIP-001: Comando CLI para skip de hábito
Feature: CLI Habit Skip Command (BR-CLI-HABIT-SKIP-001)
  As a TimeBlock user
  I want to use timeblock habit skip in the terminal
  So that I can mark habits as skipped quickly

  Background:
    Given an active routine "Rotina Matinal" exists
    And a habit "Academia" with ID 1 exists
    And a HabitInstance with ID 42 for today exists

  # Skip justificado: motivo via --reason, com nota
  Scenario: Skip with reason via flag
    When the user executes command "habit skip 42 --reason WORK --note 'Reunião urgente'"
    Then the command should succeed
    And the output should contain "skipped"
    And HabitInstance 42 should have status NOT_DONE
    And HabitInstance 42 should have substatus SKIPPED_JUSTIFIED
    And HabitInstance 42 should have skip_reason WORK
    And HabitInstance 42 should have skip_note "Reunião urgente"

  # Skip justificado sem nota
  Scenario: Skip with reason without note
    When the user executes command "habit skip 42 --reason FAMILY"
    Then the command should succeed
    And HabitInstance 42 should have substatus SKIPPED_JUSTIFIED
    And HabitInstance 42 should have skip_reason FAMILY
    And HabitInstance 42 should have skip_note NULL

  # Skip sem justificativa via --unjustified
  Scenario: Skip unjustified via flag
    When the user executes command "habit skip 42 --unjustified"
    Then the command should succeed
    And HabitInstance 42 should have status NOT_DONE
    And HabitInstance 42 should have substatus SKIPPED_UNJUSTIFIED
    And HabitInstance 42 should have no skip_reason

  # Erro: nem --reason nem --unjustified informados
  Scenario: Error when neither reason nor unjustified is given
    When the user executes command "habit skip 42"
    Then the command should fail
    And the output should contain "--reason"

  # Erro: --reason e --unjustified são mutuamente exclusivos
  Scenario: Error when reason and unjustified are combined
    When the user executes command "habit skip 42 --reason WORK --unjustified"
    Then the command should fail
    And the output should contain "mutuamente exclusiv"

  # Erro: instância inexistente
  Scenario: Error when skipping nonexistent instance
    When the user executes command "habit skip 999 --reason HEALTH"
    Then the command should fail
    And the output should contain "não encontrada"

  # Erro: motivo inválido
  Scenario: Error when using invalid reason
    When the user executes command "habit skip 42 --reason INVALID"
    Then the command should fail
    And the output should contain "inválida"
