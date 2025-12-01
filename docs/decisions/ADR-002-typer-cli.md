# ADR-002: Typer para CLI Framework

- **Status**: Accepted
- **Data**: 2025-09-15

## Contextoo

Precisávamos de framework CLI que oferecesse:

- Type hints nativos
- Validação automática de argumentos
- Documentação gerada automaticamente
- Subcomandos organizados
- Autocompleção shell

## Decisão

Adotamos **Typer** (baseado em Click).

## Alternativas Consideradas

### Click

**Prós:**

- Maduro e estável
- Documentação extensa
- Usado por Flask, Pytest

**Contras:**

- Decorators verbosos
- Sem type hints nativos
- Validação manual

### argparse

**Prós:**

- Standard library
- Zero dependências

**Contras:**

- Verboso demais
- Sem validação automática
- Documentação manual

### Fire (Google)

**Prós:**

- Zero boilerplate
- Gera CLI de qualquer função

**Contras:**

- Magia demais
- Difícil controlar interface
- Mensagens de erro ruins

## Consequências

### Positivas

- Type hints = validação grátis
- Help gerado automaticamente
- Code completion funciona
- Menos código boilerplate

### Negativas

- Dependência externa (mas leve)
- Menos flexível que Click puro

### Neutras

- Performance idêntica ao Click
- Curva de aprendizado baixa

## Validação

Consideramos acertada se:

- Redução de 50% em código de parsing
- Help sempre atualizado
- Zero bugs de tipo em args

## Referências

- [Typer Docs](https://typer.tiangolo.com/)
- [Comparação com Click](https://typer.tiangolo.com/#typer-vs-click)
