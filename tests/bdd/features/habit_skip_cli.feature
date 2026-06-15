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

  # Skip com categoria via flag
  Scenario: Skip with category via flag
    When the user executes command "habit skip 42 --reason WORK --note 'Reunião urgente'"
    Then the command should succeed
    And the output should contain "skipped"
    And HabitInstance 42 should have status NOT_DONE
    And HabitInstance 42 should have skip_reason WORK
    And HabitInstance 42 should have skip_note "Reunião urgente"

  # Skip com categoria sem nota
  Scenario: Skip with category without note
    When the user executes command "habit skip 42 --reason FAMILY"
    Then the command should succeed
    And HabitInstance 42 should have skip_reason FAMILY
    And HabitInstance 42 should have skip_note NULL

  # Erro ao skip de instância inexistente
  Scenario: Error when skipping nonexistent instance
    When the user executes command "habit skip 999 --reason HEALTH"
    Then the command should fail
    And the output should contain "não encontrada"

  # Erro ao usar categoria inválida
  Scenario: Error when using invalid category
    When the user executes command "habit skip 42 --reason INVALID"
    Then the command should fail
    And the output should contain "inválida"

  # Skip sem justificativa via flag
  Scenario: Skip without justification via flag
    When the user executes command "habit skip 42 --unjustified"
    Then the command should succeed
    And the output should contain "skipped"
    And HabitInstance 42 should have status NOT_DONE
    And HabitInstance 42 should have substatus SKIPPED_UNJUSTIFIED
    And HabitInstance 42 should have skip_reason NULL

  # Erro: --reason e --unjustified são mutuamente exclusivos
  Scenario: Error when combining reason and unjustified
    When the user executes command "habit skip 42 --reason WORK --unjustified"
    Then the command should fail
    And the output should contain "exclusiv"

  # Erro: skip sem motivo e sem --unjustified
  Scenario: Error when skipping without reason
    When the user executes command "habit skip 42"
    Then the command should fail
    And the output should contain "--reason"
