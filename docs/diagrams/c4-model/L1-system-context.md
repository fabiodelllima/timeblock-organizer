# C4 Level 1: System Context

```mermaid
graph TB
    User([Usuário<br/>Gerencia tempo e hábitos])

    TimeBlock[TimeBlock Organizer<br/>CLI para hábitos e agenda]

    Calendar[Calendário Externo<br/>Google Calendar, Outlook]
    Notification[Sistema de Notificações<br/>OS Native]

    User -->|Usa CLI/TUI| TimeBlock
    TimeBlock -.->|Sync futuro| Calendar
    TimeBlock -->|Envia lembretes| Notification

    style TimeBlock fill:#1168bd,stroke:#0b4884,color:#fff
    style Calendar fill:#999,stroke:#666,color:#fff
    style Notification fill:#999,stroke:#666,color:#fff
    style User fill:#08427b,stroke:#052e56,color:#fff
```

## Elementos

**Usuário:** Pessoa organizando tempo e cultivando hábitos

**TimeBlock Organizer:** Sistema core (SQLite local-first)

**Calendário Externo:** Sincronização futura com Google Calendar/Outlook via CalDAV

**Sistema de Notificações:** Lembretes via notificações nativas do OS
