# Problemas Encontrados e Soluções

**Data:** 2025-10-29  
**Sessão:** Documentação Completa TimeBlock

## Problemaas Identificados

### 1. Mermaid Não Renderizava

**Problema:** Diagramas Mermaid apareciam como código raw.

**Causa:** `mkdocs.yml` sem configuração adequada.

**Solução:** Usar `pymdownx.superfences` simples (funciona com mkdocs-material).

**Status:** RESOLVIDO

---

### 2. Documentação Incompleta (60%)

**Problema:** Arquivos criados mas não mapeados no `mkdocs.yml`.

**Lacunas:**

- ADRs 001-008 não listados
- Diagramas não mapeados
- Services/Models/CLI sem navegação
- Business Rules invisíveis

**Solução:** `mkdocs.yml` completo com nav estruturado.

**Status:** RESOLVIDO

---

### 3. READMEs Faltantes

**Problema:** Seções sem arquivo índice.

**Arquivos criados:**

- `docs/03-decisions/README.md`
- `docs/04-specifications/README.md`
- `docs/14-development/README.md`

**Status:** RESOLVIDO

---

### 4. Pastas Vazias

**Problema:** 4 pastas sem conteúdo.

**Preenchidas:**

- protocols/ (validation, error-handling)
- fixtures/ (test fixtures)
- reference/ (rrule-examples, priority-guide)
- templates/ (adr, issue)

**Status:** RESOLVIDO

---

### 5. site_url Incorreto

**Problema:** Domínio não configurado.

**Solução:** Alterar para GitHub Pages.

**Status:** PENDENTE (decisão do usuário)

---

## Débito Técnico Identificado

### Código

| Item                     | Severidade | Esforço | Prioridade |
| ------------------------ | ---------- | ------- | ---------- |
| Remover tuple returns    | Média      | 4h      | Alta       |
| RoutineService faltando  | Alta       | 8h      | Média      |
| ReportService faltando   | Média      | 6h      | Baixa      |
| E2E tests (0%)           | Alta       | 12h     | Alta       |
| CLI parsers sem testes   | Média      | 3h      | Média      |
| Type hints strict (mypy) | Baixa      | 2h      | Baixa      |

### Documentação

| Item                 | Severidade | Esforço | Prioridade   |
| -------------------- | ---------- | ------- | ------------ |
| C4 Level 3-4         | Baixa      | 4h      | Baixa (v2.0) |
| Protocols completos  | Média      | 2h      | Média        |
| Tutoriais detalhados | Baixa      | 4h      | Baixa        |
| Research papers      | Baixa      | 6h      | Baixa        |

### Features Faltantes

| Feature              | Escopo | Esforço | Prioridade |
| -------------------- | ------ | ------- | ---------- |
| Routine execution    | v1.0?  | 12h     | TBD        |
| Reports/Analytics    | v1.0   | 8h      | Alta       |
| Config management    | v1.0   | 4h      | Média      |
| Export/Import        | v1.1   | 6h      | Baixa      |
| TUI (Textual)        | v2.0   | 20h     | Baixa      |
| Google Calendar sync | v2.0   | 30h     | Baixa      |

### Qualidade

| Item              | Meta       | Atual | Gap |
| ----------------- | ---------- | ----- | --- |
| Test Coverage     | 90%        | ~75%  | 15% |
| Unit Tests        | 90%        | 85%   | 5%  |
| Integration Tests | 80%        | 70%   | 10% |
| E2E Tests         | 5 cenários | 0     | 5   |

## Próximas Ações

### Imediato (Sessão Atual)

- [x] Preencher pastas vazias
- [x] Corrigir mkdocs.yml
- [x] Criar READMEs faltantes
- [x] Documentar problemas
- [ ] Definir site_url
- [ ] Gerar prompt próximo chat

### Curto Prazo (1-2 semanas)

- [ ] Remover tuple returns
- [ ] Completar E2E tests
- [ ] Implementar Reports
- [ ] Coverage → 90%

### Médio Prazo (1 mês)

- [ ] RoutineService
- [ ] Config management
- [ ] Release v1.0

### Longo Prazo (v2.0)

- [ ] TUI com Textual
- [ ] Google Calendar sync
- [ ] C4 Level 3-4
