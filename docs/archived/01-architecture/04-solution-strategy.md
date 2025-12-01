# 4. Estratégia de Solução

## Decisões Chave

1. **Local-first:** SQLite sem backend
2. **Type-safe:** SQLModel + Pydantic
3. **Resource-first CLI:** Melhor UX
4. **Priority-based reordering:** Simples e explicável

## Padrões

- Service Layer para lógica
- Repository implícito (SQLModel)
- Command pattern (CLI)
