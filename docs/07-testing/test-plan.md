# Test Plan

## Critical Paths

1. Habit generation
2. Event reordering
3. Conflict detection
4. Timer lifecycle

## Test Matrix

| Componente | Unit | Integration | E2E |
|------------|------|-------------|-----|
| Services | [OK] | [OK] | - |
| Models | [OK] | - | - |
| CLI | - | [OK] | [OK] |
| Reordering | [OK] | [OK] | [OK] |
