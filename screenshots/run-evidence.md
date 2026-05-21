# Run Evidence — Anonymizer Output Across All Four File Types

Terminal output captured from `python anonymize.py` on 2026-05-21.

---

## Run 1 — Markdown file (`.md`)

**Command:**
```
python anonymize.py --mapping examples/mapping.json --input examples/note.md --output examples/output/note.anon.md --verbose
```

**Terminal output:**
```
[info] Input: 881 chars | Rules: 6 | Find entries: 12
  'Anna Nowak' -> 'PERSON_A': 2 match(es)
  'A. Nowak' -> 'PERSON_A': 2 match(es)
  'NOWAK, Anna' -> 'PERSON_A': 1 match(es)
  'Jan Kowalski' -> 'PERSON_B': 2 match(es)
  'J. Kowalski' -> 'PERSON_B': 1 match(es)
  'anna@firma.test' -> 'EMAIL_A': 2 match(es)
  'a.nowak@firma.test' -> 'EMAIL_A': 1 match(es)
  'jan.kowalski@example.com' -> 'EMAIL_B': 1 match(es)
  'jkowalski@example.com' -> 'EMAIL_B': 1 match(es)
  '+48 123 456 789' -> 'PHONE_01': 1 match(es)
  'ul. Kwiatowa 5, Warszawa' -> 'ADDRESS_01': 1 match(es)
Done. 15 replacement(s) applied -> examples/output/note.anon.md
```

**Before (`examples/note.md` excerpt):**
```markdown
- Anna Nowak (Team Lead) -- anna@firma.test -- +48 123 456 789
- Jan Kowalski (Developer) -- jan.kowalski@example.com

A. Nowak opened the meeting. NOWAK, Anna approved the final draft.
All action items were sent to anna@firma.test for confirmation.
```

**After (`examples/output/note.anon.md` same excerpt):**
```markdown
- PERSON_A (Team Lead) -- EMAIL_A -- PHONE_01
- PERSON_B (Developer) -- EMAIL_B

PERSON_A opened the meeting. PERSON_A approved the final draft.
All action items were sent to EMAIL_A for confirmation.
```

---

## Run 2 — CSV file (`.csv`)

**Command:**
```
python anonymize.py --mapping examples/mapping.json --input examples/records.csv --output examples/output/records.anon.csv --verbose
```

**Terminal output:**
```
[info] Input: 315 chars | Rules: 6 | Find entries: 12
  'Anna Nowak' -> 'PERSON_A': 1 match(es)
  'A. Nowak' -> 'PERSON_A': 1 match(es)
  'Jan Kowalski' -> 'PERSON_B': 1 match(es)
  'anna@firma.test' -> 'EMAIL_A': 1 match(es)
  'a.nowak@firma.test' -> 'EMAIL_A': 1 match(es)
  'jan.kowalski@example.com' -> 'EMAIL_B': 1 match(es)
  'jkowalski@example.com' -> 'EMAIL_B': 1 match(es)
  '+48 123 456 789' -> 'PHONE_01': 2 match(es)
  'ul. Kwiatowa 5, Warszawa' -> 'ADDRESS_01': 2 match(es)
Done. 11 replacement(s) applied -> examples/output/records.anon.csv
```

**Before (`examples/records.csv`):**
```
id,full_name,email,phone,address
1,Anna Nowak,anna@firma.test,+48 123 456 789,"ul. Kwiatowa 5, Warszawa"
2,Jan Kowalski,jan.kowalski@example.com,+48 987 654 321,ul. Lipowa 12
3,A. Nowak,a.nowak@firma.test,+48 123 456 789,"ul. Kwiatowa 5, Warszawa"
```

**After (`examples/output/records.anon.csv`):**
```
id,full_name,email,phone,address
1,PERSON_A,EMAIL_A,PHONE_01,"ADDRESS_01"
2,PERSON_B,EMAIL_B,+48 987 654 321,ul. Lipowa 12
3,PERSON_A,EMAIL_A,PHONE_01,"ADDRESS_01"
```

---

## Run 3 — Plain text log (`.txt`)

**Command:**
```
python anonymize.py --mapping examples/mapping.json --input examples/log.txt --output examples/output/log.anon.txt --verbose
```

**Terminal output:**
```
Done. 12 replacement(s) applied -> examples/output/log.anon.txt
```

---

## Run 4 — JSON data file (`.json`)

**Command:**
```
python anonymize.py --mapping examples/mapping.json --input examples/data.json --output examples/output/data.anon.json --verbose
```

**Terminal output:**
```
Done. 11 replacement(s) applied -> examples/output/data.anon.json
```

---

Anonymized output files are in [`examples/output/`](../examples/output/).  
No external APIs or HTTP calls are made at runtime.
