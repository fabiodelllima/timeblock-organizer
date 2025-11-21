#!/usr/bin/env python3
"""Remove comentários inline de arquivos Python

OBJETIVO:
    Remove comentários inline (# e hash após código) de arquivos Python,
    preservando docstrings e estrutura do código. Usado para preparar
    código sem anotações internas para GitHub.

TRANSFORMAÇÕES:
    - Remove linhas começando com #
    - Remove # inline após código
    - Preserva docstrings (triple quotes)
    - Mantém estrutura e indentação
    - Compacta linhas vazias excessivas

USO:
    python scripts/strip-comments.py                    # Processa cli/src/timeblock/
    python scripts/strip-comments.py path/to/file.py    # Arquivo específico
    python scripts/strip-comments.py --dry-run          # Preview sem escrever

EXEMPLO:
    ANTES:  x = 42  # Comentário inline
    DEPOIS: x = 42
"""
import argparse
import sys
from pathlib import Path
from typing import List


def is_docstring_delimiter(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('"""') or stripped.startswith("'''")


def strip_comments_from_file(content: str) -> str:
    lines = content.split('\n')
    result: List[str] = []
    in_docstring = False
    docstring_delimiter: str | None = None
    previous_blank = False

    for line in lines:
        stripped = line.strip()

        if is_docstring_delimiter(line):
            if not in_docstring:
                in_docstring = True
                docstring_delimiter = '"""' if '"""' in line else "'''"
            elif docstring_delimiter is not None and docstring_delimiter in line:
                in_docstring = False
                docstring_delimiter = None

        if in_docstring or is_docstring_delimiter(line):
            result.append(line)
            previous_blank = False
            continue

        if stripped.startswith('#'):
            continue

        if '#' in line and not stripped.startswith('#'):
            in_string = False
            string_char: str | None = None
            for i, char in enumerate(line):
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                elif char == '#' and not in_string:
                    line = line[:i].rstrip()
                    break

        if not stripped:
            if previous_blank:
                continue
            previous_blank = True
        else:
            previous_blank = False

        result.append(line)

    while result and not result[-1].strip():
        result.pop()

    return '\n'.join(result)


def process_file(filepath: Path, dry_run: bool = False) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        processed = strip_comments_from_file(original)

        if original == processed:
            return False

        if dry_run:
            print(f"[DRY-RUN] Would modify: {filepath}")
            return True

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(processed)

        print(f"[MODIFIED] {filepath}")
        return True

    except Exception as e:
        print(f"[ERROR] {filepath}: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description='Strip inline comments from Python files')
    parser.add_argument('paths', nargs='*', help='Files or directories to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    args = parser.parse_args()

    if not args.paths:
        root = Path(__file__).parent.parent / 'cli' / 'src' / 'timeblock'
        if not root.exists():
            print(f"[ERROR] Default path not found: {root}", file=sys.stderr)
            sys.exit(1)
        paths: List[Path] = [root]
    else:
        paths = [Path(p) for p in args.paths]

    py_files: List[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == '.py':
            py_files.append(path)
        elif path.is_dir():
            py_files.extend(path.rglob('*.py'))

    if not py_files:
        print("[INFO] No Python files found")
        return

    modified_count = 0
    for filepath in sorted(py_files):
        if process_file(filepath, args.dry_run):
            modified_count += 1

    action = "Would modify" if args.dry_run else "Modified"
    print(f"\n[SUMMARY] {action} {modified_count}/{len(py_files)} files")


if __name__ == '__main__':
    main()
