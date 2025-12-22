# ADR-024: Homelab Infrastructure Strategy

## Status

Proposto

## Contexto

O TimeBlock v2.0+ requer servidor para sincronização entre dispositivos (Desktop Linux, Android/Termux). Precisamos definir a estratégia de infraestrutura que:

1. Mantenha baixo custo operacional
2. Garanta privacidade dos dados
3. Permita disponibilidade 24/7
4. Seja compatível com ADR-012 (Manual Sync)

## Decisão

**Adotamos Raspberry Pi como servidor homelab recomendado para v2.0-stable.**

### Progressão de Deployment

| Fase        | Servidor      | Características               |
| ----------- | ------------- | ----------------------------- |
| v2.0-alpha  | Desktop Linux | Manual start, desenvolvimento |
| v2.0-beta   | Desktop Linux | UX melhorada, uso diário      |
| v2.0-stable | Raspberry Pi  | Always-on 24/7, produção      |

### Hardware Especificado

| Componente     | Especificação    | Justificativa                                     |
| -------------- | ---------------- | ------------------------------------------------- |
| Raspberry Pi 4 | 4GB RAM          | Suficiente para FastAPI + PostgreSQL + Monitoring |
| Armazenamento  | SSD USB 256GB+   | Evita degradação de SD card, melhor I/O           |
| Rede           | Ethernet Gigabit | Latência consistente vs WiFi                      |

### Stack de Software

```yaml
services:
  timeblock-api:
    image: timeblock/api:latest
    # FastAPI + Uvicorn

  db:
    image: postgres:15-alpine
    # PostgreSQL para produção

  prometheus:
    image: prom/prometheus:latest
    # Métricas

  grafana:
    image: grafana/grafana:latest
    # Dashboards
```

### Princípios Mantidos

1. **Sync Manual (ADR-012):** Pi disponibiliza servidor 24/7, mas sync continua via `timeblock connect`
2. **Offline-First (ADR-005):** Clientes funcionam 100% offline, Pi é opcional
3. **User Control (ADR-006):** Usuário decide quando sincronizar

## Implementação

### v2.0-alpha (Desktop)

```bash
# Iniciar servidor manualmente
$ timeblock server start --port 8000
```

### v2.0-stable (Raspberry Pi)

```bash
# Setup inicial no Pi
$ docker-compose up -d

# Clientes conectam quando querem
$ timeblock connect
```

## Referências

- [ADR-005: Offline-First](ADR-005-offline-first.md)
- [ADR-006: User Control Philosophy](ADR-006-user-control.md)
- [ADR-012: Sync Strategy](ADR-012-sync-strategy.md)
- [Architecture: Deployment Options](../core/architecture.md#10-deployment-options)

---

**Data:** 21 de Dezembro de 2025
