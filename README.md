# TimeBlock Organizer

> Gerenciador de tempo baseado em time blocking para terminal

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.13+-green.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-141%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Visão Geral

TimeBlock Organizer é uma ferramenta CLI (Command Line Interface) para gerenciamento de tempo usando a técnica de time blocking. Organize seus eventos em blocos de tempo, visualize sua agenda, e mantenha o controle da sua produtividade diretamente do terminal.

**v1.0.0** oferece funcionalidades essenciais de criação e listagem de eventos com validações robustas e suporte a múltiplos formatos de hora.

## Funcionalidades

### Comandos Disponíveis

- **`init`**: Inicializa o banco de dados SQLite
- **`add`**: Cria novos eventos com validações automáticas
- **`list`**: Lista eventos com filtros flexíveis por data

### Recursos Principais

- Múltiplos formatos de hora suportados (HH:MM, HHh, HHhMM)
- Detecção automática de eventos que cruzam meia-noite
- Validação de conflitos de horário
- Validação de duração (mínima e máxima)
- Categorização por cores
- Visualização em tabelas formatadas com Rich
- Persistência em SQLite

## Instalação

### Requisitos

- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)

### Setup

```bash
# Clone o repositório
git clone https://github.com/fabiodelllima/timeblock-organizer.git
cd timeblock-organizer/cli

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instale dependências
pip install -e .

# Inicialize o banco de dados
python -m src.timeblock.main init
```

## Uso

### Inicializar Banco de Dados

```bash
timeblock init
```

Cria o banco de dados SQLite em `data/timeblock.db`. Se já existir, pergunta se deseja reinicializar.

### Adicionar Eventos

#### Formato Padrão (HH:MM)

```bash
timeblock add "Reunião de equipe" -s 09:00 -e 10:30
timeblock add "Almoço" -s 12:00 -e 13:00 --desc "Restaurante XYZ"
```

#### Formato Coloquial (HHh e HHhMM)

```bash
timeblock add "Academia" -s 7h -e 8h30
timeblock add "Estudar Python" -s 14h -e 16h
timeblock add "Café" -s 15h30 -e 16h
```

#### Com Parâmetros Opcionais

```bash
timeblock add "Projeto X" \
  --start 14h \
  --end 17h \
  --date 2025-10-20 \
  --desc "Sprint planning e desenvolvimento" \
  --color blue
```

#### Evento que Cruza Meia-Noite

```bash
timeblock add "Plantão noturno" -s 23h -e 2h
# ⚠ Event crosses midnight (ends next day)
# ✓ Event created successfully!
```

### Listar Eventos

#### Ver Eventos de Hoje

```bash
timeblock list
# ou
timeblock list --day 0
```

#### Ver Eventos de Datas Específicas

```bash
# Amanhã
timeblock list --day 1

# Ontem
timeblock list --day -1

# Próxima segunda-feira
timeblock list --day monday

# Data específica
timeblock list --date 2025-10-25
```

#### Ver Semana Inteira

```bash
# Semana atual (próximos 7 dias)
timeblock list --week 0

# Próxima semana
timeblock list --week 1

# Semana passada
timeblock list --week -1
```

#### Ver Mês

```bash
# Mês atual
timeblock list --month 0

# Próximo mês
timeblock list --month 1
```

### Parâmetros dos Comandos

#### `add` - Criar Evento

| Parâmetro     | Obrigatório | Formato          | Descrição           |
| ------------- | ----------- | ---------------- | ------------------- |
| `title`       | Sim         | string           | Título do evento    |
| `-s, --start` | Sim         | HH:MM ou HHh[MM] | Hora de início      |
| `-e, --end`   | Sim         | HH:MM ou HHh[MM] | Hora de término     |
| `-d, --date`  | Não         | YYYY-MM-DD       | Data (padrão: hoje) |
| `--desc`      | Não         | string           | Descrição detalhada |
| `--color`     | Não         | nome/hex         | Cor do evento       |

#### `list` - Listar Eventos

| Parâmetro | Tipo       | Descrição                                                                |
| --------- | ---------- | ------------------------------------------------------------------------ |
| `--day`   | int/string | Dia relativo (0=hoje, 1=amanhã, -1=ontem) ou nome (monday, tuesday, etc) |
| `--week`  | int        | Semana relativa (0=atual, 1=próxima, -1=anterior)                        |
| `--month` | int        | Mês relativo (0=atual, 1=próximo, -1=anterior)                           |
| `--date`  | string     | Data específica YYYY-MM-DD                                               |

## Formatos de Hora

O sistema aceita três formatos de hora:

### 1. Formato Padrão (HH:MM)

```bash
09:00    # 9 da manhã
14:30    # 2:30 da tarde
23:45    # 11:45 da noite
```

### 2. Formato Coloquial Hora Inteira (HHh)

```bash
9h       # 9 da manhã
14h      # 2 da tarde
23h      # 11 da noite
```

### 3. Formato Coloquial com Minutos (HHhMM)

```bash
9h30     # 9:30 da manhã
14h15    # 2:15 da tarde
23h45    # 11:45 da noite
```

Todos os formatos são intercambiáveis:

```bash
timeblock add "Evento" -s 9h -e 10:30      # Misturado
timeblock add "Evento" -s 09:00 -e 10h30   # Misturado
timeblock add "Evento" -s 9h30 -e 11h      # Coloquial
```

## Validações

### Duração

