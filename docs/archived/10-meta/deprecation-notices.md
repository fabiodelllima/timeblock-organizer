# API Deprecation Notices

Este documento registra mudanças de API e funcionalidades depreciadas no TimeBlock Organizer.

**Formato:** `DATA | ANTIGO -> NOVO | Caminho de Migração | Versão de Remoção`

---

## Depreciações Ativas

### CLI Commands

#### 27-11-2025: `schedule generate` -> `habit create --generate`

| Aspecto      | Detalhe                                                  |
| ------------ | -------------------------------------------------------- |
| **Antigo**   | `schedule generate HABIT_ID --from DATE --to DATE`       |
| **Novo**     | `habit create --title "X" ... --generate N` (N = meses)  |
| **Razão**    | Simplificação do workflow - geração integrada na criação |
| **Migração** | Usar flag `--generate N` durante criação do habit        |
| **Remoção**  | v2.0.0                                                   |

**Exemplo de migração:**

```bash
# Antes (2 comandos)
habit create --title "Meditação" --start 06:00 --end 06:30 --repeat EVERYDAY
schedule generate HABIT_ID --from 01-01-2025 --to 31-01-2025

# Depois (1 comando)
habit create --title "Meditação" --start 06:00 --end 06:30 --repeat EVERYDAY --generate 1
```

---

#### 27-11-2025: `list --weeks` -> `list --week`

| Aspecto      | Detalhe                                         |
| ------------ | ----------------------------------------------- |
| **Antigo**   | `list --weeks 4` (parâmetro separado de --week) |
| **Novo**     | `list --week +4` (sintaxe unificada)            |
| **Razão**    | API confusa com dois parâmetros similares       |
| **Migração** | Substituir `--weeks N` por `--week +N`          |
| **Remoção**  | v2.0.0                                          |

**Nova sintaxe:**

```bash
list --week 0      # Esta semana
list --week +1     # Próxima semana
list --week +4     # Próximas 4 semanas
list --week -1     # Semana passada
```

---

#### 27-11-2025: `habit adjust` -> `habit edit`

| Aspecto      | Detalhe                                                   |
| ------------ | --------------------------------------------------------- |
| **Antigo**   | `habit adjust HABIT_ID --start TIME --end TIME`           |
| **Novo**     | `habit edit HABIT_ID --start TIME --end TIME`             |
| **Razão**    | Nomenclatura mais clara e consistente com outros comandos |
| **Migração** | Substituir `adjust` por `edit`                            |
| **Remoção**  | v2.0.0                                                    |

---

### Documentação Arquivada

Os seguintes documentos foram movidos para `docs/10-meta/archived/` por conterem
informações obsoletas ou específicas de sessões passadas:

| Documento                                       | Data       | Razão                                |
| ----------------------------------------------- | ---------- | ------------------------------------ |
| `schedule-generate-improvements-2025-11-13.md`  | 27-11-2025 | Proposta não implementada, API mudou |
| `sprint-e2e-and-test-refactoring-2025-11-12.md` | 27-11-2025 | Sprint concluída                     |

---

## Depreciações Concluídas (Removidas)

_Nenhuma depreciação foi completamente removida ainda._

---

## Princípios de Depreciação

Baseado em [Software Engineering at Google](https://abseil.io/resources/swe-book/html/ch15.html)
e [Keep a Changelog](https://keepachangelog.com/):

1. **Avisos acionáveis:** Todo aviso de depreciação inclui caminho de migração
2. **Relevância:** Apenas mudanças que afetam usuários são documentadas
3. **Timeline claro:** Versão de remoção sempre especificada
4. **Arquivo, não delete:** Docs obsoletos são arquivados para referência histórica

---

## Referências

- ADR-018: Language Standards
- ADR-020: Business Rules Nomenclature
- docs/10-meta/changelog.md

---

Última atualização: 27-11-2025
