#!/usr/bin/env python3
"""
anonymize.py -- Local Data Anonymizer

Replaces sensitive strings in UTF-8 text files (.json, .txt, .md, .csv)
using deterministic rules loaded from a JSON mapping file.

No external APIs, HTTP requests, or AI/LLM services are used at runtime.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.json', '.txt', '.md', '.csv'}


def load_mapping(path_str):
    """Load and validate the JSON mapping file."""
    path = Path(path_str)
    if not path.exists():
        sys.exit(f"ERROR: Mapping file not found: {path_str}")

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: Mapping file contains invalid JSON: {e}")
    except UnicodeDecodeError:
        sys.exit(f"ERROR: Mapping file '{path_str}' is not valid UTF-8.")

    if not isinstance(data.get('replacements'), list):
        sys.exit("ERROR: Mapping file must have a top-level 'replacements' array.")

    for idx, rule in enumerate(data['replacements'], start=1):
        if not isinstance(rule, dict):
            sys.exit(f"ERROR: Rule #{idx} must be a JSON object.")
        if 'replace' not in rule:
            sys.exit(f"ERROR: Rule #{idx} is missing the 'replace' key.")
        if not isinstance(rule.get('find'), list) or not rule['find']:
            sys.exit(f"ERROR: Rule #{idx}: 'find' must be a non-empty array.")
        for jdx, entry in enumerate(rule['find'], start=1):
            if not isinstance(entry, str) or not entry:
                sys.exit(
                    f"ERROR: Rule #{idx}, find[{jdx}]: each entry must be a non-empty string."
                )

    return data


def apply_single_find(text, find, replace, case_sensitive):
    """
    Replace all non-overlapping occurrences of find in text with replace.
    Returns (new_text, count).

    The lambda in re.sub prevents backslashes in replace from being
    misinterpreted as regex backreferences (e.g. \\1, \\g<name>).
    """
    if case_sensitive:
        count = text.count(find)
        return text.replace(find, replace), count
    pattern = re.compile(re.escape(find), re.IGNORECASE)
    count = len(pattern.findall(text))
    new_text = pattern.sub(lambda _: replace, text)
    return new_text, count


def anonymize(text, mapping, verbose=False):
    """
    Apply all replacement rules to text.

    Algorithm:
      for each rule in replacements (in array order):
        for each string in rule['find'] (in array order):
          replace ALL non-overlapping occurrences, left-to-right, single pass

    Returns (result_text, stats) where stats is a list of
    (find_str, replace_str, count) for every find entry processed.
    """
    case_sensitive = mapping.get('options', {}).get('case_sensitive', False)
    stats = []

    for rule in mapping['replacements']:
        replace = rule['replace']
        for find in rule['find']:
            text, count = apply_single_find(text, find, replace, case_sensitive)
            stats.append((find, replace, count))
            if verbose and count:
                print(f"  '{find}' -> '{replace}': {count} match(es)", file=sys.stderr)

    return text, stats


def main():
    parser = argparse.ArgumentParser(
        prog='anonymize.py',
        description=(
            'Local Data Anonymizer -- replaces sensitive strings in a file\n'
            'using rules from a JSON mapping file. No external APIs are used.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python anonymize.py --mapping examples/mapping.json --input examples/note.md --output out/note.anon.md
  python anonymize.py --mapping examples/mapping.json --input examples/records.csv --output out/records.anon.csv --verbose
  python anonymize.py --mapping examples/mapping.json --input examples/data.json --output out/data.anon.json --dry-run
  python anonymize.py --mapping examples/mapping.json --input examples/log.txt --output out/log.anon.txt
        """,
    )
    parser.add_argument('--mapping', required=True, metavar='FILE',
                        help='Path to the JSON mapping file.')
    parser.add_argument('--input', required=True, metavar='FILE',
                        help='Source file to anonymize (.json, .txt, .md, .csv).')
    parser.add_argument('--output', required=True, metavar='FILE',
                        help='Destination path for the anonymized output file.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print replacement counts without writing any file.')
    parser.add_argument('--verbose', action='store_true',
                        help='Log each find->replace substitution count to stderr.')

    args = parser.parse_args()

    # Validate input path and extension
    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"ERROR: Input file not found: {args.input}")
    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        sys.exit(
            f"ERROR: '{ext}' is not a supported extension. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Load and validate mapping
    mapping = load_mapping(args.mapping)

    # Read source file as UTF-8
    try:
        source = input_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        sys.exit(f"ERROR: Input file is not valid UTF-8: {exc}")

    if args.verbose:
        n_rules = len(mapping['replacements'])
        n_finds = sum(len(r['find']) for r in mapping['replacements'])
        print(
            f"[info] Input: {len(source):,} chars | Rules: {n_rules} | Find entries: {n_finds}",
            file=sys.stderr,
        )

    # Apply replacements
    result, stats = anonymize(source, mapping, verbose=args.verbose)
    total = sum(c for _, _, c in stats)

    # Dry run: print stats and exit without writing
    if args.dry_run:
        print(f"Dry run -- {total} replacement(s) would be made. No file written.")
        for find, replace, count in stats:
            if count:
                print(f"  '{find}' -> '{replace}': {count}")
        return

    # Warn if output overwrites input
    output_path = Path(args.output)
    if output_path.resolve() == input_path.resolve():
        print(
            "WARNING: --output is the same as --input. The original file will be overwritten.",
            file=sys.stderr,
        )

    # Create output parent directory if it does not exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        output_path.write_text(result, encoding='utf-8')
    except OSError as exc:
        sys.exit(f"ERROR: Could not write output file '{args.output}': {exc}")

    print(f"Done. {total} replacement(s) applied -> {output_path}")


if __name__ == '__main__':
    main()
