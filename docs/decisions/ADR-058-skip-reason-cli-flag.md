# ADR-058: Seleção de motivo de skip — flags no CLI, interatividade no TUI

- **Status:** Aceito
- **Data:** 2026-06-14
- **Substitui:** BR-SKIP-004 (CLI Prompt Interativo)
- **Relacionado:** BR-TUI-024, ADR-019, ADR-020, issue #42 (Caso 3), issue #51

---

## Contexto

Escolher o motivo de um skip envolve duas decisões independentes: por onde o
usuário informa o motivo (de forma interativa ou por flag) e qual a variante do
skip (justificado, com motivo categorizado; ou não justificado, sem motivo). Este
ADR define onde cada uma dessas decisões vive no produto.

O TUI já oferece a entrada interativa: o modal da BR-TUI-024 lista as categorias
de `SkipReason`. O CLI atende a automação, e ali a flag é a forma natural de
informar a intenção. A BR-SKIP-004 propunha juntar as duas decisões num único
prompt interativo dentro do CLI (menu `[1-9]`). Como o TUI já cobre a parte
interativa, este ADR separa as duas decisões e as distribui entre as superfícies.

A mesma decisão acerta o vocabulário da flag. O campo no modelo é `skip_reason`,
o tipo é `SkipReason` e a BR-SKIP-001 já fala em `--reason`; só a implementação
destoa, expondo `--category`/`-c`. Além disso, `-c` disputa a letra com `--color`
(de `habit create` e `habit update`). É um caso concreto da inconsistência de
nomenclatura que a issue #51 trata (ADR-020).

## Decisão

1. **A entrada interativa pertence ao TUI** (BR-TUI-024), e o modal cobre as duas
   variantes: as 8 categorias de `SkipReason` e uma opção "Sem justificativa". O
   CLI atende a automação e recebe o motivo por flag.

2. **CLI, skip justificado:** `habit skip <id> --reason <CATEGORIA>` marca
   `NOT_DONE` / `SKIPPED_JUSTIFIED` e grava `skip_reason`.

3. **CLI, skip não justificado:** `habit skip <id> --unjustified` marca
   `NOT_DONE` / `SKIPPED_UNJUSTIFIED`, sem `skip_reason`. Com a opção do modal
   (Decisão 1), `SKIPPED_UNJUSTIFIED` passa a ser alcançável pelas duas
   superfícies — uma variante de primeira classe, não um estado restrito a um
   único caminho.

4. **Guardas:** o skip sem flag (`habit skip <id>`) falha de propósito, para o
   usuário nunca criar um skip sem perceber; `--reason` e `--unjustified` não
   convivem na mesma chamada; `--note` continua opcional nas duas variantes, no
   CLI e no modal.

5. **Renomeações de flag:** `--category`/`-c` passa para `--reason`/`-r`,
   alinhando a flag ao campo (`skip_reason`), ao tipo (`SkipReason`) e à
   documentação, e devolvendo `-c` ao `--color`. A nova `--unjustified` usa o
   short `-u`, que está livre. O `-r` repete, em outro subcomando, a letra de
   `--repeat`; o Typer isola os shorts por comando, então não há conflito ao
   executar.

6. **A BR-SKIP-004 é descontinuada.** O menu interativo `[1-9]` no CLI cede lugar
   à entrada por flag (justificado e não justificado) somada à interatividade do
   TUI (BR-TUI-024), cujo modal ganha a 9ª opção "Sem justificativa" ao lado das
   8 categorias. Tudo o que a BR-SKIP-004 reunia — categorizar e não justificar —
   continua disponível, dividido entre as superfícies, sem estado alcançável por
   um único caminho.

### Contrato resultante

```
habit skip 42 --reason WORK     → SKIPPED_JUSTIFIED + reason
habit skip 42 --unjustified     → SKIPPED_UNJUSTIFIED
habit skip 42                   → erro: informe --reason CAT ou --unjustified
habit skip 42 --reason W -u     → erro: --reason e --unjustified não convivem
```

## Alternativas consideradas

- **Levar o prompt interativo também para o CLI** (a BR-SKIP-004 original).
  Descartada: repetiria no CLI a interatividade que o TUI já entrega
  (BR-TUI-024), ao custo de um laço de prompt, do parsing de `[1-9]` e de testes
  de entrada pelo terminal, com pouco retorno. A divisão "TUI interativo, CLI por
  flag" é mais coesa.

- **Permitir skip sem flag** — `habit skip <id>` sozinho criaria
  `SKIPPED_UNJUSTIFIED`. Descartada: um comando digitado por engano viraria um
  skip não justificado sem o usuário querer. O caminho não justificado fica
  explícito na flag `--unjustified` (Decisão 3).

## Referências

- `docs/reference/business-rules/br-skip.md` (BR-SKIP-001 a 004)
- `docs/reference/business-rules/br-tui.md` (BR-TUI-024 — Skip com Modal de SkipReason)
- ADR-019 (Test Naming Convention), ADR-020 (Business Rules Nomenclature)
- Issue #42 (Caso 3 — rastreabilidade BR→teste), Issue #51 (reconciliação ADR-020)
