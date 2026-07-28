# Spec: EML Test Runner for Ingestion Pipeline

## Objective

Create a self-contained test script that takes a `.eml` file path as input and exercises the email ingestion pipeline's parsing, attachment extraction, and `extract_info_mail` functions — with all external dependencies (S3, Kafka, Exchange, DB, CContact API) mocked.

Run via CLI:
```bash
python core/test_eml_runner.py --scan docs/test_case/
# or
python core/test_eml_runner.py "docs/test_case/AGROMET BARBIANELLO - Richiesta di quotazione urgente - decorrenza 30_06 AR + RC + CAT.eml"
```

## Scope

**In scope:**
1. Parse `.eml` → mock `exchangelib.Message`
2. `save_attachments` → extract attachments into lists
3. `extract_info_mail` → produce `msg_data` 
4. `save_eml` → mock S3 upload, verify call

**Out of scope (all mocked):**
- Exchange connection, S3 upload, Kafka, DB writes, CContact API, validation flow

## Project Structure

```
microservices/os-email-ingestion/core/
├── test_eml_runner.py          ← NEW
├── mail_reader.py              ← functions under test
└── test_*.py                   ← existing, unchanged
```

## Commands

```bash
# Single EML:
python -m unittest core.test_eml_runner

# Scan all test_case EMLs:
python core/test_eml_runner.py --scan docs/test_case/

# Specific file:
python core/test_eml_runner.py docs/test_case/AGROMET\ BARBIANELLO.eml
```

## Test Scenarios

### 1. Parse → Mock Message
- Read `.eml` as bytes, build mock with all message attributes
- Verify headers (subject, from, to, cc, body, date)

### 2. Attachment Extraction (`save_attachments`)
- Unique paths for all files
- Inline vs non-inline classification
- RFC 2047 names decoded
- Correct `----` separator in file paths

### 3. `extract_info_mail`
- Returns list of `{"name": ..., "value": ...}` dicts
- Required fields present: `tep_subject`, `tep_from`, `tep_to`, `tep_body`, `tep_attachment`, `tep_messageid`
- `tep_body` sanitized (no oversized base64)
- `tep_attachment` pipe-delimited format correct

### 4. `save_eml` (mocked S3)
- Called once with correct `file_path`, `content_type`, `bucket`
- Content is non-empty bytes

### 5. Structured Output Summary
- Message metadata (subject, sender, date)
- Attachment counts (total, inline, non-inline, by type)
- msg_data field names and lengths
- S3 upload verification

## Test Data

All `.eml` files under `docs/test_case/`. Notable EMLs:

| File | What it tests |
|---|---|
| `AGROMET BARBIANELLO...` | Large EML (6MB), complex attachments |
| `I_ SEGUITI Sinistro Revo...` | Multiple inner RFC822 messages with duplicates |
| `Fwd_ Polizza REVO.eml` | Forwarded email |
| `aaaaa SIN [ref. ticket_...]` | Sinistro with ticket reference |
| `NC_OX00031003----_opec...` | PEC/S/MIME |
| `test aggressive.eml` | Edge cases |
| `----_008fed00...` | Outlook ItemAttachment |
| `Notifica apertura...CRISPY BACON` | Standard sinistri notification |

## Boundaries

- **Always**: Mock all external services
- **Always**: Python 3.8 compatible (no `:=`, no `match/case`)
- **Never**: Modify production code in `mail_reader.py`
- **Never**: Commit secrets or environment values

## Verification

1. Script runs against 3+ different EMLs without crashes
2. All assertions pass for structured data validation
3. `--scan` mode runs all EMLs, reports pass/fail summary

## Success Criteria

- [ ] Script parses any `.eml` from `docs/test_case/` and produces correct mock
- [ ] `save_attachments` produces unique paths (no overwrites)
- [ ] `extract_info_mail` returns all expected fields with correct types
- [ ] `save_eml` mock verifies correct S3 upload parameters
- [ ] `--scan` mode runs all EMLs, reports per-file results
- [ ] No real network calls or disk writes
- [ ] Runs on Python 3.8
- [ ] Existing `test_*.py` tests still pass

## Open Questions

1. Should `--scan` mode continue on error (reporting all failures) or stop at first error?
2. Should the script also verify regex extraction from subject/body for `check_nr_sinistro_subject_body` and `check_nr_polizza_subject_body`?
