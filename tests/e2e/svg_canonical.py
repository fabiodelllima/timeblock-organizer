"""Canonicalização de SVG para snapshots determinísticos (ADR-060, #69).

Normaliza a formatação que o export_screenshot() do Textual emite — layout da
tag raiz, indentação e quebras de linha entre elementos —, que varia entre
versões do Textual e entre ambientes, sem alterar o conteúdo visível. Aplicada
no serialize() do SVGSnapshotExtension, o ponto único por onde todo SVG passa
na geração do baseline e na comparação.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

# Whitespace XML puro (espaço, tab, CR, LF) — NÃO inclui nbsp (\xa0), que
# carrega o espaçamento visível dentro dos elementos <text>.
_PURE_XML_WHITESPACE = re.compile(r"^[\x20\x09\x0d\x0a]+$")


def canonicalize_svg(svg: str) -> str:
    """Reduz um SVG a uma forma canônica estável, preservando o conteúdo visível.

    Remove os nós text/tail compostos exclusivamente de whitespace XML (a
    indentação estrutural entre elementos) e aplica C14N; nós com qualquer
    conteúdo visível, inclusive nbsp, ficam intactos. É idempotente.
    """
    root = ET.fromstring(svg)
    for element in root.iter():
        if element.text is not None and _PURE_XML_WHITESPACE.match(element.text):
            element.text = None
        if element.tail is not None and _PURE_XML_WHITESPACE.match(element.tail):
            element.tail = None
    return ET.canonicalize(ET.tostring(root, encoding="unicode"))
