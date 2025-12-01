# ADR-012: Sync Strategy - Queue-Based Architecture

**Status**: Accepted

**Data**: 2025-11-05

## Contexto

O TimeBlock Organizer v1.2.0 é uma aplicação CLI local que opera exclusivamente em SQLite. Com a evolução para v2.0, precisamos sincronizar dados entre dois dispositivos:

- **Linux Desktop** (Fedora): Dispositivo primário de trabalho
- **Android Mobile** (Termux): Dispositivo móvel para consultas/updates rápidos

**Requisitos Fundamentais:**

- **Offline-First**: Ambos dispositivos devem funcionar 100% offline
- **Eventual Consistency**: Sincronização assíncrona quando conectados
- **User Control**: Usuário decide quando sincronizar (não automático)
- **Simplicidade**: Solução simples para uso pessoal (1 usuário)
- **Battery-Friendly**: Não drenar bateria do mobile com daemons
- **Auditável**: Fácil debugar (inspecionar filas, logs estruturados)

**Situação Atual:**

- Sistema funciona localmente
- Sem infraestrutura de sync
- Cada dispositivo tem banco SQLite independente
- Modificações manuais duplicadas (erro-prone)

## Decisão

Adotamos **Queue-Based Sync** com comando explícito `timeblock connect` porque:

1. Oferece controle total ao usuário
2. Zero overhead quando offline
3. É auditável e debugável
4. Não requer daemon/background process
5. Similar a ferramentas familiares (git, npm)

### Arquitetura Escolhida

```terminal
┌─────────────────────────────────────────────────────────────┐
│ CRUD Operation (Create/Update/Delete)                       │
│   ↓                                                         │
│ Service Layer                                               │
│   ↓                                                         │
│ SyncQueue.add(operation) → ~/.timeblock/sync_queue.json     │
│   ↓                                                         │
│ [Operations persisted locally]                              │
│   ↓                                                         │
│ User executes: timeblock connect                            │
│   ↓                                                         │
│ DiscoveryService.discover_server() [mDNS]                   │
│   ↓                                                         │
│ SyncService.sync()                                          │
│   ├─ Push local queue → Server                              │
│   ├─ Server detects conflicts                               │
│   ├─ Pull remote changes ← Server                           │
│   └─ Apply changes locally                                  │
│   ↓                                                         │
│ Conflict Resolution (if any)                                │
│   ├─ Interactive: User chooses                              │
│   └─ Auto: Last-write-wins                                  │
│   ↓                                                         │
│ Clear queue after successful sync                           │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### **1. SyncQueue**

- Persiste operações em `~/.timeblock/sync_queue.json`
- Formato JSON legível (fácil debug)
- Append-only até sync completo
- Cada operação tem: id, timestamp, device_id, type, data

#### **2. DiscoveryService**

- mDNS/Zeroconf para descoberta automática
- Mostra nome amigável ("Servidor TimeBlock")
- Esconde detalhes técnicos (IP, porta) por padrão
- Modo `--details` para debug

#### **3. SyncService**

- Push: Envia queue para servidor
- Pull: Recebe mudanças remotas
- Merge: Aplica mudanças localmente
- Conflict Detection: Compara `updated_at`

#### **4. FastAPI Server**

- Endpoints: `/sync/push`, `/sync/pull`, `/ping`
- Roda no Fedora (porta 8000)
- Anuncia via mDNS
- Stateless (SQLite local como storage)

### Fluxo de Uso

```bash
# Dispositivo 1 (Fedora)
$ timeblock habit create "Exercicio" --start 07:00 --duration 60
✓ Habit criado (adicionado à fila de sync)

# Dispositivo 2 (Termux)
$ timeblock habit update <uuid> --start 09:00
✓ Habit atualizado (adicionado à fila de sync)

# Conectar para sincronizar
$ timeblock connect
Procurando servidor TimeBlock na rede...
Servidor encontrado: Servidor TimeBlock
Rede: Casa WiFi

Conectar a este servidor? [Y/n] Y

Conectando...
Sincronizando dados...
  - 1 habit enviado
  - 1 habit recebido

