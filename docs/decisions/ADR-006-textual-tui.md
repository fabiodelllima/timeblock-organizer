# ADR-006: Textual para TUI

- **Status:** Proposed
- **Data:** 2025-10-01

## Contextoo

CLI funcional, mas UX limitada para visualização de agenda e navegação.

Requisitos:

- Visualização de calendário
- Navegação interativa
- Compatível com terminais modernos
- Não bloquear uso via CLI puro

## Decisão

Adicionar TUI com **Textual** (Python framework).

Modo híbrido:

- CLI para automação/scripts
- TUI para uso interativo

## Alternativas

### Rich apenas

**Prós:** Já usamos Rich
**Contras:** Sem interatividade

### Prompt Toolkit

**Prós:** Maduro, flexível
**Contras:** Low-level, mais código

### Urwid

**Prós:** Estável
**Contras:** API antiga, menos moderno

## Consequências

### Positivas

- Calendário visual
- Navegação teclado/mouse
- Reactive updates
- Textual usa Rich (já dep)

### Negativas

- Dependência adicional
- Complexidade de manutenção
- Testes mais difíceis

### Neutras

- CLI permanece primário
- TUI é opcional

## Validação

- Lançamento calendário < 500ms
- Navegação fluida (60 FPS)
- Testes automatizados funcionam

## Implementação

```python
from textual.app import App

class TimeBlockTUI(App):
    def compose(self):
        yield CalendarView()
        yield EventList()
```

## Roadmap

1. v2.1: Calendar view básico
2. v2.2: Event editor inline
3. v2.3: Reordering preview
