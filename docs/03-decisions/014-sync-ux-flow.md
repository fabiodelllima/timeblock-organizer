# ADR-014: Sync UX Flow - Connect Paradigm

**Status**: Accepted

**Data**: 2025-11-05

**Depende de**: ADR-012, ADR-013

## Contexto

ADR-012 definiu Queue-Based Sync. ADR-013 definiu schema tecnico. Agora precisamos definir **como o usuario interage** com sincronizacao.

**Requisitos UX:**

1. Simplicidade
2. Controle
3. Confianca
4. Familiaridade
5. Nao-intrusivo
6. Auditavel

## Decisao

Adotamos **"Connect Paradigm"** com discovery automatica e resolucao interativa.

### Comando Principal

```bash
$ timeblock connect

Procurando servidor TimeBlock na rede...
Servidor encontrado: Servidor TimeBlock
Rede: Casa WiFi

Conectar a este servidor? [Y/n] Y

Conectando...
Sincronizando dados...
  - 3 habits enviados
  - 5 habits recebidos
  - 1 conflito detectado

Sincronizacao completa!
```

### Resolucao Interativa

```bash
Conflito detectado - Habit "Exercicio":

  Campo              Local       Remoto
  scheduled_start    07:00       09:00
  updated_at         10:30       10:45
  device             Termux      Fedora

Manter qual versao? [(L)ocal/(R)emoto] R

Aplicando versao remota...
Conflito resolvido
```

### Novos Comandos

1. **timeblock connect** - Sincroniza
2. **timeblock server** - Inicia servidor
3. **timeblock status** - Status sync
4. **timeblock queue** - Inspeciona fila

## Alternativas Consideradas

- **IP/Porta Manual**: Rejeitada (mDNS resolve)
- **Push/Pull Separados**: Rejeitada (um comando suficiente)
- **Auto-Resolve Default**: Rejeitada (interativo default)
- **GUI/TUI**: Rejeitada v2.0 (possivel v2.5)

## Consequencias

### Positivas

1. Zero configuracao (mDNS)
2. Transparencia total
3. Controle fino
4. UX familiar (git-like)
5. Feedback rico
6. Extensivel

### Negativas

1. Requer mesma rede (mDNS)
2. Discovery pode falhar
3. Resolucao bloqueante
4. Conflitos complexos dificeis

**Mitigacoes**: Fallback `--server`, modo `--auto`, timeout, contexto adicional.

## Fluxos Completos

### Primeiro Sync

```bash
# Fedora
$ timeblock server start
Servidor rodando em 0.0.0.0:8000

# Termux
$ timeblock connect
Sincronizacao completa!
```

### Conflito Simples

```bash
$ timeblock connect
Conflito detectado
[diff table]
Manter qual versao? [L/R] L
Conflito resolvido
```

### Debug

```bash
$ timeblock connect --details
[IP, porta, hostname, latencia]
```

## Validacao

1. Time to first sync: <30s
2. Discovery success: >95%
3. User comprehension: >90%
4. Conflict resolution: <1min
5. Error recovery: >95%

## Referencias

- Git UX: <https://git-scm.com/book/>
- mDNS: <https://www.zeroconf.org/>
- CLI Guidelines: <https://clig.dev/>

---

**Upstream**: ADR-012, ADR-013

**Related**: ADR-011, ADR-002
