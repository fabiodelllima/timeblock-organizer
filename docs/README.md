# TimeBlock Organizer - Documentação

Documentação técnica do TimeBlock Organizer.

---

## Documentação Principal

| Documento | Descrição | Versão |
|-----------|-----------|--------|
| [architecture.md](core/architecture.md) | Arquitetura, stack, camadas | v2.0.0 |
| [business-rules.md](core/business-rules.md) | 50 regras de negócio | v3.0.0 |
| [cli-reference.md](core/cli-reference.md) | Referência completa da CLI | v1.4.0 |
| [workflows.md](core/workflows.md) | Fluxos e cenários BDD | v2.1.0 |

---

## Seções

### [decisions/](decisions/)

22 Architecture Decision Records (ADRs) documentando decisões técnicas.

### [diagrams/](diagrams/)

Diagramas Mermaid: C4 Model, sequências, estados, ER.

### [testing/](testing/)

Estratégia de testes, cenários BDD, matriz de rastreabilidade.

### [archived/](archived/)

Documentação histórica (130+ arquivos). Consultar apenas para referência.

---

## Início Rápido

**Novo no projeto?** Leia nesta ordem:

1. [architecture.md](core/architecture.md) - visão geral
2. [business-rules.md](core/business-rules.md) - regras do domínio
3. [cli-reference.md](core/cli-reference.md) - como usar

**Contribuindo?** Adicione também:

4. [decisions/](decisions/) - entender decisões passadas
5. [testing/](testing/) - estratégia de testes

---

## Convenções

- **Idioma:** Documentação em Português, código em Inglês
- **Business Rules:** Formato `BR-DOMAIN-XXX`
- **ADRs:** Formato `ADR-XXX-nome.md`
- **Commits:** Português, formato convencional

---

## Links Externos

- [Atomic Habits](https://jamesclear.com/atomic-habits) - Filosofia base
- [SQLModel](https://sqlmodel.tiangolo.com/) - ORM
- [Typer](https://typer.tiangolo.com/) - Framework CLI
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
