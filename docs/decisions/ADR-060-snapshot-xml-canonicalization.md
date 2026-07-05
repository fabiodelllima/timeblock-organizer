# ADR-060: Canonicalização de XML nas snapshots SVG

- **Status:** Aceito
- **Data:** 2026-07-04
- **Issue de origem:** #69
- **ADRs relacionados:** ADR-059 (Snapshot Clock Determinism — trata determinismo de relógio; este trata determinismo de formatação)
- **BRs relacionadas:** N/A (infraestrutura de testes de snapshot)

## Contexto

A comparação de snapshots é byte a byte (`assert svg == snapshot` no
`SVGSnapshotExtension`, via `tests/e2e/conftest.py`). O SVG vem do
`export_screenshot()` do Textual, e a **formatação** que ele emite — o layout
da tag raiz `<svg>`, a indentação e as quebras de linha entre elementos — varia
entre versões do Textual e entre ambientes de renderização. Uma diferença
puramente de formatação, sem qualquer regressão visual, quebra a comparação.

Hoje isso é contido por dois acordos frágeis: gerar todos os baselines no mesmo
ambiente (venv com `textual==8.2.3`) e fixar a imagem do CI na mesma versão.
Basta um bump de Textual ou uma divergência de ambiente para quebrar a
comparação sem que exista regressão real — foi o que já se observou (um baseline
com o `<svg>` em múltiplas linhas versus um render em linha única; mesmo
conteúdo visual, bytes diferentes, teste quebrado).

Secundariamente, a extensão declara `_file_extension = "svg"`, mas o syrupy 5.x
lê o atributo `file_extension` (sem sublinhado), cujo padrão é `"raw"`. O
atributo com sublinhado é ignorado, e os baselines são gravados como `.raw` — um
nome de arquivo que não corresponde ao conteúdo SVG.

Este é o problema irmão do ADR-059: aquele fechou o determinismo de **relógio**
(a data no render); este fecha o determinismo de **formatação** (a forma textual
que o ambiente emite).

## Decisão

Canonicalizar o XML do SVG dentro do `serialize()` do `SVGSnapshotExtension` —
o ponto único por onde todo SVG passa, tanto na geração do baseline
(`--snapshot-update`) quanto na comparação. Como os dois caminhos passam pela
mesma forma canônica, diferenças cosméticas de formatação entre versões e
ambientes deixam de quebrar o teste.

O método usa apenas a stdlib, sem dependência nova:

1. Parse do SVG com `xml.etree.ElementTree`.
2. Remoção dos nós `text`/`tail` compostos exclusivamente de whitespace XML
   (espaço, tab, CR, LF) — a indentação estrutural entre elementos. Qualquer nó
   com conteúdo visível é preservado intacto, inclusive os espaços
   não-quebráveis (`&#160;`/`\xa0`) que carregam o espaçamento dos painéis.
3. `ET.canonicalize()` (C14N) sobre a árvore resultante, produzindo uma
   serialização determinística.

Corrigir a extensão para `file_extension = "svg"` (o nome que o syrupy 5.x
honra), passando os baselines a `.svg`, coerente com o conteúdo.

Regenerar os 19 baselines existentes (16 em `test_snapshot_cruds`, 3 em
`test_snapshots`) uma única vez, na forma canônica e com a extensão `.svg`.

Adicionar um teste garantindo que a canonicalização é **idempotente**
(`canonical(canonical(x)) == canonical(x)`) e **preserva o conteúdo visível** —
critério de aceite da issue #69.

## Alternativas consideradas

- **`lxml` com serialização canônica.** Resolve, mas adiciona uma dependência
  nativa; o `ET.canonicalize` da stdlib é suficiente. Rejeitada por não
  justificar a dependência.
- **`ET.canonicalize(strip_text=True)`.** Normaliza a formatação, mas trata os
  nbsp como whitespace removível e remove os `\xa0` no início e no fim dos nós
  de texto — corrompendo o espaçamento visível (o `  Leitura` do card perde os
  dois espaços). Rejeitada por não preservar conteúdo. Verificado empiricamente.
- **`ET.canonicalize` sem `strip_text`.** Preserva o conteúdo, mas não normaliza
  o whitespace estrutural entre elementos — um SVG e sua versão reformatada
  divergem. Insuficiente sozinha. Verificado empiricamente.
- **Normalização por regex (`re.sub(r">\s+<", "><", svg)`).** Frágil: o `\s` do
  Python casa nbsp por padrão, arriscando remover nós de texto compostos só de
  nbsp (células vazias), e prescinde da robustez do reparse. Rejeitada em favor
  da abordagem baseada em parse.
- **Formatador externo sobre os arquivos em disco.** Quebraria a comparação — o
  comparador não bateria com os arquivos reformatados. A normalização tem de
  estar no caminho do comparador (`serialize`), não nos arquivos. Rejeitada.
- **Status quo (fixar Textual e a imagem do CI).** É o acordo frágil atual; um
  bump quebra a comparação sem regressão real. É o problema que este ADR resolve.

## Consequências

**Positivas.** A comparação passa a depender do conteúdo visual, não da forma
textual que o ambiente emitiu. Os baselines se desacoplam da versão exata do
Textual, reduzindo a fragilidade a bumps e a divergências de ambiente. A
extensão dos arquivos passa a corresponder ao conteúdo (`.svg`).

**Custos.** Os 19 baselines são reescritos uma vez — um diff grande e único. A
forma canônica re-serializa namespaces e expande entidades, então os arquivos
mudam de forma e de tamanho. Os arquivos `.raw` são apagados e recriados como
`.svg` (churn de renomeação, resolvido na mesma regeneração). A canonicalização
acrescenta um parse mais um serialize por snapshot — custo desprezível ante o
tempo de render do Textual.

**Neutras.** A canonicalização roda tanto sobre o SVG armazenado quanto sobre o
recém-renderizado, mantendo os dois em sincronia por construção. Um bump futuro
de Textual que altere apenas a formatação deixa de exigir regeneração de
baseline; um que altere o conteúdo visual continua, corretamente, quebrando o
teste.
