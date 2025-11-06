# TimeBlock Organizer - Roadmap v2.0

**Data**: 05 de Novembro de 2025

**Timeline**: 12 meses (Nov 2025 - Nov 2026)

**Objetivo**: Evoluir de CLI local para sistema distribuido offline-first

## Visao Geral

### Estado Atual (v1.2.0)

- CLI local: 100%
- Models e Services: 100%
- Tests: 70% (unit + integration, sem E2E completos)
- Docs: 80%

**Gaps v2.0:**

- Sync infrastructure: 0%
- E2E tests: 4% (1/26)
- DevOps: 0%
- Docs sync: 0%

### Objetivo Final (v2.0-stable)

- Sincronizacao Linux - Android (Termux)
- Offline-first com Queue-Based Sync
- Discovery automatico (mDNS)
- Conflict resolution interativo
- FastAPI server local
- CI/CD completo
- 26 E2E tests
- Docker + Monitoring

## Milestones

```terminal
v1.2.0
  Sprint 1.4 (1 sem)  → Docs Showcase
  Sprint 1.5 (2 sem)  → E2E Foundation
  v1.3.0 (3 meses)    → Sync Infrastructure
    v2.0-alpha (2 meses) → Sync MVP
      v2.0-beta (2 meses) → Enhanced
        v2.0-stable (2 meses) → Production
```

## Sprint 1.4 - Documentacao Showcase (1 semana)

**Status**: EM ANDAMENTO
**Datas**: 04-10 Nov 2025

**Tarefas:**

- ADR-012: Sync Strategy
- ADR-013: Offline-First Schema
- ADR-014: Sync UX Flow
- ARCHITECTURE.md: Sync section
- ROADMAP.md: Este documento
- CI/CD: GitHub Actions
- E2E: 5 testes scaffolding

**Entregaveis:**

- 3 ADRs sync
- ARCHITECTURE.md atualizado
- ROADMAP.md completo
- CI/CD pipeline
- 5 E2E tests estrutura

## Sprint 1.5 - E2E Tests Foundation (2 semanas)

**Datas**: 11-24 Nov 2025

**Tarefas:**

- Mock server basico
- test_habit_management.py (5 testes)
- test_instance_generation.py (4 testes)
- Coverage E2E >50%

**Entregaveis:**

- 9 E2E tests funcionando
- Mock server
- Coverage report E2E

## v1.3.0 - Sync Infrastructure (3 meses)

**Datas**: Dez 2025 - Fev 2026

### Sprint 1.3.1 - Models Migration (2 semanas)

- Alembic migration 002_offline_first.py
- Atualizar 7 models (UUID + 6 campos)
- Migration testing
- Migration guide

### Sprint 1.3.2 - Services Update (2 semanas)

- Atualizar 5 services CRUD
- Queue integration
- device_id persistence
- Tests atualizados

### Sprint 1.3.3 - Sync Services (3 semanas)

- SyncQueue service
- DiscoveryService (mDNS)
- SyncService base
- Tests unitarios (15+)

### Sprint 1.3.4 - E2E Sync Tests (2 semanas)

- test_sync_queue.py (3 testes)
- test_sync_discovery.py (3 testes)
- Mock server avancado

### Sprint 1.3.5 - Documentation (1 semana)

- sync-protocol.md
- queue-specification.md
- Atualizar ARCHITECTURE.md

## v2.0-alpha - Sync MVP (2 meses)

**Datas**: Mar - Abr 2026

### Sprint 2.0.1 - Connect Command (2 semanas)

- Implementar `timeblock connect`
- Discovery integration
- Queue push/pull

### Sprint 2.0.2 - FastAPI Server (2 semanas)

- api/main.py
- POST /sync/push
- GET /sync/pull
- mDNS announcement

### Sprint 2.0.3 - Conflict Resolution (2 semanas)

- Last-write-wins logic
- Interactive UI
- Auto-resolve mode

### Sprint 2.0.4 - E2E Complete (2 semanas)

- test_sync_connect.py (8 testes)
- test_conflict_detection.py (3 testes)
- 26/26 E2E tests completos

## v2.0-beta - Enhanced Sync (2 meses)

**Datas**: Mai - Jun 2026

- Dashboard TUI
- Healthcheck e Monitoring
- Error Recovery
- Performance Optimization

## v2.0-stable - Production (2 meses)

**Datas**: Jul - Ago 2026

- Raspberry Pi deployment
- Docker e Compose
- Monitoring Production
- Security Audit

## v2.5+ - Future

**Timeline**: 2027+

- v2.5: Field-level timestamps, VPN support
- v3.0: Rust CRDT layer
- v3.5: Peer-to-peer sync
- v4.0: External integrations

## Metricas de Sucesso

### v1.3.0

- Migration sucesso: 100%
- E2E tests: 15/26
- Coverage: >85%

### v2.0-alpha

- Connect funciona: 100%
- Sync 100 ops: <5s
- E2E tests: 26/26

### v2.0-stable

- Pi uptime: >99.9%
- Zero vulnerabilidades criticas
- Documentation 100%

## Riscos e Mitigacoes

1. **Migration Complexity** → Backup automatico, testing extensivo
2. **mDNS Reliability** → Fallback IP manual
3. **Scope Creep** → Strict MVP scope

---

**Criado**: 05 de Novembro de 2025

**Proxima Revisao**: Apos Sprint 1.4
