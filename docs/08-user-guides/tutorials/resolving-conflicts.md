# Tutorial: Resolvendo Conflitos

## Cenário

Você tem:

- Meditação: 07:00-07:15 (P3)
- Reunião urgente: 07:00-08:00 (P5)

## Detectar

```shell
timeblock reschedule --preview
```

Output:

```terminal
Conflitos detectados: 1

Proposta:
[OK] Meditar: 07:00-07:15 → 08:00-08:15
  Motivo: Conflito com Reunião (prioridade 5)

Aceitar? (y/n)
```

## Aplicar

```shell
y
```

Meditação movida automaticamente!
