# ADR-023: Microservices Ecosystem

**Status:** Proposto

**Data:** 21 de Dezembro de 2025

**Contexto:** v3.0.0 Planning

---

## Contexto

O TimeBlock Core atende bem ao gerenciamento de hábitos e rotinas. Casos de uso adjacentes (medicamentos, compromissos, listas) requerem lógica especializada que não pertence ao core.

## Decisão

Adotar arquitetura de microservices com comunicação event-driven via Apache Kafka.

### Princípios

1. **Serviços Independentes:** Cada serviço funciona 100% standalone
2. **Integração Opt-in:** Conexões entre serviços são opcionais
3. **Event Streaming:** Kafka como backbone de comunicação
4. **Contratos Versionados:** CloudEvents + JSON Schema

### Por que Kafka

| Critério   | RabbitMQ         | Kafka              | Decisão |
| ---------- | ---------------- | ------------------ | ------- |
| Modelo     | Message broker   | Event log          | Kafka   |
| Retenção   | Consome e deleta | Retém configurável | Kafka   |
| Replay     | Não suporta      | Event sourcing     | Kafka   |
| Throughput | ~50k msg/s       | ~1M msg/s          | Kafka   |
| Auditoria  | Manual           | Built-in           | Kafka   |

**Justificativa:**

- Event sourcing permite reconstruir estado
- Replay de eventos para debugging/recovery
- Múltiplos consumers leem mesmo evento
- Auditoria completa de ações
- Skill relevante para portfolio DevOps

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      Apache Kafka                           │
│                                                             │
│  Topics:                                                    │
│  - timeblock.habits      - medblock.doses                   │
│  - timeblock.timer       - eventblock.events                │
│  - timeblock.routines    - listblock.items                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
      ┌───────────────────────┼───────────────────────┐
      │                       │                       │
      v                       v                       v
┌────────────┐          ┌────────────┐          ┌────────────┐
│ TimeBlock  │          │ MedBlock   │          │ EventBlock │
│   Core     │          │            │          │            │
│            │          │ Standalone │          │ Standalone │
│ Standalone │          │            │          │            │
└────────────┘          └────────────┘          └────────────┘
```

### Serviços Planejados

| Serviço        | Responsabilidade             | Topics Publicados |
| -------------- | ---------------------------- | ----------------- |
| TimeBlock Core | Hábitos, rotinas, timer      | `timeblock.*`     |
| MedBlock       | Medicamentos, doses, estoque | `medblock.*`      |
| EventBlock     | Compromissos, bloqueios      | `eventblock.*`    |
| ListBlock      | Listas, itens de compras     | `listblock.*`     |

### Integrações Opt-in

| Evento                     | Consumer (opcional) | Ação               |
| -------------------------- | ------------------- | ------------------ |
| `medblock.dose.scheduled`  | TimeBlock Core      | Cria HabitInstance |
| `eventblock.event.created` | TimeBlock Core      | Bloqueia slot      |
| `listblock.list.created`   | TimeBlock Core      | Gera Task          |

### Formato de Eventos (CloudEvents)

```json
{
  "specversion": "1.0",
  "type": "medblock.dose.scheduled",
  "source": "/medblock/v1",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2025-12-21T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "medication_id": 123,
    "medication_name": "Omeprazol",
    "scheduled_time": "08:00",
    "dosage": "20mg"
  }
}
```

### Stack Tecnológica

| Componente      | Tecnologia                | Versão |
| --------------- | ------------------------- | ------ |
| Message Broker  | Apache Kafka              | 3.x    |
| Schema Registry | Confluent SR              | 7.x    |
| Serialização    | JSON (v3.0), Avro (v3.1+) | -      |
| Python Client   | confluent-kafka           | 2.x    |
| Formato Eventos | CloudEvents               | 1.0    |

## Consequências

### Positivas

- Cada serviço evolui independentemente
- Replay de eventos para debug/recovery
- Auditoria completa built-in
- Escalabilidade por serviço
- Falha isolada
- Portfolio com Kafka

### Negativas

- Complexidade operacional (Kafka + KRaft)
- Eventual consistency (não ACID global)
- Curva de aprendizado Kafka
- Infra adicional

### Mitigações

- Kafka com KRaft (sem Zookeeper)
- Dead-letter topics para retry
- Tracing distribuído (OpenTelemetry)
- Idempotência em consumers
- Docker Compose para dev local

## Alternativas Consideradas

1. **RabbitMQ** - Rejeitado: Sem replay, sem event sourcing
2. **REST Síncrono** - Rejeitado: Acoplamento temporal
3. **Shared Database** - Rejeitado: Schema coupling

## Referências

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/)
