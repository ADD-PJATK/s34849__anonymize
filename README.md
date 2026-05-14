# s34849__anonymize
Anonymizer app for extra points from student s34849

A self-contained CLI tool that redacts sensitive strings in `.json`, `.txt`, `.md`, and `.csv` files using deterministic rules loaded from a JSON mapping file.

**No external APIs, HTTP requests, or AI/LLM services are used at runtime.** All replacements are local, deterministic string substitutions using only the Python standard library.

---

## Prerequisites

- **Python 3.8 or later** — uses only the standard library, no `pip install` needed.

Verify your version:

```bash
python --version
```

---

## Installation

```bash
git clone <your-repo-url>
cd <repo-folder>
```

No additional dependencies. The script runs directly.

---

## How to Run

```bash
python anonymize.py --mapping <mapping.json> --input <source-file> --output <output-file>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--mapping FILE` | Yes | Path to the JSON mapping file |
| `--input FILE` | Yes | Source file to anonymize (`.json`, `.txt`, `.md`, `.csv`) |
| `--output FILE` | Yes | Destination path for the anonymized file |
| `--dry-run` | No | Print replacement counts without writing any file |
| `--verbose` | No | Log each find→replace count to stderr |

### Copy-pasteable examples

```bash
# Anonymize a Markdown file
python anonymize.py --mapping examples/mapping.json --input examples/note.md --output out/note.anon.md

# Anonymize a CSV file
python anonymize.py --mapping examples/mapping.json --input examples/records.csv --output out/records.anon.csv

# Anonymize a plain-text log
python anonymize.py --mapping examples/mapping.json --input examples/log.txt --output out/log.anon.txt

# Anonymize a JSON data file
python anonymize.py --mapping examples/mapping.json --input examples/data.json --output out/data.anon.json

# Preview what would change without writing (dry run)
python anonymize.py --mapping examples/mapping.json --input examples/note.md --output out/note.anon.md --dry-run

# Verbose: see each substitution logged to stderr
python anonymize.py --mapping examples/mapping.json --input examples/records.csv --output out/records.anon.csv --verbose
```

> The `out/` directory is created automatically if it does not exist.

---

## Mapping File Format

The mapping file is a **UTF-8 JSON file** with two top-level keys:

```json
{
  "replacements": [
    {
      "find": ["Anna Nowak", "A. Nowak", "NOWAK, Anna"],
      "replace": "PERSON_A"
    },
    {
      "find": ["anna@firma.test", "a.nowak@firma.test"],
      "replace": "EMAIL_A"
    }
  ],
  "options": {
    "case_sensitive": false
  }
}
```

### `replacements` (required)

An ordered array of rules. Each rule contains:

- **`find`** — a **non-empty array of strings**. Every string in this list is replaced by the same token.
- **`replace`** — a **single string**. This is the anonymized substitute for every match of any string in `find`.

### `options` (optional)

- **`case_sensitive`** — boolean, default `false`.
  - `false` → case-insensitive matching (`ANNA`, `anna`, `Anna` all match `"Anna Nowak"`)
  - `true` → only exact-case matches are replaced

### Validation: what causes an immediate exit

| Invalid input | Error |
|---------------|-------|
| `replacements` key missing or not an array | `ERROR: Mapping file must have a top-level 'replacements' array.` |
| A rule is not a JSON object | `ERROR: Rule #N must be a JSON object.` |
| A rule is missing `replace` | `ERROR: Rule #N is missing the 'replace' key.` |
| `find` missing, not an array, or empty array | `ERROR: Rule #N: 'find' must be a non-empty array.` |
| Any entry in `find` is empty or not a string | `ERROR: Rule #N, find[M]: each entry must be a non-empty string.` |
| Mapping file not found | `ERROR: Mapping file not found: <path>` |
| Mapping file is invalid JSON | `ERROR: Mapping file contains invalid JSON: <detail>` |

---

## Processing Order and Overlap Policy

### Rule order

Rules are applied in the **exact order they appear** in the `replacements` array. No sorting is performed.

### Within a rule: `find` entry order

Within each rule, the strings in `find` are applied **one at a time, in array order**. Each string triggers a complete left-to-right scan of the text as it exists **at that point** — after all prior replacements from earlier find entries in the same rule and from earlier rules.

