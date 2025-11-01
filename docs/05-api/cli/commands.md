# CLI Commands Reference

## Habit Commands

```shell
timeblock habit add "Meditar" --recurrence "FREQ=DAILY" --duration 15
timeblock habit list
timeblock habit complete <id>
timeblock habit skip <id>
```

## Task Commands

```shell
timeblock task add "Finalizar relatório" --deadline "2025-11-01"
timeblock task list --overdue
timeblock task complete <id>
```

## Reschedule Command

```shell
timeblock reschedule --preview
timeblock reschedule --apply
```

## Timer Commands

```shell
timeblock timer start <event_id>
timeblock timer pause
timeblock timer resume
timeblock timer stop
```
