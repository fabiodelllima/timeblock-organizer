"""Testes da canonicalização de SVG do serialize() de snapshot (ADR-060, #69)."""

from __future__ import annotations

import re

from svg_canonical import canonicalize_svg

# SVG mínimo que cobre o essencial: namespace padrão, indentação estrutural,
# atributos, e nbsp no conteúdo visível (o espaçamento do card do timer).
_SVG = (
    '<svg class="rich-terminal" xmlns="http://www.w3.org/2000/svg">\n'
    "    <style>.r1 { fill: #cdd6f4 }</style>\n"
    "    <g>\n"
    '        <text class="r1" x="10">em&#160;andamento&#160;&#160;Leitura</text>\n'
    "    </g>\n"
    "</svg>\n"
)


def test_canonicalize_is_idempotent() -> None:
    once = canonicalize_svg(_SVG)
    assert canonicalize_svg(once) == once


def test_canonicalize_normalizes_structural_whitespace() -> None:
    reformatted = re.sub(r">[\x20\x09\x0d\x0a]+<", "><", _SVG)
    assert canonicalize_svg(_SVG) == canonicalize_svg(reformatted)


def test_canonicalize_preserves_visible_text_and_nbsp() -> None:
    result = canonicalize_svg(_SVG)
    assert "andamento" in result
    assert "Leitura" in result
    idx = result.find("Leitura")
    # os dois nbsp que precedem "Leitura" (espaçamento do card) permanecem
    assert result[idx - 2 : idx] == "\u00a0\u00a0"
