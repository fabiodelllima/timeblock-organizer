# ADR-020: Padrão de Nomenclatura de Regras de Negócio

- **Status:** Aceito
- **Data:** 11 de Novembro de 2025
- **Contexto:** Sprint 2 - Test Refactoring

## Contexto

Durante o refactoring de testes (Sprint 2), identificamos que a nomenclatura de Business Rules evoluiu de forma inconsistente:

- **Padrão Antigo:** `BR-DOMINIO-001` (sem categoria)
- **Padrão Novo:** `BR-DOMINIO-CATEGORIA-001` (com categoria)

Exemplo:

- Antigo: `BR-TASK-001`, `BR-TASK-002`
- Novo: `BR-TASK-CREATE-001`, `BR-TASK-INPUT-001`

## Decisão

Adotamos padrão **categórico** para todas as BRs:

```terminal
BR-{DOMINIO}-{CATEGORIA}-{NUMERO}
```

**Componentes:**

- `DOMINIO`: Domínio de negócio (TASK, HABIT, EVENT, SYSTEM, DB)
- `CATEGORIA`: Categoria funcional (CREATE, DELETE, LIST, REORDER, INPUT, VALIDATION, FILTER, MIGRATE)
- `NUMERO`: Sequencial de 3 dígitos (001-999)

**Exemplos:**

```terminal
BR-TASK-CREATE-001: Criação básica de task
BR-TASK-INPUT-002: Validação de título
BR-HABIT-LIST-001: Listagem vazia
BR-EVENT-FILTER-003: Filtro por dia
BR-DB-MIGRATE-001: Criação de tabelas
```

## Justificativa

**Vantagens:**

1. **Escalabilidade:** 999 BRs por categoria vs 999 total por domínio
2. **Organização:** Agrupamento lógico claro por funcionalidade
3. **Rastreabilidade:** Mapear BR → Teste → Código fica mais direto
4. **Manutenibilidade:** Categorias facilitam navegação e busca
5. **Clareza:** Nome autodescritivo da funcionalidade

**Comparação:**

```terminal
Antigo: BR-TASK-015 (qual funcionalidade?)
Novo:   BR-TASK-CREATE-001 (criação de task - claro!)
```

**Migração:**

- BRs antigas serão mapeadas para novo padrão
- Documentação atualizada primeiro (docs-first)
- Testes já seguem novo padrão (Sprint 2)

## Consequências

**Positivas:**

- Documentação mais estruturada e navegável
- Melhor rastreabilidade em auditorias
- Padrão escalável para centenas de BRs
- Facilita onboarding de novos desenvolvedores

**Negativas:**

- Esforço único de migração de docs existentes
- Breaking change em referências antigas (se houver)
- Nomes de BRs mais longos

**Mitigações:**

- Criar tabela de mapeamento (antigo → novo)
- Manter comentários com referências antigas por 1 versão
- Scripts de migração automática onde possível

## Implementação

### **Fase 1: Documentação**

1. Atualizar `docs/04-specifications/business-rules/*.md`
2. Criar `docs/04-specifications/business-rules/MIGRATION-MAP.md`
3. Atualizar índice em `docs/07-testing/README.md`

### **Fase 2: Verificação**

4. Validar que todos os testes referenciam BRs corretas
5. Atualizar RTM (Requirements Traceability Matrix)

### **Fase 3: Comunicação**

6. Documentar mudança no CHANGELOG
7. Atualizar guias de contribuição

## Referências

- ADR-018: Language Standards (idioma português)
- ADR-019: Test Naming Convention (base para esta decisão)
- Sprint 2: Test Refactoring (contexto da mudança)
- `docs/04-specifications/business-rules/` (local das BRs)

## Exemplos

**Domínios identificados:**

- TASK: Tasks pontuais
- HABIT: Hábitos recorrentes
- EVENT: Eventos genéricos
- SYSTEM: Sistema/Inicialização
- CLI: Interface de linha de comando
- DB: Database/Migrações
- TEST: Infraestrutura de testes

**Categorias por domínio:**

- CREATE, DELETE, UPDATE, LIST (CRUD)
- INPUT, VALIDATION (Validações)
- FILTER, SEARCH (Consultas)
- REORDER, CONFLICT (Lógica de negócio)
- MIGRATE, INIT (Sistema)

---

**Relacionado:** ADR-018 (Language Standards), ADR-019 (Test Naming)

**Revisão:** Após conclusão da migração de docs
