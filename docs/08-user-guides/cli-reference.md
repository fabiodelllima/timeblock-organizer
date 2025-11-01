# CLI Reference Completo

## Habit Commands

### add

```shell
timeblock habit add <name> --recurrence <RRULE> --duration <minutes> [--priority <1-5>]
```

### list

```shell
timeblock habit list [--today] [--status <planned|completed|skipped>]
```

### complete

```shell
timeblock habit complete <id> [--actual-duration <minutes>]
```

### skip

```shell
timeblock habit skip <id> [--reason <text>]
```

## Task Commands

### add

```shell
timeblock task add <title> [--deadline <date>] [--priority <1-5>]
```

### list

```shell
timeblock task list [--overdue] [--status <pending|completed>]
```

### complete

```shell
timeblock task complete <id>
```

## Reschedule

```shell
timeblock reschedule [--preview] [--apply] [--date <YYYY-MM-DD>]
```

## Timer

```shell
timeblock timer start <event_id>
timeblock timer pause
timeblock timer resume
timeblock timer stop
```

## Config

```shell
timeblock config set <key> <value>
timeblock config get <key>
timeblock config list
```
