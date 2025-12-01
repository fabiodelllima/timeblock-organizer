# ADR-001: SQLModel como ORM

- **Status**: Accepted
- **Data**: 2025-09-15

## Contextoo

Precisávamos escolher um ORM para o TimeBlock que atendesse:

- Funcionamento com SQLite (local-first)
- Type hints nativos do Python
- Simplicidade para projeto médio porte
- Migrations controladas

## Decisão

Adotamos **SQLModel** por combinar SQLAlchemy com Pydantic.

## Alternativas Consideradas

### SQLAlchemy Puro

**Prós:**

- Controle total
- Documentação extensa
- Battle-tested

**Contras:**

- Verboso
- Sem validação built-in
- Setup complexo

### Django ORM

**Prós:**

- Maduro
- Migrations excelentes

**Contras:**

- Traz todo Django
- Overkill para CLI
- Menos flexível

### Peewee

**Prós:**

- Leve
- Simples

**Contras:**

- Menos recursos
- Comunidade menor

## Consequências

### Positivas

- Código type-safe
- Validação via Pydantic
- Serialização JSON fácil
- Boa DX

### Negativas

- Dependência adicional (Pydantic)
- Menos exemplos que SQLAlchemy puro
- Relativamente novo

### Neutras

- Performance similar a SQLAlchemy
- Curva de aprendizado moderada

## Validação

Consideramos acertada se:

- Redução de bugs de tipo em 50%
- Código models 30% mais conciso
- Facilita testes com fixtures

## Referências

- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