### The algorithm

```
for each rule in replacements (in array order):
    for each find_string in rule.find (in array order):
        replace ALL non-overlapping occurrences of find_string,
        scanning left-to-right in a single pass
```

### Overlap within a single rule

Because each `find` entry in a rule is applied sequentially to the already-modified text, the first matching entry "consumes" the overlapping region before the next entry can see it.

**Example:** `find = ["ab", "bc"]`, `replace = "TOKEN"`, source = `"abc"`

1. Apply `"ab"` → text becomes `"TOKENc"`
2. Apply `"bc"` → `"bc"` no longer exists in `"TOKENc"` → no change
3. Final result: `"TOKENc"`

### Overlap between rules

Once a substring is converted to a replacement token, later rules may match the token string if it contains their `find` text. **Use distinctive, safe tokens** (e.g., `PERSON_A`, `EMAIL_01`) that cannot accidentally appear in other `find` strings.

### Multiple `find` entries in one rule (interaction)

All entries in `find` map to the same `replace` token. Because they are applied in array order:

- `find[0]` is applied first across the entire text.
- `find[1]` is applied to the result of `find[0]`, and so on.
- This means `find[1]` will never match text that was already replaced by `find[0]`.

This behavior is **deterministic** and **intentional** — it prevents double-replacement and ensures consistent output for the same inputs.

---

## Encoding

- **Input** files are read as **UTF-8**. If a file cannot be decoded as UTF-8, the program exits with a descriptive error.
- **Output** files are written as **UTF-8** (no BOM).
- The mapping file is also read as **UTF-8**.

---

## Output File Behaviour

| Scenario | Behaviour |
|----------|-----------|
| Output directory does not exist | Created automatically (including nested dirs) |
| `--output` is the same path as `--input` | Warning printed to stderr; file is overwritten |
| `--dry-run` flag set | Nothing written; replacement counts printed to stdout |
| No matches found | Output file written, identical to input; `0 replacement(s)` reported |
| Output file already exists | Silently overwritten (no prompt) |

---

## No External Services

This tool does **not** make any HTTP or HTTPS requests. It does **not** call any AI model, LLM, or cloud API (OpenAI, Anthropic, Google, or any other) to perform replacements. All masking is done with local, deterministic Python string operations using only the built-in `re`, `json`, `argparse`, `sys`, and `pathlib` modules.

---

## Before / After Example

**Input (`examples/note.md` — excerpt):**

```
- Anna Nowak (Team Lead) -- anna@firma.test -- +48 123 456 789
- Jan Kowalski (Developer) -- jan.kowalski@example.com

A. Nowak opened the meeting. NOWAK, Anna approved the final draft.
```

**Command:**

```bash
python anonymize.py --mapping examples/mapping.json --input examples/note.md --output out/note.anon.md
```

**Output (`out/note.anon.md` — same excerpt):**

```
- PERSON_A (Team Lead) -- EMAIL_A -- PHONE_01
- PERSON_B (Developer) -- EMAIL_B

PERSON_A opened the meeting. PERSON_A approved the final draft.
```

---

**Input (`examples/records.csv`):**

```
id,full_name,email,phone,address
1,Anna Nowak,anna@firma.test,+48 123 456 789,"ul. Kwiatowa 5, Warszawa"
2,Jan Kowalski,jan.kowalski@example.com,+48 987 654 321,ul. Lipowa 12
```

**Output (`out/records.anon.csv`):**

```
id,full_name,email,phone,address
1,PERSON_A,EMAIL_A,PHONE_01,"ADDRESS_01"
2,PERSON_B,EMAIL_B,+48 987 654 321,ul. Lipowa 12
```

---

## Examples Directory

| File | Description |
|------|-------------|
| `examples/mapping.json` | Six rules covering names, emails, phone, and address |
| `examples/note.md` | Markdown meeting notes with multiple sensitive references |
| `examples/records.csv` | CSV employee records with names, emails, phones, addresses |
| `examples/log.txt` | Application log entries containing sensitive data |
| `examples/data.json` | JSON project file with team and contact information |

---

## Screenshots

See the `screenshots/` folder for terminal output showing successful anonymization runs on `.md`, `.csv`, `.txt`, and `.json` files.