- **Mínima**: Eventos devem ter duração maior que 0
- **Máxima**: Eventos não podem ter 24h ou mais

```bash
timeblock add "Curto" -s 10h -e 10h
# ✗ Event duration cannot be 24 hours or more

timeblock add "Longo" -s 10h -e 9h59
# ✓ Event created (23h59min)
```

### Conflitos

O sistema detecta e alerta sobre conflitos de horário:

```bash
timeblock add "Reunião A" -s 14h -e 15h
timeblock add "Reunião B" -s 14h30 -e 16h
# ⚠ Warning: Conflicts with existing event "Reunião A"
# ✓ Event created successfully!
```

### Cruzamento de Meia-Noite

Eventos que cruzam meia-noite são permitidos e sinalizados:

```bash
timeblock add "Virada" -s 23h -e 2h
# ⚠ Event crosses midnight (ends next day)
# ✓ Event created successfully!
# Duration: 3.0h
```

## Exemplos de Uso

### Rotina Diária

```bash
# Manhã
timeblock add "Acordar e exercícios" -s 7h -e 8h
timeblock add "Café da manhã" -s 8h -e 8h30
timeblock add "Trabalho focado" -s 9h -e 12h

# Tarde
timeblock add "Almoço" -s 12h -e 13h
timeblock add "Reuniões" -s 13h -e 15h
timeblock add "Trabalho focado" -s 15h -e 17h

# Noite
timeblock add "Jantar" -s 19h -e 20h
timeblock add "Estudos" -s 20h -e 22h

# Ver agenda do dia
timeblock list
```

### Planejamento Semanal

```bash
# Segunda-feira
timeblock add "Reunião de equipe" -s 9h -e 10h --date 2025-10-21
timeblock add "Sprint planning" -s 10h -e 12h --date 2025-10-21

# Terça-feira
timeblock add "Code review" -s 14h -e 15h --date 2025-10-22
timeblock add "Pair programming" -s 15h -e 17h --date 2025-10-22

# Ver semana
timeblock list --week 0
```

### Evento com Descrição Detalhada

```bash
timeblock add "Workshop Python Avançado" \
  -s 14h \
  -e 18h \
  --date 2025-10-25 \
  --desc "Tópicos: decorators, context managers, metaclasses. Local: Sala 201. Trazer laptop." \
  --color purple
```

## Visualização de Saída

### Listagem de Eventos

```
                                           This Week
 ID    Date        Title                 Time           Duration     Status          Color
 1     2025-10-16  Reunião de equipe     09:00 → 10:30      1.5h    planned            -
 2     2025-10-16  Almoço                12:00 → 13:00      1.0h    planned            -
 3     2025-10-16  Projeto X             14:00 → 17:00      3.0h    planned          blue

                                          Next 2 Weeks
 ID    Date        Title                 Time           Duration     Status          Color
 4     2025-10-21  Workshop Python       14:00 → 18:00      4.0h    planned         purple

Total: 4 events
```

### Avisos e Confirmações

```
✓ Event created successfully!
ID: 5
Academia
07:00 → 08:30 (1.5h)

⚠ Event crosses midnight (ends next day)
✓ Event created successfully!
ID: 6
Plantão noturno
23:00 → 02:00 (3.0h)

✗ Event duration cannot be 24 hours or more. Time blocking is designed for specific activities, not entire days.
```

## Estrutura do Projeto

```
cli/
├── src/timeblock/
│   ├── models/              # Modelos de dados (Event, EventColor, EventStatus)
│   ├── database/            # Engine SQLite e configuração
│   ├── commands/            # Comandos CLI (init, add, list)
│   └── utils/               # Validadores, formatadores, helpers
├── tests/                   # Suite de testes (141 testes)
├── data/                    # Banco de dados SQLite
├── pyproject.toml           # Configuração do projeto
└── requirements.txt         # Dependências
```

## Tecnologias

- **Python 3.13**: Linguagem principal
- **SQLModel**: ORM type-safe (SQLAlchemy + Pydantic)
- **Rich**: Formatação e tabelas no terminal
- **Typer**: Framework CLI moderno
- **Ruff**: Linter e formatter
- **SQLite**: Banco de dados local
- **pytest**: Framework de testes

## Testes

```bash
# Rodar todos os testes
pytest -v

# Com relatório de cobertura
pytest --cov=src/timeblock --cov-report=html

# Testes específicos
pytest tests/unit/
pytest tests/integration/

# Ver relatório HTML
open htmlcov/index.html
```

### Estatísticas

- **141 testes** passando
- **99% cobertura** de código
- Testes unitários e de integração
- Fixtures reutilizáveis
- Testes de caracterização para refatorações seguras

## Roadmap

### v1.0.0 (Atual)

- [x] Inicialização de banco de dados
- [x] Criar eventos com validações
- [x] Listar eventos com filtros
- [x] Múltiplos formatos de hora
- [x] Detecção de conflitos

### v2.0.0 (Planejado)

- [ ] Sistema de Habits recorrentes
- [ ] Reordenação adaptativa de eventos
- [ ] Interface Textual (TUI rica)
- [ ] Timer para tracking de tempo real
- [ ] Relatórios e análise de padrões
- [ ] Import/export via Markdown
- [ ] Comandos: update, delete, routine

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**Autor**: Fábio de Lima  
**v1.0.0** - Outubro 2025  
Primeira versão estável do TimeBlock Organizer CLI
