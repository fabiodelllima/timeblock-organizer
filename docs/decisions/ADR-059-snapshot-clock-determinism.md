# ADR-059: Relógio congelado para testes de snapshot de TUI

- **Status:** Aceito
- **Data:** 2026-06-18

## Contexto

Os testes de snapshot da TUI (`tests/e2e/test_snapshots.py` e `tests/e2e/test_snapshot_cruds.py`) capturam o dashboard renderizado via `export_screenshot()` do Textual e comparam byte a byte com baselines. O dashboard lê a data e a hora correntes — cabeçalho, loader, agenda e o elapsed do timer passam por `date.today()` e `datetime.now()` —, então o SVG variava a cada dia e os snapshots quebravam diariamente. Por isso estavam excluídos dos gates (pre-push e CI) via `--ignore`, sem cobertura efetiva de regressão visual.

## Decisão

- Os testes de snapshot rodam sob relógio congelado (freezegun), por uma fixture autouse escopada no `conftest.py` aos módulos de snapshot, com data fixa `SNAPSHOT_FROZEN_DATETIME = "2025-06-16 09:00:00"`.
- A fixture usa `tick=True`: o relógio parte da data fixa e avança em tempo real. O congelamento pleno congelaria `time.monotonic()` e travaria os timers do asyncio — o `pilot.pause()` dos testes que abrem modais nunca retornaria. Com `tick`, data e minuto seguem fixos (cada teste roda em milissegundos) e o elapsed do timer trunca para o valor esperado.
- O escopo por nome de módulo preserva os demais testes e2e: `test_task_lifecycle` tem `@freeze_time` próprio, e outros dependem de `now` real.
- Os baselines foram regenerados via `pytest --snapshot-update` e os snapshots reabilitados nos gates (pre-push e CI).

## Consequências

- Snapshots determinísticos: não quebram mais com a virada do dia, e voltam a cobrir regressão visual no pre-push e no CI.
- Os baselines SVG dependem do ambiente de render. O CI usa `textual==8.2.3` (pin exato em `requirements.txt`) sobre `python:3.14-slim`, alinhado ao ambiente local que gerou os baselines; o pin exato do Textual é parte da garantia — uma divergência de versão quebraria a comparação byte a byte.
- O elapsed do timer trunca para `01:25:00`. Resíduo teórico: se o intervalo entre o setup e o render passar de 1 segundo sob carga extrema, o valor truncaria diferente; é improvável para um render único de dashboard, e a correção seria escopar congelamento pleno apenas nesse teste.
- O baseline de `timer_running` captura "em andamentoLeitura" (sem espaço entre status e nome), defeito de formatação pré-existente do timer panel rastreado em issue própria; o snapshot apenas reflete a UI atual.
