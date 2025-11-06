# ADR-007: Implementar Alembic em v1.3.0, Não v1.2.0

**Status:** ACEITO

**Data:** 03 de Novembro de 2025

**Contexto:** v1.2.0 - Infraestrutura

## Contexto

Projeto com 1 usuário (desenvolvedor). Debate sobre quando implementar Alembic (versionamento de schema de banco).

## Decisão

**Adiar Alembic para v1.3.0. Usar script Python simples em v1.2.0.**

## Razão

**v1.2.0 foca em qualidade:**

- Corrigir testes falhando
- Aumentar cobertura 69% → 90%
- Documentação showcase/portfolio

**v1.3.0 foca em infraestrutura:**

- Ambientes formalizados (dev/test/prod)
- Logging avançado
- Alembic (junto com ambientes)

**Separação lógica:** Implementar Alembic JUNTO com ambientes faz mais sentido arquiteturalmente.

## Alternativas Consideradas

### **A) Alembic em v1.2.0**

- Pros: Versionamento formal desde cedo
- Cons: Over-engineering para 1 usuário, mistura objetivos

### **B) Alembic em v2.0**

- Pros: Quando tiver múltiplos usuários
- Cons: Muito tarde, dificulta desenvolvimento

### **C) Alembic em v1.3.0 (ESCOLHIDA)**

- Pros: Junto com ambientes, momento certo na maturidade
- Cons: Nenhuma significativa

## Consequências

**v1.2.0:**

- Usa script Python para migrations simples
- Backup manual obrigatório antes de mudanças

**v1.3.0:**

- Alembic completo
- Migrations versionadas
- Rollback automático

## Portfolio/Showcase

Demonstra:

- Maturidade em priorização (quando usar cada ferramenta)
- Pragmatismo (não over-engineer)
- Visão de longo prazo (planejamento de v1.3.0)

---

**Relacionado:** ADR-008 (Ambientes), v1.3.0 roadmap
