# CLI Reference - TimeBlock Organizer

**Versão:** 1.4.0

**Data:** 30 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [routine](#2-routine)
3. [habit](#3-habit)
4. [habit atom](#4-habit-atom)
5. [task](#5-task)
6. [timer](#6-timer)
7. [tag](#7-tag)
8. [report](#8-report)
9. [Validação de Flags](#9-validação-de-flags)
10. [Apêndice: Tabela de Flags](#10-apêndice-tabela-de-flags)
11. [Apêndice: Conflitos de Flags](#11-apêndice-conflitos-de-flags)
12. [Comandos Depreciados](#12-comandos-depreciados)

---

## 1. Visão Geral

### 1.1. Estrutura de Comandos

TimeBlock usa semântica **resource-first**:

```
timeblock <recurso> <ação> [argumentos] [opções]
```

**Recursos disponíveis:**

| Recurso    | Descrição                                    |
| ---------- | -------------------------------------------- |
| routine    | Gerencia rotinas (agrupamentos de hábitos)   |
| habit      | Gerencia hábitos (templates recorrentes)     |
| habit atom | Gerencia instâncias de hábitos (ocorrências) |
| task       | Gerencia tarefas (eventos únicos)            |
| timer      | Controla cronômetro                          |
| tag        | Gerencia categorias (cor + título opcional)  |
| report     | Gera relatórios de produtividade             |

### 1.2. Convenções

**Argumentos vs Opções:**

| Tipo       | Formato   | Descrição                          | Exemplo      |
| ---------- | --------- | ---------------------------------- | ------------ |
| Argumento  | `NOME`    | Posicional, geralmente obrigatório | `<HABIT_ID>` |
| Flag longa | `--opção` | Nomeada, descritiva                | `--title`    |
| Flag curta | `-o`      | Um caractere, conveniência         | `-l`         |

**Regras de flags curtas:**

- Sempre um único caractere (padrão POSIX)
- Minúsculo por padrão
- Maiúsculo para: diferenciar conflitos (-d vs -D) ou ações importantes (-P, -C)
- Flags curtas NÃO combinam valores: `-ft 2025-01-01 2025-12-31` não funciona
- Ordem das flags não importa (named arguments)

**Combinação de flags curtas:**

Flags booleanas (sem valor) podem ser combinadas:

```bash
# Equivalentes
timeblock routine list -a -v
timeblock routine list -av

# Equivalentes
timeblock habit atom list -T -P
timeblock habit atom list -TP

# Equivalentes
timeblock task list -w -C
timeblock task list -wC
```

**Restrição:** Flags que recebem valor NÃO podem ser combinadas:

```bash
# NÃO funciona (flags com valor)
timeblock habit create -se 07:00 08:30    # ERRO

# Correto
timeblock habit create -s 07:00 -e 08:30  # OK
```

**Regra geral:** Apenas a última flag da combinação pode receber valor:

```bash
timeblock habit atom list -TPh 1    # ERRO: -T e -P são booleanas, mas -h espera valor
timeblock habit atom list -TP -h 1  # OK
```

### 1.3. Formatos de Entrada

**Horário:**

| Formato | Exemplo | Resultado |
| ------- | ------- | --------- |
| HH:MM   | 07:30   | 07:30     |
| HHh     | 7h      | 07:00     |
| HHhMM   | 7h30    | 07:30     |

**Data:**

| Formato    | Exemplo    | Resultado  |
| ---------- | ---------- | ---------- |
| YYYY-MM-DD | 2025-12-01 | 2025-12-01 |
| DD/MM/YYYY | 01/12/2025 | 2025-12-01 |
| DD-MM-YYYY | 01-12-2025 | 2025-12-01 |

**Datetime (task):**

| Formato            | Exemplo            | Resultado        |
| ------------------ | ------------------ | ---------------- |
| "YYYY-MM-DD HH:MM" | "2025-12-01 14:00" | 2025-12-01 14:00 |
| "YYYY-MM-DD HHhMM" | "2025-12-01 14h00" | 2025-12-01 14:00 |
| "YYYY-MM-DD HHh"   | "2025-12-01 14h"   | 2025-12-01 14:00 |
| "DD-MM-YYYY HH:MM" | "01-12-2025 14:00" | 2025-12-01 14:00 |
| "DD-MM-YYYY HHhMM" | "01-12-2025 14h00" | 2025-12-01 14:00 |
| "DD-MM-YYYY HHh"   | "01-12-2025 14h"   | 2025-12-01 14:00 |
| "DD/MM/YYYY HH:MM" | "01/12/2025 14:00" | 2025-12-01 14:00 |
| "DD/MM/YYYY HHhMM" | "01/12/2025 14h00" | 2025-12-01 14:00 |
| "DD/MM/YYYY HHh"   | "01/12/2025 14h"   | 2025-12-01 14:00 |

**Cor:**

| Formato           | Exemplo               |
| ----------------- | --------------------- |
| Nome pré-definido | tomato, sage, peacock |
| Alias simples     | red, green, blue      |
| Hexadecimal       | #FF5733, #33B679      |

### 1.4. Cores Predefinidas

TimeBlock oferece cores nomeadas baseadas no Google Calendar.

**Nomes Descritivos:**

| Nome      | Hex     | Uso Sugerido          |
| --------- | ------- | --------------------- |
| tomato    | #D50000 | Urgente, importante   |
| flamingo  | #E67C73 | Pessoal               |
| tangerine | #F4511E | Energia, ação         |
| banana    | #F6BF26 | Atenção, destaque     |
| sage      | #33B679 | Saúde, bem-estar      |
| basil     | #0B8043 | Natureza, crescimento |
| peacock   | #039BE5 | Trabalho, foco        |
| blueberry | #3F51B5 | Estudo, aprendizado   |
| lavender  | #7986CB | Relaxamento           |
| grape     | #8E24AA | Criatividade          |
| graphite  | #616161 | Neutro                |

**Aliases Simples:**

| Alias  | Equivale a |
| ------ | ---------- |
| red    | tomato     |
| orange | tangerine  |
| yellow | banana     |
| green  | sage       |
| blue   | peacock    |
| purple | grape      |
| gray   | graphite   |

### 1.5. Enums

Valores de enum são case-insensitive no CLI:

```bash
# Ambos funcionam
timeblock habit create -r WEEKDAYS ...
timeblock habit create -r weekdays ...
```

**Internamente:** Enums são armazenados em UPPER_CASE (padrão Python/PEP 8).

---

## 2. routine

Gerencia rotinas - agrupamentos de hábitos relacionados.

**Referência:** BR-ROUTINE-001 a BR-ROUTINE-006

**Comandos disponíveis:**

| Comando            | Descrição              |
| ------------------ | ---------------------- |
| routine create     | Cria nova rotina       |
| routine edit       | Edita rotina existente |
| routine delete     | Remove rotina          |
| routine list       | Lista rotinas          |
| routine activate   | Ativa rotina           |
| routine deactivate | Desativa rotina        |

---

### 2.1. routine create

Cria nova rotina.

**Sintaxe:**

```bash
timeblock routine create <NAME>
```

**Argumentos:**

| Argumento | Tipo   | Obrigatório | Descrição                         |
| --------- | ------ | ----------- | --------------------------------- |
| NAME      | string | Sim         | Nome da rotina (1-200 caracteres) |

**Comportamento:**

| Regra                 | Descrição                                        | BR             |
| --------------------- | ------------------------------------------------ | -------------- |
| Primeira rotina ativa | Primeira rotina criada é ativada automaticamente | BR-ROUTINE-001 |
| Subsequentes inativas | Rotinas criadas depois ficam inativas            | BR-ROUTINE-001 |
| Nome único            | Nome deve ser único (case-insensitive)           | BR-ROUTINE-005 |

**Exemplos:**

```bash
timeblock routine create "Rotina Matinal"
timeblock routine create "Rotina Trabalho"
timeblock routine create "Rotina Fim de Semana"
```

**Erros possíveis:**

| Erro           | Causa                          | Mensagem                                 |
| -------------- | ------------------------------ | ---------------------------------------- |
| Nome duplicado | Já existe rotina com esse nome | "Rotina 'X' já existe"                   |
| Nome vazio     | Nome não informado             | "Nome é obrigatório"                     |
| Nome longo     | Mais de 200 caracteres         | "Nome deve ter no máximo 200 caracteres" |

---

### 2.2. routine edit

Edita rotina existente.

**Sintaxe:**

```bash
timeblock routine edit <ROUTINE_ID> [--title <TITLE>]
```

**Argumentos:**

| Argumento  | Tipo | Obrigatório | Descrição    |
| ---------- | ---- | ----------- | ------------ |
| ROUTINE_ID | int  | Sim         | ID da rotina |

**Opções:**

| Longa   | Curta | Tipo   | Obrigatório | Descrição             |
| ------- | ----- | ------ | ----------- | --------------------- |
| --title | -l    | string | Não         | Novo título da rotina |

**Exemplos:**

```bash
timeblock routine edit 1 -l "Rotina Matinal Atualizada"
timeblock routine edit 2 --title "Trabalho Remoto"
```

**Erros possíveis:**

| Erro               | Causa               | Mensagem                     |
| ------------------ | ------------------- | ---------------------------- |
| Rotina inexistente | ID não encontrado   | "Rotina ID X não encontrada" |
| Nome duplicado     | Novo nome já existe | "Rotina 'X' já existe"       |

---

### 2.3. routine delete

Remove uma rotina.

**Sintaxe:**

```bash
timeblock routine delete <ROUTINE_ID> [--purge]
```

**Argumentos:**

| Argumento  | Tipo | Obrigatório | Descrição    |
| ---------- | ---- | ----------- | ------------ |
| ROUTINE_ID | int  | Sim         | ID da rotina |

**Opções:**

| Longa   | Curta | Tipo | Obrigatório | Descrição               |
| ------- | ----- | ---- | ----------- | ----------------------- |
| --purge | (sem) | flag | Não         | Deletar permanentemente |

**Comportamento (BR-ROUTINE-006):**

| Modo                 | Ação                          | Confirmação             |
| -------------------- | ----------------------------- | ----------------------- |
| Padrão (sem --purge) | Soft delete (desativa)        | Sim, interativa         |
| Com --purge          | Hard delete (remove do banco) | Sim, interativa + aviso |

**Restrições:**

| Restrição          | Descrição                                           |
| ------------------ | --------------------------------------------------- |
| Rotina com hábitos | Não pode ser purgada. Deve deletar hábitos primeiro |
| Rotina ativa       | Pode ser deletada, sistema ativa outra se existir   |

**Fluxo interativo (--purge):**

```
$ timeblock routine delete 1 --purge

[WARN] Esta ação é irreversível!

Rotina: Rotina Matinal (ID: 1)
Hábitos vinculados: 0

Histórico de hábitos desta rotina será PERDIDO permanentemente.
Isso afetará relatórios que incluem dados desta rotina.

Tem certeza que deseja DELETAR PERMANENTEMENTE? [s/N]: _
```

**Exemplos:**

```bash
timeblock routine delete 1           # Soft delete
timeblock routine delete 1 --purge   # Hard delete
```

---

### 2.4. routine list

Lista rotinas existentes.

**Sintaxe:**

```bash
timeblock routine list [--all] [--verbose]
```

**Opções:**

| Longa     | Curta | Tipo | Obrigatório | Descrição                |
| --------- | ----- | ---- | ----------- | ------------------------ |
| --all     | -a    | flag | Não         | Incluir rotinas inativas |
| --verbose | -v    | flag | Não         | Mostrar detalhes extras  |

**Comportamento:**

| Flag      | Resultado                       |
| --------- | ------------------------------- |
| (nenhuma) | Lista apenas rotinas ativas     |
| --all     | Lista todas (ativas e inativas) |
| --verbose | Inclui contagem de hábitos      |

**Saída padrão:**

```
Rotinas:
  * 1. Rotina Matinal (ativa)
    2. Rotina Trabalho (inativa)
```

**Saída com --verbose:**

```
Rotinas:
  * 1. Rotina Matinal (ativa)
       Hábitos: 5 (3 ativos)
    2. Rotina Trabalho (inativa)
       Hábitos: 3 (0 ativos)
```

**Exemplos:**

```bash
timeblock routine list
timeblock routine list -a
timeblock routine list -v
timeblock routine list -av
```

---

### 2.5. routine activate

Ativa uma rotina.

**Sintaxe:**

```bash
timeblock routine activate <ROUTINE_ID>
```

**Argumentos:**

| Argumento  | Tipo | Obrigatório | Descrição    |
| ---------- | ---- | ----------- | ------------ |
| ROUTINE_ID | int  | Sim         | ID da rotina |

**Comportamento (BR-ROUTINE-001):**

| Regra             | Descrição                                           |
| ----------------- | --------------------------------------------------- |
| Uma ativa por vez | Apenas uma rotina pode estar ativa                  |
| Desativa anterior | Ativar rotina A desativa rotina B automaticamente   |
| Define contexto   | Rotina ativa é usada como default em comandos habit |

**Exemplo:**

```bash
timeblock routine activate 2
# Saída: Rotina "Rotina Trabalho" ativada. "Rotina Matinal" desativada.
```

---

### 2.6. routine deactivate

Desativa uma rotina.

**Sintaxe:**

```bash
timeblock routine deactivate <ROUTINE_ID>
```

**Argumentos:**

| Argumento  | Tipo | Obrigatório | Descrição    |
| ---------- | ---- | ----------- | ------------ |
| ROUTINE_ID | int  | Sim         | ID da rotina |

**Comportamento:**

| Situação          | Resultado                           |
| ----------------- | ----------------------------------- |
| Rotina já inativa | Nenhuma ação, aviso informativo     |
| Rotina ativa      | Desativa, nenhuma rotina fica ativa |

**Nota:** Sistema pode operar sem rotina ativa, mas comandos habit exigirão --routine explícito.

---

## 3. habit

Gerencia hábitos - templates de eventos recorrentes.

**Referência:** BR-HABIT-001 a BR-HABIT-005

**Comandos disponíveis:**

| Comando       | Descrição                              |
| ------------- | -------------------------------------- |
| habit create  | Cria novo hábito (template)            |
| habit edit    | Edita hábito existente                 |
| habit delete  | Remove hábito                          |
| habit list    | Lista hábitos                          |
| habit renew   | Gera mais instâncias                   |
| habit details | Mostra detalhes completos              |
| habit skip    | Wizard interativo para pular instância |

---

### 3.1. habit create

Cria novo hábito (template).

**Sintaxe:**

```bash
timeblock habit create \
  --title <TITLE> \
  --start <HH:MM> \
  --end <HH:MM> \
  --repeat <PATTERN> \
  [--color <COLOR>] \
  [--tag <TAG_ID>] \
  [--routine <ROUTINE_ID>] \
  [--renew <PERIOD> <N>]
```

**Opções obrigatórias:**

| Longa    | Curta | Tipo      | Descrição                      |
| -------- | ----- | --------- | ------------------------------ |
| --title  | -l    | string    | Título do hábito (1-200 chars) |
| --start  | -s    | time      | Hora início (HH:MM)            |
| --end    | -e    | time      | Hora fim (HH:MM)               |
| --repeat | (sem) | enum/list | Padrão de repetição            |

**Opções opcionais:**

| Longa     | Curta | Tipo       | Default  | Descrição           |
| --------- | ----- | ---------- | -------- | ------------------- |
| --color   | -c    | string     | (nenhum) | Cor (nome ou hex)   |
| --tag     | -g    | int        | (nenhum) | ID da tag existente |
| --routine | -R    | int        | ativa    | ID da rotina        |
| --renew   | -n    | period int | month 3  | Período de geração  |

**Padrões de repetição (BR-HABIT-002):**

| Valor     | Descrição        | Dias                        |
| --------- | ---------------- | --------------------------- |
| MONDAY    | Apenas segundas  | seg                         |
| TUESDAY   | Apenas terças    | ter                         |
| WEDNESDAY | Apenas quartas   | qua                         |
| THURSDAY  | Apenas quintas   | qui                         |
| FRIDAY    | Apenas sextas    | sex                         |
| SATURDAY  | Apenas sábados   | sáb                         |
| SUNDAY    | Apenas domingos  | dom                         |
| WEEKDAYS  | Dias úteis       | seg-sex                     |
| WEEKENDS  | Fim de semana    | sáb-dom                     |
| EVERYDAY  | Todos os dias    | seg-dom                     |
| LISTA     | Dias específicos | ex: MONDAY,WEDNESDAY,FRIDAY |

**Períodos de renovação:**

| Período    | Descrição             | Exemplo       |
| ---------- | --------------------- | ------------- |
| week N     | Próximas N semanas    | -n week 4     |
| month N    | Próximos N meses      | -n month 3    |
| quarter N  | Próximos N trimestres | -n quarter 2  |
| semester N | Próximos N semestres  | -n semester 1 |
| year N     | Próximos N anos       | -n year 1     |

**Comportamento de --renew:**

| Cenário      | Resultado                      |
| ------------ | ------------------------------ |
| Omitido      | Usa default: month 3 (3 meses) |
| Especificado | SUBSTITUI o default (não soma) |

**Validações (BR-CLI-001):**

| Validação       | Regra                                |
| --------------- | ------------------------------------ |
| --start/--end   | Par obrigatório (ambos ou nenhum)    |
| --color/--tag   | Mutuamente exclusivos                |
| --start < --end | Hora início deve ser menor que fim   |
| Rotina existe   | Se --routine informado, deve existir |

**Exemplos:**

```bash
# Básico (gera 3 meses por default)
timeblock habit create \
  -l "Academia" \
  -s 07:00 \
  -e 08:30 \
  --repeat WEEKDAYS

# Com cor e renovação customizada
timeblock habit create \
  -l "Meditação" \
  -s 06:00 \
  -e 06:20 \
  --repeat EVERYDAY \
  -c sage \
  -n month 6

# Dias específicos com tag
timeblock habit create \
  -l "Inglês" \
  -s 19:00 \
  -e 20:00 \
  --repeat MONDAY,WEDNESDAY,FRIDAY \
  -g 1 \
  -n week 8

# Em rotina específica
timeblock habit create \
  -l "Reunião Semanal" \
  -s 10:00 \
  -e 11:00 \
  --repeat MONDAY \
  -R 2
```

---

### 3.2. habit edit

Edita hábito (template) existente.

**Sintaxe:**

```bash
timeblock habit edit <HABIT_ID> \
  [--title <TITLE>] \
  [--start <HH:MM>] \
  [--end <HH:MM>] \
  [--repeat <PATTERN>] \
  [--color <COLOR>] \
  [--tag <TAG_ID>]
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| HABIT_ID  | int  | Sim         | ID do hábito |

**Opções:**

| Longa    | Curta | Tipo      | Descrição        |
| -------- | ----- | --------- | ---------------- |
| --title  | -l    | string    | Novo título      |
| --start  | -s    | time      | Nova hora início |
| --end    | -e    | time      | Nova hora fim    |
| --repeat | (sem) | enum/list | Novo padrão      |
| --color  | -c    | string    | Nova cor         |
| --tag    | -g    | int       | Nova tag         |

**Comportamento (BR-HABIT-004):**

| Instâncias      | Ação                               |
| --------------- | ---------------------------------- |
| PENDING futuras | Atualizadas com novos valores      |
| DONE            | Não alteradas (preserva histórico) |
| NOT_DONE        | Não alteradas (preserva histórico) |

**Comportamento especial de --repeat:**

| Cenário       | Resultado                                           |
| ------------- | --------------------------------------------------- |
| Adiciona dias | Gera novas instâncias para dias adicionados         |
| Remove dias   | Instâncias PENDING dos dias removidos são deletadas |
| Mantém dias   | Instâncias existentes preservadas                   |

**Exemplos:**

```bash
timeblock habit edit 1 -l "Academia Matinal"
timeblock habit edit 1 -s 06:30 -e 08:00
timeblock habit edit 1 --repeat EVERYDAY
timeblock habit edit 1 -c blueberry
```

---

### 3.3. habit delete

Remove hábito (template).

**Sintaxe:**

```bash
timeblock habit delete <HABIT_ID>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| HABIT_ID  | int  | Sim         | ID do hábito |

**Comportamento (BR-HABIT-005):**

| Item                     | Ação                                       |
| ------------------------ | ------------------------------------------ |
| Confirmação              | Interativa obrigatória                     |
| Instâncias PENDING       | Removidas                                  |
| Instâncias DONE/NOT_DONE | Preservadas para histórico                 |
| Relatórios               | Continuam funcionando com dados históricos |

**Fluxo interativo:**

```
$ timeblock habit delete 1

Hábito: Academia (ID: 1)
Instâncias pendentes: 45
Instâncias concluídas: 18

Instâncias pendentes serão removidas.
Histórico será preservado para relatórios.

Confirma exclusão? [s/N]: _
```

---

### 3.4. habit list

Lista hábitos (templates).

**Sintaxe:**

```bash
timeblock habit list [--routine <FILTER>] [--verbose]
```

**Opções:**

| Longa     | Curta | Tipo       | Default | Descrição        |
| --------- | ----- | ---------- | ------- | ---------------- |
| --routine | -R    | string/int | active  | Filtro de rotina |
| --verbose | -v    | flag       | false   | Mostrar detalhes |

**Valores de --routine:**

| Valor      | Resultado                         |
| ---------- | --------------------------------- |
| active     | Hábitos da rotina ativa (default) |
| all        | Hábitos de todas as rotinas       |
| N (número) | Hábitos da rotina com ID N        |

**Saída padrão:**

```
Hábitos (Rotina Matinal):
  1. Academia (07:00-08:30) WEEKDAYS
  2. Meditação (06:00-06:20) EVERYDAY
  3. Leitura (21:00-22:00) EVERYDAY
```

**Saída com --verbose:**

```
Hábitos (Rotina Matinal):
  1. Academia (07:00-08:30) WEEKDAYS
     Cor: sage | Instâncias: 45 pendentes, 18 concluídas
  2. Meditação (06:00-06:20) EVERYDAY
     Cor: lavender | Instâncias: 60 pendentes, 30 concluídas
```

**Exemplos:**

```bash
timeblock habit list              # Rotina ativa
timeblock habit list -R all       # Todas rotinas
timeblock habit list -R 2         # Rotina ID 2
timeblock habit list -v           # Com detalhes
timeblock habit list -R all -v    # Todas com detalhes
```

---

### 3.5. habit renew

Renova instâncias de um hábito.

**Sintaxe:**

```bash
timeblock habit renew <HABIT_ID> <PERIOD> <N>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição                            |
| --------- | ---- | ----------- | ------------------------------------ |
| HABIT_ID  | int  | Sim         | ID do hábito                         |
| PERIOD    | enum | Sim         | week, month, quarter, semester, year |
| N         | int  | Sim         | Quantidade de períodos               |

**Comportamento:**

| Regra            | Descrição                                         |
| ---------------- | ------------------------------------------------- |
| A partir de hoje | Gera instâncias de hoje em diante                 |
| Sem duplicação   | Não cria instâncias em datas já existentes        |
| Notificação      | Sistema notifica quando instâncias estão acabando |

**Exemplos:**

```bash
timeblock habit renew 1 month 3    # Próximos 3 meses
timeblock habit renew 1 week 4     # Próximas 4 semanas
timeblock habit renew 1 quarter 1  # Próximo trimestre
timeblock habit renew 1 year 1     # Próximo ano
```

**Saída:**

```
$ timeblock habit renew 1 month 3

Hábito: Academia
Período: 01/12/2025 a 28/02/2026
Instâncias criadas: 39
Instâncias já existentes (ignoradas): 6
Total de instâncias pendentes: 45
```

---

### 3.6. habit details

Mostra detalhes completos de um hábito.

**Sintaxe:**

```bash
timeblock habit details <HABIT_ID>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| HABIT_ID  | int  | Sim         | ID do hábito |

**Saída:**

```
$ timeblock habit details 1

Hábito: Academia (ID: 1)
========================================

Configuração:
  Rotina: Rotina Matinal
  Horário: 07:00 - 08:30 (1h30min)
  Repetição: WEEKDAYS (seg-sex)
  Cor: sage (#33B679)
  Tag: Saúde

Instâncias:
  Primeira: 2025-01-01
  Última: 2025-03-31
  Total: 65
    - Pendentes: 45
    - Concluídas: 18
    - Puladas: 2

Estatísticas:
  Taxa de conclusão: 90%
  Streak atual: 5 dias
  Streak recorde: 12 dias
  Tempo médio: 1h25min

Próximas 5 instâncias:
  2025-12-02 (seg) 07:00-08:30
  2025-12-03 (ter) 07:00-08:30
  2025-12-04 (qua) 07:00-08:30
  2025-12-05 (qui) 07:00-08:30
  2025-12-06 (sex) 07:00-08:30
```

---

### 3.7. habit skip

Wizard interativo para pular instância de hábito.

**Sintaxe:**

```bash
timeblock habit skip
```

**Comportamento:**

Este comando oferece um fluxo interativo completo:

1. Lista instâncias pendentes de hoje
2. Usuário escolhe qual pular
3. Apresenta menu de motivos
4. Registra o skip

**Fluxo interativo:**

```
$ timeblock habit skip

Instâncias pendentes hoje:

[1] Academia (07:00-08:30)
[2] Meditação (06:00-06:20)
[3] Leitura (21:00-22:00)

Qual deseja pular? [1-3]: 1

Por que você está pulando Academia hoje?

[1] Saúde
[2] Trabalho
[3] Família
[4] Viagem
[5] Clima
[6] Falta de recursos
[7] Emergência
[8] Outro
[9] Sem justificativa

Escolha [1-9]: 1

Deseja adicionar uma nota? (Enter para pular): Dor nas costas

[OK] Academia pulada (motivo: Saúde)
```

**Nota:** Para pular instância específica sem wizard, use `habit atom skip <INSTANCE_ID>`.

---

## 4. habit atom

Gerencia instâncias de hábitos - ocorrências em datas específicas.

**Referência:** BR-HABITINSTANCE-001 a BR-HABITINSTANCE-005

**Comandos disponíveis:**

| Comando           | Descrição                  |
| ----------------- | -------------------------- |
| habit atom create | Cria instância avulsa      |
| habit atom edit   | Edita instância específica |
| habit atom delete | Remove instância           |
| habit atom list   | Lista instâncias           |
| habit atom skip   | Pula instância             |
| habit atom log    | Registra tempo manualmente |

---

### 4.1. habit atom create

Cria instância avulsa de um hábito.

**Sintaxe:**

```bash
timeblock habit atom create <HABIT_ID> \
  --date <DATE> \
  --start <HH:MM> \
  --end <HH:MM>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição               |
| --------- | ---- | ----------- | ----------------------- |
| HABIT_ID  | int  | Sim         | ID do hábito (template) |

**Opções obrigatórias:**

| Longa   | Curta | Tipo | Descrição         |
| ------- | ----- | ---- | ----------------- |
| --date  | -d    | date | Data da instância |
| --start | -s    | time | Hora início       |
| --end   | -e    | time | Hora fim          |

**Uso:** Criar instância em dia que não faz parte da recorrência padrão.

**Exemplo:**

```bash
# Academia é WEEKDAYS, mas quero treinar no sábado
timeblock habit atom create 1 -d 2025-12-06 -s 10:00 -e 11:30
```

**Validações:**

| Validação      | Regra                                                               |
| -------------- | ------------------------------------------------------------------- |
| Hábito existe  | HABIT_ID deve existir                                               |
| Data válida    | Formato aceito                                                      |
| Horário válido | --start < --end                                                     |
| Sem duplicata  | Não pode existir outra instância do mesmo hábito na mesma data/hora |

---

### 4.2. habit atom edit

Edita instância específica.

**Sintaxe:**

```bash
timeblock habit atom edit <INSTANCE_ID> \
  [--date <DATE>] \
  [--start <HH:MM>] \
  [--end <HH:MM>]
```

**Argumentos:**

| Argumento   | Tipo | Obrigatório | Descrição       |
| ----------- | ---- | ----------- | --------------- |
| INSTANCE_ID | int  | Sim         | ID da instância |

**Opções:**

| Longa   | Curta | Tipo | Descrição        |
| ------- | ----- | ---- | ---------------- |
| --date  | -d    | date | Nova data        |
| --start | -s    | time | Nova hora início |
| --end   | -e    | time | Nova hora fim    |

**Comportamento (BR-HABITINSTANCE-005):**

| Regra               | Descrição                             |
| ------------------- | ------------------------------------- |
| Apenas instância    | Afeta apenas a instância especificada |
| Não altera template | Habit original permanece inalterado   |
| Detecta conflitos   | Sistema avisa se houver sobreposição  |

**Restrições:**

| Campo   | Editável? | Motivo            |
| ------- | --------- | ----------------- |
| --date  | Sim       | Reagendar         |
| --start | Sim       | Ajustar horário   |
| --end   | Sim       | Ajustar horário   |
| --title | Não       | Herda do template |
| --tag   | Não       | Herda do template |
| --color | Não       | Herda do template |

**Exemplos:**

```bash
timeblock habit atom edit 42 -d 2025-12-03
timeblock habit atom edit 42 -s 08:00 -e 09:30
timeblock habit atom edit 42 -d 2025-12-03 -s 08:00 -e 09:30
```

---

### 4.3. habit atom delete

Remove instância específica.

**Sintaxe:**

```bash
timeblock habit atom delete <INSTANCE_ID>
```

**Argumentos:**

| Argumento   | Tipo | Obrigatório | Descrição       |
| ----------- | ---- | ----------- | --------------- |
| INSTANCE_ID | int  | Sim         | ID da instância |

**Comportamento:**

| Item        | Ação                                   |
| ----------- | -------------------------------------- |
| Confirmação | Interativa                             |
| Scope       | Remove apenas a instância especificada |
| Template    | Não é afetado                          |

---

### 4.4. habit atom list

Lista instâncias de hábitos.

**Sintaxe:**

```bash
timeblock habit atom list [<HABIT_ID>] \
  [--today] [--week] \
  [--pending] [--done] [--all]
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição          |
| --------- | ---- | ----------- | ------------------ |
| HABIT_ID  | int  | Não         | Filtrar por hábito |

**Opções de período (mutuamente exclusivas):**

| Longa   | Curta | Descrição    |
| ------- | ----- | ------------ |
| --today | -T    | Apenas hoje  |
| --week  | -w    | Semana atual |

**Opções de status:**

| Longa     | Curta | Descrição              |
| --------- | ----- | ---------------------- |
| --pending | -P    | Apenas PENDING         |
| --done    | -C    | Apenas DONE (complete) |
| --all     | -a    | Todos status           |

**Defaults:**

| Cenário         | Período     | Status       |
| --------------- | ----------- | ------------ |
| Sem flags       | --week      | --pending    |
| Apenas HABIT_ID | Todas datas | Todos status |

**Combinações válidas:**

```bash
timeblock habit atom list                   # Semana, pendentes (default)
timeblock habit atom list 1                 # Todas do hábito 1
timeblock habit atom list -T                # Hoje, todos status
timeblock habit atom list -T -C             # Hoje, completadas
timeblock habit atom list 1 -w -P           # Hábito 1, semana, pendentes
timeblock habit atom list -T -a             # Hoje, todos status
```

**Saída:**

```
Instâncias (semana atual):

Segunda, 02/12:
  [ ] 07:00-08:30 Academia (pendente)
  [x] 06:00-06:20 Meditação (concluída)

Terça, 03/12:
  [ ] 07:00-08:30 Academia (pendente)
  [ ] 06:00-06:20 Meditação (pendente)
```

---

### 4.5. habit atom skip

Pula uma instância de hábito.

**Sintaxe:**

```bash
timeblock habit atom skip <INSTANCE_ID> \
  [--reason <REASON>] \
  [--note <NOTE>]
```

**Argumentos:**

| Argumento   | Tipo | Obrigatório | Descrição       |
| ----------- | ---- | ----------- | --------------- |
| INSTANCE_ID | int  | Sim         | ID da instância |

**Opções:**

| Longa    | Curta | Tipo   | Descrição                     |
| -------- | ----- | ------ | ----------------------------- |
| --reason | -r    | enum   | Categoria do skip             |
| --note   | (sem) | string | Nota opcional (máx 500 chars) |

**Comportamento (BR-SKIP-001 a BR-SKIP-004):**

| Cenário            | Status resultante   |
| ------------------ | ------------------- |
| Sem opções         | Menu interativo     |
| Com --reason (1-8) | SKIPPED_JUSTIFIED   |
| Opção 9 no menu    | SKIPPED_UNJUSTIFIED |

**Impacto em streak (BR-STREAK-002):**

| Status              | Streak        |
| ------------------- | ------------- |
| SKIPPED_JUSTIFIED   | Quebra streak |
| SKIPPED_UNJUSTIFIED | Quebra streak |

**Categorias predefinidas:**

| Valor | Código         | Descrição                    |
| ----- | -------------- | ---------------------------- |
| 1     | HEALTH         | Saúde (doença, consulta)     |
| 2     | WORK           | Trabalho (reunião, deadline) |
| 3     | FAMILY         | Família (evento, emergência) |
| 4     | TRAVEL         | Viagem/Deslocamento          |
| 5     | WEATHER        | Clima (chuva, frio)          |
| 6     | LACK_RESOURCES | Falta de recursos            |
| 7     | EMERGENCY      | Emergências                  |
| 8     | OTHER          | Outros (com nota)            |
| 9     | (unjustified)  | Sem justificativa            |

**Fluxo interativo (sem opções):**

```
$ timeblock habit atom skip 42

Por que você está pulando Academia hoje?

[1] Saúde
[2] Trabalho
[3] Família
[4] Viagem
[5] Clima
[6] Falta de recursos
[7] Emergência
[8] Outro
[9] Sem justificativa

Escolha [1-9]: _
```

**Exemplos:**

```bash
# Com categoria direta
timeblock habit atom skip 42 -r HEALTH

# Com categoria e nota
timeblock habit atom skip 42 -r HEALTH --note "Dor nas costas"

# Menu interativo
timeblock habit atom skip 42
```

---

### 4.6. habit atom log

Registra tempo manualmente (sem usar timer).

**Sintaxe:**

```bash
# Modo intervalo
timeblock habit atom log <INSTANCE_ID> \
  --start <HH:MM> \
  --end <HH:MM>

# Modo duração
timeblock habit atom log <INSTANCE_ID> \
  --duration <MINUTES>
```

**Argumentos:**

| Argumento   | Tipo | Obrigatório | Descrição       |
| ----------- | ---- | ----------- | --------------- |
| INSTANCE_ID | int  | Sim         | ID da instância |

**Opções (mutuamente exclusivas):**

| Longa      | Curta | Tipo | Descrição          |
| ---------- | ----- | ---- | ------------------ |
| --start    | -s    | time | Hora início        |
| --end      | -e    | time | Hora fim           |
| --duration | -d    | int  | Duração em minutos |

**Validação (BR-CLI-001):**

| Modo      | Regra                               |
| --------- | ----------------------------------- |
| Intervalo | --start E --end obrigatórios juntos |
| Duração   | Apenas --duration                   |
| Misto     | ERRO: não pode combinar             |

**Comportamento (BR-TIMER-007):**

| Ação              | Descrição                       |
| ----------------- | ------------------------------- |
| Cria TimeLog      | Registro de tempo sem timer     |
| Calcula substatus | FULL/PARTIAL/OVERDONE/EXCESSIVE |
| Marca DONE        | Instância vira DONE             |

**Cálculo de substatus:**

| Substatus | Condição                             |
| --------- | ------------------------------------ |
| PARTIAL   | Tempo < 80% do planejado             |
| FULL      | Tempo entre 80% e 120% do planejado  |
| OVERDONE  | Tempo entre 120% e 150% do planejado |
| EXCESSIVE | Tempo > 150% do planejado            |

**Exemplos:**

```bash
# Modo intervalo
timeblock habit atom log 42 -s 07:15 -e 08:20

# Modo duração
timeblock habit atom log 42 -d 65
```

**Saída:**

```
$ timeblock habit atom log 42 -s 07:15 -e 08:20

Hábito: Academia
Tempo planejado: 1h30min
Tempo registrado: 1h05min
Substatus: PARTIAL (72%)

[OK] Tempo registrado. Instância marcada como concluída.
```

---

## 5. task

Gerencia tarefas - eventos únicos não-recorrentes.

**Referência:** BR-TASK-001 a BR-TASK-006

**Comandos disponíveis:**

| Comando       | Descrição              |
| ------------- | ---------------------- |
| task create   | Cria nova tarefa       |
| task edit     | Edita tarefa existente |
| task delete   | Remove tarefa          |
| task list     | Lista tarefas          |
| task complete | Marca como concluída   |
| task uncheck  | Reverte para pendente  |

---

### 5.1. task create

Cria nova tarefa.

**Sintaxe:**

```bash
timeblock task create \
  --title <TITLE> \
  --datetime <DATETIME> \
  [--desc <DESC>] \
  [--color <COLOR>] \
  [--tag <TAG_ID>]
```

**Opções obrigatórias:**

| Longa      | Curta | Tipo     | Descrição                      |
| ---------- | ----- | -------- | ------------------------------ |
| --title    | -l    | string   | Título da tarefa (1-200 chars) |
| --datetime | -D    | datetime | Data e hora                    |

**Opções opcionais:**

| Longa   | Curta | Tipo   | Descrição                  |
| ------- | ----- | ------ | -------------------------- |
| --desc  | (sem) | string | Descrição (máx 2000 chars) |
| --color | -c    | string | Cor (nome ou hex)          |
| --tag   | -g    | int    | ID da tag existente        |

**Formato de --datetime:**

| Formato     | Exemplo            | Resultado                  |
| ----------- | ------------------ | -------------------------- |
| Data + hora | "2025-12-01 14:30" | Evento com horário         |
| Apenas data | "2025-12-01"       | Dia inteiro (CLI confirma) |

**Fluxo para dia inteiro:**

```
$ timeblock task create -l "Feriado" -D "2025-12-25"

Nenhum horário informado. É um evento de dia inteiro? [S/n]: _
```

**Validações:**

| Validação     | Regra                 |
| ------------- | --------------------- |
| --color/--tag | Mutuamente exclusivos |
| --datetime    | Formato válido        |
| --title       | 1-200 caracteres      |
| --desc        | Máx 2000 caracteres   |

**Exemplos:**

```bash
# Com horário
timeblock task create -l "Dentista" -D "2025-12-01 14:30"

# Dia inteiro
timeblock task create -l "Feriado" -D "2025-12-25"

# Com descrição e cor
timeblock task create \
  -l "Reunião importante" \
  -D "2025-12-02 10:00" \
  --desc "Apresentar relatório trimestral" \
  -c tomato
```

---

### 5.2. task edit

Edita tarefa existente.

**Sintaxe:**

```bash
timeblock task edit <TASK_ID> \
  [--title <TITLE>] \
  [--datetime <DATETIME>] \
  [--desc <DESC>] \
  [--color <COLOR>] \
  [--tag <TAG_ID>]
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| TASK_ID   | int  | Sim         | ID da tarefa |

**Opções:**

| Longa      | Curta | Tipo     | Descrição                  |
| ---------- | ----- | -------- | -------------------------- |
| --title    | -l    | string   | Novo título                |
| --datetime | -D    | datetime | Nova data/hora             |
| --desc     | (sem) | string   | Nova descrição             |
| --color    | -c    | string   | Nova cor                   |
| --tag      | -g    | int      | Nova tag                   |
| --status   | (sem) | enum     | Novo status (pending/done) |

**Restrição (BR-TASK-005):**

| Status    | Editável?                       |
| --------- | ------------------------------- |
| Pendente  | Sim (todos os campos)           |
| Concluída | Apenas --status (para reverter) |

**Erro se concluída (campos não-status):**

```
[ERROR] Tarefa já concluída. Use --status pending para reabrir antes de editar.
```

**Exemplos:**

```bash
timeblock task edit 1 -l "Dentista - Limpeza"
timeblock task edit 1 -D "2025-12-02 15:00"
timeblock task edit 1 -c blueberry
```

**Uso de --status:**

```bash
timeblock task edit 1 --status pending   # Reverte para pendente
timeblock task edit 1 --status done      # Marca como concluída
```

---

### 5.3. task delete

Remove tarefa.

**Sintaxe:**

```bash
timeblock task delete <TASK_ID>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| TASK_ID   | int  | Sim         | ID da tarefa |

**Comportamento:**

| Item             | Ação              |
| ---------------- | ----------------- |
| Confirmação      | Interativa        |
| Tarefa concluída | Pode ser deletada |

---

### 5.4. task list

Lista tarefas.

**Sintaxe:**

```bash
timeblock task list \
  [--today] [--week] \
  [--pending] [--done] [--all]
```

**Opções de período (mutuamente exclusivas):**

| Longa   | Curta | Descrição    |
| ------- | ----- | ------------ |
| --today | -T    | Apenas hoje  |
| --week  | -w    | Semana atual |

**Opções de status:**

| Longa     | Curta | Descrição         |
| --------- | ----- | ----------------- |
| --pending | -P    | Apenas pendentes  |
| --done    | -C    | Apenas concluídas |
| --all     | -a    | Todas             |

**Default:** --pending (sem flags)

**Combinações válidas:**

```bash
timeblock task list                 # Pendentes (default)
timeblock task list -T              # Hoje, todos status
timeblock task list -w -C           # Semana, concluídas
timeblock task list -a              # Todas
timeblock task list -T -P           # Hoje, pendentes
```

**Saída:**

```
Tarefas pendentes:

Hoje, 01/12:
  [ ] 14:30 Dentista
  [ ] (dia inteiro) Pagar contas

Amanhã, 02/12:
  [ ] 10:00 Reunião importante
```

---

### 5.5. task complete

Marca tarefa como concluída.

**Sintaxe:**

```bash
timeblock task complete <TASK_ID>
```

**Aliases:** `task check`, `task done`

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| TASK_ID   | int  | Sim         | ID da tarefa |

**Comportamento (BR-TASK-002):**

| Ação      | Descrição                                     |
| --------- | --------------------------------------------- |
| Timestamp | Define `completed_datetime` com momento atual |
| Status    | Tarefa sai da lista de pendentes              |

**Exemplos:**

```bash
timeblock task complete 1
timeblock task check 1      # Alias
timeblock task done 1       # Alias
```

---

### 5.6. task uncheck

Reverte tarefa concluída para pendente.

**Sintaxe:**

```bash
timeblock task uncheck <TASK_ID>
```

**Alias:** `task reopen`

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição    |
| --------- | ---- | ----------- | ------------ |
| TASK_ID   | int  | Sim         | ID da tarefa |

**Comportamento:**

| Ação      | Descrição                            |
| --------- | ------------------------------------ |
| Timestamp | Remove `completed_datetime` (= null) |
| Status    | Tarefa volta para lista de pendentes |

**Uso:** Corrigir marcação acidental ou reabrir tarefa.

**Exemplos:**

```bash
timeblock task uncheck 1
timeblock task reopen 1     # Alias
```

**Equivalente:**

```bash
timeblock task edit 1 --status pending
```

---

## 6. timer

Controla cronômetro para rastrear tempo.

**Referência:** BR-TIMER-001 a BR-TIMER-006

**Comandos disponíveis:**

| Comando      | Descrição           |
| ------------ | ------------------- |
| timer start  | Inicia cronômetro   |
| timer pause  | Pausa cronômetro    |
| timer resume | Retoma cronômetro   |
| timer stop   | Para e salva        |
| timer reset  | Cancela sem salvar  |
| timer status | Mostra status atual |

---

### 6.1. timer start

Inicia cronômetro.

**Sintaxe:**

```bash
timeblock timer start <INSTANCE_ID>
```

**Argumentos:**

| Argumento   | Tipo | Obrigatório | Descrição                 |
| ----------- | ---- | ----------- | ------------------------- |
| INSTANCE_ID | int  | Sim         | ID da instância de hábito |

**Comportamento (BR-TIMER-001):**

| Regra             | Descrição                              |
| ----------------- | -------------------------------------- |
| Um timer por vez  | Apenas um timer ativo simultaneamente  |
| Timer ativo       | Se já houver, exibe menu de opções     |
| Múltiplas sessões | Instância DONE pode iniciar novo timer |

**Fluxo com timer ativo:**

```
$ timeblock timer start 43

[ERROR] Timer já ativo: Academia (15min decorridos)

Opções:
  [1] Pausar Academia e iniciar Meditação
  [2] Cancelar Academia (reset) e iniciar Meditação
  [3] Continuar com Academia

Escolha [1-3]: _
```

**Exemplo:**

```bash
timeblock timer start 42
# Saída: [OK] Timer iniciado: Academia (07:00-08:30)
```

---

### 6.2. timer pause

Pausa cronômetro ativo.

**Sintaxe:**

```bash
timeblock timer pause
```

**Comportamento (BR-TIMER-002):**

| Item         | Descrição                      |
| ------------ | ------------------------------ |
| Transição    | RUNNING => PAUSED              |
| Rastreamento | Tempo de pausa é contabilizado |

**Saída:**

```
$ timeblock timer pause

[OK] Timer pausado: Academia
Tempo decorrido: 00:15:30
```

---

### 6.3. timer resume

Retoma cronômetro pausado.

**Sintaxe:**

```bash
timeblock timer resume
```

**Comportamento (BR-TIMER-002):**

| Item       | Descrição                        |
| ---------- | -------------------------------- |
| Transição  | PAUSED => RUNNING                |
| Acumulação | Tempo de pausa é somado ao total |

**Saída:**

```
$ timeblock timer resume

[OK] Timer retomado: Academia
Tempo pausado total: 00:05:00
```

---

### 6.4. timer stop

Para cronômetro e salva registro.

**Sintaxe:**

```bash
timeblock timer stop
```

**Comportamento (BR-TIMER-003):**

| Ação                | Descrição                                   |
| ------------------- | ------------------------------------------- |
| Fecha sessão        | Encerra timer atual                         |
| Salva               | Cria registro TimeLog no banco              |
| Calcula substatus   | FULL/PARTIAL/OVERDONE/EXCESSIVE             |
| Marca DONE          | Instância vira DONE                         |
| Permite nova sessão | Pode iniciar outro timer na mesma instância |

**Saída:**

```
$ timeblock timer stop

[OK] Timer finalizado: Academia

Tempo planejado: 1h30min
Tempo trabalhado: 1h25min
Tempo pausado: 5min
Substatus: FULL (94%)

Instância marcada como concluída.
```

---

### 6.5. timer reset

Cancela cronômetro sem salvar.

**Sintaxe:**

```bash
timeblock timer reset
```

**Alias:** `timer cancel`

**Comportamento (BR-TIMER-003):**

| Ação      | Descrição                    |
| --------- | ---------------------------- |
| Descarta  | Sessão atual NÃO é salva     |
| Instância | Permanece PENDING            |
| Uso       | Quando iniciou hábito errado |

**Fluxo interativo:**

```
$ timeblock timer reset

Timer ativo: Academia (25min decorridos)

Tem certeza que deseja cancelar? O tempo NÃO será salvo. [s/N]: _
```

---

### 6.6. timer status

Mostra status do cronômetro atual.

**Sintaxe:**

```bash
timeblock timer status
```

**Saída (timer ativo):**

```
$ timeblock timer status

Timer ativo: Academia
========================================
Status: RUNNING
Tempo decorrido: 00:45:30
Tempo planejado: 01:30:00
Tempo pausado: 00:05:00
Progresso: 50%
```

**Saída (sem timer):**

```
$ timeblock timer status

Nenhum timer ativo.
```

---

## 7. tag

Gerencia categorias - cor com título opcional.

**Comandos disponíveis:**

| Comando    | Descrição           |
| ---------- | ------------------- |
| tag create | Cria nova tag       |
| tag edit   | Edita tag existente |
| tag delete | Remove tag          |
| tag list   | Lista tags          |

---

### 7.1. tag create

Cria nova tag.

**Sintaxe:**

```bash
timeblock tag create [--title <TITLE>] [--color <COLOR>]
```

**Opções:**

| Longa   | Curta | Tipo   | Default  | Descrição         |
| ------- | ----- | ------ | -------- | ----------------- |
| --title | -l    | string | (nenhum) | Título da tag     |
| --color | -c    | string | banana   | Cor (nome ou hex) |

**Comportamento:**

| Regra            | Descrição                             |
| ---------------- | ------------------------------------- |
| Cor obrigatória  | Assume default se não informada       |
| Título opcional  | Tag anônima se omitido                |
| Compartilhamento | Múltiplos habits podem usar mesma tag |

**Exemplos:**

```bash
timeblock tag create -c green                 # Tag anônima verde
timeblock tag create -l "Estudo" -c blueberry # Tag nomeada
timeblock tag create -l "Saúde" -c sage
timeblock tag create                          # Tag anônima, cor banana
```

---

### 7.2. tag edit

Edita tag existente.

**Sintaxe:**

```bash
timeblock tag edit <TAG_ID> \
  [--title <TITLE>] \
  [--color <COLOR>]
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição |
| --------- | ---- | ----------- | --------- |
| TAG_ID    | int  | Sim         | ID da tag |

**Opções:**

| Longa   | Curta | Tipo   | Descrição   |
| ------- | ----- | ------ | ----------- |
| --title | -l    | string | Novo título |
| --color | -c    | string | Nova cor    |

**Uso comum:** Nomear tag anônima posteriormente.

**Exemplos:**

```bash
timeblock tag edit 1 -l "Trabalho"
timeblock tag edit 1 -c peacock
timeblock tag edit 1 -l "Trabalho" -c peacock
```

---

### 7.3. tag delete

Remove tag.

**Sintaxe:**

```bash
timeblock tag delete <TAG_ID>
```

**Argumentos:**

| Argumento | Tipo | Obrigatório | Descrição |
| --------- | ---- | ----------- | --------- |
| TAG_ID    | int  | Sim         | ID da tag |

**Comportamento:**

| Item              | Ação                          |
| ----------------- | ----------------------------- |
| Confirmação       | Interativa                    |
| Habits vinculados | Ficam sem tag (tag_id = null) |

---

### 7.4. tag list

Lista tags existentes.

**Sintaxe:**

```bash
timeblock tag list
```

**Saída:**

```
Tags:
  1. Estudo (#3F51B5)
  2. Saúde (#33B679)
  3. Trabalho (#039BE5)
  4. (sem título) (#F6BF26)
```

---

## 8. report

Gera relatórios de produtividade.

**Nota:** O subcomando `view` é o default. Pode ser omitido.

**Comandos disponíveis:**

| Comando       | Descrição       |
| ------------- | --------------- |
| report [view] | Exibe relatório |

---

### 8.1. report [view]

Exibe relatório de produtividade.

**Sintaxe:**

```bash
timeblock report [view] \
  [--week] [--month] [--quarter] [--semester] [--year] \
  [--from <DATE>] [--to <DATE>] \
  [--habit <HABIT_ID>] \
  [--verbose]
```

**Opções de período (mutuamente exclusivas):**

| Longa      | Curta | Descrição           |
| ---------- | ----- | ------------------- |
| --week     | -w    | Semana atual        |
| --month    | -m    | Mês atual (default) |
| --quarter  | -q    | Trimestre atual     |
| --semester | (sem) | Semestre atual      |
| --year     | -y    | Ano atual           |
| --from     | -f    | Data início (range) |
| --to       | -t    | Data fim (range)    |

**Opções de filtro:**

| Longa     | Curta | Descrição          |
| --------- | ----- | ------------------ |
| --habit   | -h    | Filtrar por hábito |
| --verbose | -v    | Detalhes extras    |

**Validação:**

| Regra       | Descrição                         |
| ----------- | --------------------------------- |
| --from/--to | Par obrigatório (ambos ou nenhum) |
| Períodos    | Mutuamente exclusivos             |

**Default:** --month (mês atual)

**Saída padrão:**

```
$ timeblock report

Relatório: Dezembro 2025
========================================

Resumo Geral:
  Taxa de conclusão: 85%
  Hábitos rastreados: 5
  Tempo total: 45h 30min

Por Hábito:
  Academia
    Conclusão: 90% (18/20)
    Streak atual: 5 dias
    Tempo médio: 1h25min

  Meditação
    Conclusão: 95% (28/30)
    Streak atual: 12 dias
    Tempo médio: 18min

Distribuição por Substatus:
  FULL: 70%
  PARTIAL: 20%
  OVERDONE: 8%
  EXCESSIVE: 2%
```

**Exemplos:**

```bash
timeblock report                    # Mês atual (view implícito)
timeblock report view               # Mês atual (view explícito)
timeblock report -w                 # Semana atual
timeblock report -q                 # Trimestre atual
timeblock report -f 2025-01-01 -t 2025-06-30
timeblock report -m -h 1            # Mês + hábito específico
timeblock report -v                 # Com detalhes extras
```

---

## 9. Validação de Flags

Esta seção documenta as regras de validação de flags (BR-CLI-001).

### 9.1. Pares Obrigatórios

Flags que devem ser usadas juntas:

| Par             | Contexto          | Mensagem de erro                                 |
| --------------- | ----------------- | ------------------------------------------------ |
| --start / --end | habit, habit atom | "--end é obrigatório quando --start é fornecido" |
| --from / --to   | report            | "--to é obrigatório quando --from é fornecido"   |

### 9.2. Mutuamente Exclusivos

Flags que não podem ser usadas juntas:

| Grupo                      | Contexto                   | Mensagem de erro                             |
| -------------------------- | -------------------------- | -------------------------------------------- |
| --color / --tag            | habit, task                | "Use --color OU --tag, não ambos"            |
| --start+--end / --duration | habit atom log             | "Use --start/--end OU --duration, não ambos" |
| --today / --week           | habit atom list, task list | "Especifique apenas um período"              |
| Flags de período           | report                     | "Especifique apenas um período"              |

### 9.3. Combinações Válidas

Flags que podem ser combinadas:

| Combinação            | Contexto        | Resultado                   |
| --------------------- | --------------- | --------------------------- |
| --today + --pending   | habit atom list | Hoje + status pending       |
| --today + --done      | habit atom list | Hoje + status done          |
| --today + --all       | habit atom list | Hoje + todos status         |
| --week + --pending    | habit atom list | Semana + status pending     |
| (período) + --habit   | report          | Período + filtro por hábito |
| (período) + --verbose | report          | Período + detalhes          |

### 9.4. Valores Default

Comportamento quando flags são omitidas:

| Comando         | Sem flags   | Default          |
| --------------- | ----------- | ---------------- |
| habit list      | (nada)      | --routine active |
| habit atom list | (nada)      | --week --pending |
| task list       | (nada)      | --pending        |
| report          | (nada)      | --month          |
| tag create      | (nada)      | --color banana   |
| habit create    | sem --renew | --renew month 3  |

### 9.5. Validações de Formato

| Flag           | Formato válido                             | Mensagem de erro                                             |
| -------------- | ------------------------------------------ | ------------------------------------------------------------ |
| --start, --end | HH:MM, HHh, HHhMM                          | "Formato inválido. Use HH:MM, HHh ou HHhMM"                  |
| --datetime     | "YYYY-MM-DD HH:MM", "DD/MM/YYYY HHh", etc. | "Formato inválido. Veja formatos aceitos com --help"         |
| --date         | YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY         | "Formato inválido. Use YYYY-MM-DD, DD/MM/YYYY ou DD-MM-YYYY" |
| --from, --to   | YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY         | "Formato inválido. Use YYYY-MM-DD, DD/MM/YYYY ou DD-MM-YYYY" |
| --color        | nome ou #RRGGBB                            | "Cor inválida. Use nome predefinido ou #RRGGBB"              |
| --duration     | inteiro positivo                           | "Duração deve ser número positivo"                           |
| --repeat       | enum ou lista                              | "Padrão inválido. Use WEEKDAYS, EVERYDAY, etc."              |

### 9.6. Validações Lógicas

| Validação         | Regra                     | Mensagem de erro                          |
| ----------------- | ------------------------- | ----------------------------------------- |
| --start < --end   | Hora início menor que fim | "Hora início deve ser menor que hora fim" |
| --from < --to     | Data início menor que fim | "Data início deve ser menor que data fim" |
| --duration > 0    | Duração positiva          | "Duração deve ser maior que zero"         |
| HABIT_ID existe   | ID deve existir no banco  | "Hábito ID X não encontrado"              |
| ROUTINE_ID existe | ID deve existir no banco  | "Rotina ID X não encontrada"              |
| TAG_ID existe     | ID deve existir no banco  | "Tag ID X não encontrada"                 |

---

## 10. Apêndice: Tabela de Flags

Referência rápida de todas as flags.

### 10.1. Flags com Short

| Long       | Short | Tipo       | Contextos                                |
| ---------- | ----- | ---------- | ---------------------------------------- |
| --all      | -a    | flag       | routine list, habit atom list, task list |
| --color    | -c    | string     | habit, task, tag                         |
| --date     | -d    | date       | habit atom                               |
| --datetime | -D    | datetime   | task                                     |
| --done     | -C    | flag       | habit atom list, task list               |
| --duration | -d    | int        | habit atom log                           |
| --end      | -e    | time       | habit, habit atom                        |
| --from     | -f    | date       | report                                   |
| --habit    | -h    | int        | report                                   |
| --month    | -m    | flag       | report                                   |
| --pending  | -P    | flag       | habit atom list, task list               |
| --quarter  | -q    | flag       | report                                   |
| --reason   | -r    | enum       | habit atom skip                          |
| --renew    | -n    | period+int | habit create                             |
| --routine  | -R    | string/int | habit create, habit list                 |
| --start    | -s    | time       | habit, habit atom                        |
| --tag      | -g    | int        | habit, task                              |
| --title    | -l    | string     | habit, task, tag, routine                |
| --to       | -t    | date       | report                                   |
| --today    | -T    | flag       | habit atom list, task list               |
| --verbose  | -v    | flag       | routine list, habit list, report         |
| --week     | -w    | flag       | habit atom list, task list, report       |
| --year     | -y    | flag       | report                                   |

### 10.2. Flags sem Short

| Long       | Tipo      | Contextos       | Motivo                           |
| ---------- | --------- | --------------- | -------------------------------- |
| --desc     | string    | task            | Raramente usado                  |
| --note     | string    | habit atom skip | Complementar a --reason          |
| --purge    | flag      | routine delete  | Operação destrutiva              |
| --repeat   | enum/list | habit           | Ver seção 11 (conflito com -r)   |
| --semester | flag      | report          | Menos comum                      |
| --status   | enum      | task edit       | Explícito para mudança de status |

### 10.3. Mnemônicos

| Short | Mnemônico       | Notas                        |
| ----- | --------------- | ---------------------------- |
| -a    | All             |                              |
| -c    | Color           |                              |
| -C    | Complete/Check  | Maiúsculo                    |
| -d    | Date / Duration | Contexto define              |
| -D    | Datetime        | Maiúsculo (diferencia de -d) |
| -e    | End             |                              |
| -f    | From            |                              |
| -g    | taG             |                              |
| -h    | Habit           |                              |
| -l    | Label (title)   |                              |
| -m    | Month           |                              |
| -n    | New (renew)     |                              |
| -P    | Pending         | Maiúsculo                    |
| -q    | Quarter         |                              |
| -r    | Reason          |                              |
| -R    | Routine         | Maiúsculo                    |
| -s    | Start           |                              |
| -t    | To              |                              |
| -T    | Today           | Maiúsculo                    |
| -v    | Verbose         |                              |
| -w    | Week            |                              |
| -y    | Year            |                              |

---

## 11. Apêndice: Conflitos de Flags

Esta seção documenta os conflitos de letras entre flags e as decisões tomadas.

### 11.1. Conflitos Identificados

Durante o design da CLI, algumas letras foram disputadas por múltiplas flags:

| Letra | Candidatos                         | Decisão                          |
| ----- | ---------------------------------- | -------------------------------- |
| -d    | --date, --done, --duration, --desc | --date e --duration por contexto |
| -n    | --name, --note, --renew            | --renew (-n = "new")             |
| -p    | --pending, --purge                 | Nenhum (usam maiúsculas)         |
| -r    | --reason, --repeat, --renew        | --reason                         |
| -s    | --start, --semester                | --start                          |
| -t    | --title, --tag, --to, --today      | --to (par com --from)            |

### 11.2. Resolução por Maiúsculas

Quando conflitos não puderam ser resolvidos por contexto, usamos maiúsculas:

| Flag       | Short | Justificativa                      |
| ---------- | ----- | ---------------------------------- |
| --datetime | -D    | Diferencia de --date (-d)          |
| --done     | -C    | "Complete/Check", diferencia de -d |
| --pending  | -P    | Maiúsculo para par com -C          |
| --today    | -T    | Diferencia de --to (-t)            |
| --routine  | -R    | Diferencia de --reason (-r)        |

### 11.3. Flags Deixadas sem Short

Algumas flags intencionalmente não têm versão curta:

| Flag       | Motivo                                    |
| ---------- | ----------------------------------------- |
| --purge    | Operação destrutiva - deve ser explícita  |
| --repeat   | Conflito com -r (--reason mais frequente) |
| --desc     | Raramente usado                           |
| --note     | Complementar, sempre com --reason         |
| --semester | Menos comum que outros períodos           |

### 11.4. Contexto Define Significado

A flag -d tem significados diferentes por contexto:

| Contexto          | -d significa |
| ----------------- | ------------ |
| habit atom create | --date       |
| habit atom edit   | --date       |
| habit atom log    | --duration   |

Isso é aceitável porque:

1. Os contextos são claramente distintos
2. O tipo de valor esperado é diferente (data vs número)
3. Segue padrão de outras CLIs (ex: `docker run -d` vs `docker logs -d`)

### 11.5. Pares Semânticos Preservados

Priorizamos manter consistência em pares semânticos:

| Par                | Shorts  | Contexto       |
| ------------------ | ------- | -------------- |
| --start / --end    | -s / -e | Horário        |
| --from / --to      | -f / -t | Range de datas |
| --pending / --done | -P / -C | Status         |

Isso significa que --title (-l, "label") e --today (-T) cederam suas letras "naturais" para manter os pares consistentes.

---

## 12. Comandos Depreciados

Os seguintes comandos foram descontinuados:

| Depreciado          | Substituição               | Versão de remoção |
| ------------------- | -------------------------- | ----------------- |
| schedule generate   | habit create --renew       | v2.0.0            |
| habit adjust        | habit atom edit            | v2.0.0            |
| list (global)       | habit atom list, task list | v2.0.0            |
| add (global)        | task create                | v2.0.0            |
| routine edit --name | routine edit --title       | v2.0.0            |

## 13. Roadmap: Comandos Futuros

Esta seção documenta comandos planejados para versões futuras.

### 13.1. reason (v2.1.0)

Gerencia motivos customizados para skip.

| Comando       | Descrição                 |
| ------------- | ------------------------- |
| reason create | Cria motivo customizado   |
| reason list   | Lista motivos disponíveis |
| reason delete | Remove motivo customizado |

**reason create:**

```bash
timeblock reason create <TITLE>
```

**Exemplo:**

```bash
timeblock reason create "Compromisso social"
timeblock reason create "Manutenção do carro"
```

**reason list:**

```bash
timeblock reason list

Motivos disponíveis:

Predefinidos:
  HEALTH          Saúde
  WORK            Trabalho
  FAMILY          Família
  TRAVEL          Viagem
  WEATHER         Clima
  LACK_RESOURCES  Falta de recursos
  EMERGENCY       Emergência
  OTHER           Outro

Customizados:
  1. Compromisso social
  2. Manutenção do carro
```

**reason delete:**

```bash
timeblock reason delete <REASON_ID>
```

### 13.2. sync (v2.2.0)

Sincronização offline-first entre dispositivos.

| Comando     | Descrição                      |
| ----------- | ------------------------------ |
| sync status | Mostra status de sincronização |
| sync now    | Força sincronização imediata   |
| sync config | Configura servidor de sync     |

### 13.3. import/export (v2.1.0)

Importação e exportação de dados.

| Comando        | Descrição                          |
| -------------- | ---------------------------------- |
| import routine | Importa rotina de arquivo Markdown |
| export routine | Exporta rotina para Markdown       |
| export report  | Exporta relatório para PDF/CSV     |

### 13.4. config (v2.0.0)

Configurações do sistema.

| Comando      | Descrição                   |
| ------------ | --------------------------- |
| config show  | Mostra configurações atuais |
| config set   | Define configuração         |
| config reset | Restaura padrões            |

**Configurações planejadas:**

| Chave             | Tipo | Default | Valores           | Descrição                                     |
| ----------------- | ---- | ------- | ----------------- | --------------------------------------------- |
| theme             | enum | auto    | light, dark, auto | Tema de cores                                 |
| language          | enum | pt-BR   | pt-BR, en, es     | Idioma da interface                           |
| week_start        | enum | monday  | monday, sunday    | Primeiro dia da semana                        |
| notification_days | int  | 7       | 1-30              | Dias antes de avisar sobre fim das instâncias |

---

## Referências

- **Business Rules:** `docs/core/business-rules.md`
- **Architecture:** `docs/core/architecture.md`
- **ADR-005:** Resource-first CLI
- **ADR-018:** Language Standards

---

**Documento consolidado em:** 30 de Novembro de 2025