⚠ Conflito detectado - Habit "Exercicio":
  Campo           Local    Remoto
  ─────────────────────────────────
  scheduled_start 07:00    09:00
  updated_at      10:30    10:45

Manter qual versao? [(L)ocal/(R)emoto] R

Sincronizacao completa!
```

## Alternativas Consideradas

### Opção 1: Daemon Auto-Sync

Background daemon monitora mudanças e sincroniza automaticamente.

**Prós:**

- Transparente para usuário
- Sincronização mais frequente
- Conflitos menores (sync mais rápido)

**Contras:**

- **Overhead constante** (CPU, bateria mobile)
- **Complexidade**: gerenciar ciclo de vida do daemon
- **Hard to debug**: processo pode morrer silenciosamente
- **Battery drain**: inaceitável em mobile
- **Não auditável**: usuário não sabe quando sincronizou
- **Overkill**: para 1 usuário, é excessivo

**Veredicto**: Rejeitada. Complexidade não justifica benefícios para uso pessoal.

### Opção 2: Syncthing + SQLite

Usar Syncthing para sincronizar arquivo SQLite entre dispositivos.

**Prós:**

- Solução pronta
- Zero código custom
- Funciona para qualquer arquivo

**Contras:**

- **Corrupção garantida**: SQLite não suporta sync de arquivo binário
- **Write locks**: conflitos de lock entre dispositivos
- **Database corruption**: merge binário = database corrupted
- **Sem conflict resolution**: Syncthing não entende SQLite
- **Não auditável**: conflitos são silenciosos

**Veredicto**: Rejeitada. SQLite não é feito para sync de arquivo. Causa corrupção de dados.

### Opção 3: API-Only (Cloud Required)

Servidor central na cloud, clientes sempre consultam API.

**Prós:**

- Sincronização imediata
- Sempre consistente
- Escalável para múltiplos usuários

**Contras:**

- **Quebra offline-first**: requer internet sempre
- **Latência**: operações dependem de rede
- **Custo**: hosting cloud mensal
- **Privacidade**: dados em servidor terceiro
- **Overkill**: 1 usuário não precisa cloud
- **Complexidade**: autenticação, sessões, etc

**Veredicto**: Rejeitada. Viola requisito offline-first e adiciona custos desnecessários.

### Opção 4: Git-Based Sync

Usar Git para versionar e sincronizar database.

**Prós:**

- Ferramenta conhecida
- Auditável (git log)
- Merge strategies prontas

**Contras:**

- **Binary merge**: SQLite é binário, git não merga bem
- **Overhead**: commit/push manual para cada operação
- **Complexidade**: usuário precisa entender git
- **Não semântico**: git não entende Habit/Task/etc
- **Lock conflicts**: mesmos problemas do Syncthing

**Veredicto**: Rejeitada. Git não é ferramenta para sync de application data.

## Consequências

### Positivas

#### **1. Controle Total do Usuário**

- Usuário decide quando sincronizar
- Visibilidade clara do processo
- Sem surpresas (daemon morrendo, sync falhando silenciosamente)

#### **2. Zero Overhead Offline**

- Nenhum processo em background
- Battery-friendly (crítico para mobile)
- Performance máxima no uso diário

#### **3. Auditabilidade**

- Queue JSON é human-readable
- Fácil inspecionar operações pendentes: `cat ~/.timeblock/sync_queue.json`
- Logs estruturados de todas sincronizações
- Debug simples: ver queue, ver logs, ver banco

#### **4. Simplicidade Técnica**

- Menos código para manter
- Menos bugs (sem race conditions de daemon)
- Fácil testar (mock queue, mock server)
- Deployment simples (sem systemd, sem service management)

#### **5. UX Familiar**

- Similar a `git push/pull`
- Similar a `npm sync`
- Usuários tech já conhecem o padrão
- Comando explícito > magia automática

#### **6. Escalabilidade Futura**

- Base sólida para features avançadas:
  - v2.5: Sync automático opcional (opt-in)
  - v3.0: Multiple servers
  - v3.5: Peer-to-peer sync

### Negativas

#### **1. Sincronização Manual**

- Usuário precisa lembrar de executar `timeblock connect`
- Conflitos podem acumular se esquecer de sincronizar
- Não é "transparente" como daemon seria

**Mitigação**:

- Dashboard TUI mostra badge de operações pendentes
- Comando `timeblock status` mostra queue count
- Prompt amigável: "3 operações pendentes. Sincronizar agora?"

#### **2. Janela de Conflitos Maior**

- Quanto mais tempo sem sync, maior chance de conflitos
- Conflitos acumulados são mais complexos de resolver

**Mitigação**:

- UX de resolução interativa clara
- Modo `--auto` para resolver automaticamente (last-write-wins)
- Educação: "Sincronize ao final do dia"

#### **3. Requer Servidor Ativo**

- Server FastAPI precisa estar rodando no Fedora
- Se server estiver offline, sync falha

**Mitigação**:

- Queue persiste operações até server voltar
- Mensagem clara: "Servidor não encontrado. Operações salvas na fila."
- Healthcheck: `timeblock connect --check` (não sincroniza, só testa conexão)

### Neutras

#### **1. Discovery via mDNS**

- Requer mesma rede local (WiFi)
- Não funciona entre redes diferentes (VPN necessária se precisar)

**Solução Futura**: v2.5 pode adicionar descoberta por IP manual (fallback)

#### **2. Queue JSON Crescente**

- Queue pode crescer se usuário não sincronizar por semanas
- JSON parsing lento se queue > 10.000 operações

**Solução**: Implementar compactação/archiving de queues antigas (v2.5)

#### **3. FastAPI Server Single-Threaded**

- Server atual é single-device (apenas 1 cliente por vez)
- Não escala para múltiplos usuários

**Solução**: Não é problema para uso pessoal. v3.0 pode adicionar multi-tenant se necessário.

## Validação

Consideramos esta decisão acertada se:

### Métricas Técnicas

1. **Queue Performance**: Adicionar operação à queue < 10ms
2. **Sync Speed**: Sincronizar 100 operações < 5 segundos
3. **Discovery Time**: Descobrir servidor via mDNS < 3 segundos
4. **Battery Impact**: Termux não consome >1% bateria extra por hora (zero daemon)
5. **Reliability**: 0 corrupções de database em 6 meses de uso

### Métricas UX

1. **User Adoption**: Usuário sincroniza pelo menos 1x por dia
2. **Conflict Rate**: < 5% das sincronizações resultam em conflito
3. **Conflict Resolution Time**: Resolver conflito < 30 segundos
4. **Discovery Success**: mDNS descobre servidor em 95% das tentativas
5. **Sync Success Rate**: > 98% das sincronizações completam sem erro

### Métricas de Manutenção

1. **Code Simplicity**: Sync codebase < 1.000 LOC
2. **Test Coverage**: > 90% coverage em sync components
3. **Bug Rate**: < 2 bugs críticos de sync por mês
4. **Debug Time**: Diagnosticar problema de sync < 15 minutos (logs + queue inspection)

## Referências

### Conceitos

- **Offline-First**: <https://offlinefirst.org/>
- **Eventual Consistency**: <https://en.wikipedia.org/wiki/Eventual_consistency>
- **Queue-Based Architectures**: <https://www.enterpriseintegrationpatterns.com/patterns/messaging/>

### Ferramentas Similares

- **Git**: Queue-based (staging area), explicit push/pull
- **npm/yarn**: Explicit sync commands, offline-capable
- **rsync**: On-demand sync, user-controlled
- **Nextcloud Sync Client**: Offers both auto and manual modes

### Tecnologias Usadas

- **mDNS/Zeroconf**: <https://github.com/python-zeroconf/python-zeroconf>
- **FastAPI**: <https://fastapi.tiangolo.com/>
- **SQLModel**: <https://sqlmodel.tiangolo.com/>

### Decisões Relacionadas

- ADR-013: Offline-First Schema (depende desta decisão)
- ADR-014: Sync UX Flow (implementa esta decisão)
- ADR-011: Conflict Philosophy (base conceitual para merge strategy)
