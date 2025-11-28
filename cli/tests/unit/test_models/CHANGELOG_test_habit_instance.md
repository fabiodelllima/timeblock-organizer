# Changelog: test_habit_instance.py

## 2025-11-03 - Sprint 1.2 Fase 1

### Correções

#### **Bug 1: Comparação de Enum**

- Antes: `assert instance.status == "planned"`
- Depois: `assert instance.status == HabitInstanceStatus.PLANNED`
- Razão: Status é enum, não string

#### **Bug 2: Teste Obsoleto Removido**

- Removido: `test_habit_instance_with_actuals`
- Razão: Campos `actual_start`/`actual_end` não existem no modelo atual
- Feature tracking pode ser v1.3.0+ usando TimeLog table

#### **Bug 3: ResourceWarnings**

- Adicionado: `engine.dispose()` no fixture
- Razão: Fechar conexões DB após testes

### Testes Atuais

1. `test_habit_instance_creation` - Criação básica
2. `test_habit_instance_manually_adjusted` - Flag manual adjustment

### TODO Futuro

- v1.3.0: Considerar feature de actual times tracking
- Usar TimeLog table para métricas de tempo real vs programado
