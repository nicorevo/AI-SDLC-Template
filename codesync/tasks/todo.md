# Todo: Codesync Scheduled XML Snapshot

## Plan gate

- [x] Piano revisionato e approvato dall'utente.

## Phase 1: Configuration

- [x] Task 1 — Configurare intervallo e percorso senza ambiguità.
- [x] Checkpoint 1 — Test di configurazione e generatore verdi.

## Phase 2: Persistent snapshot

- [x] Task 2 — Pubblicare atomicamente uno snapshot valido.
- [x] Task 3 — Escludere lo snapshot dalla propria scansione.
- [x] Checkpoint 2 — Snapshot core revisionato e verificato.

## Phase 3: HTTP and lifecycle

- [x] Task 4 — Generare allo startup e servire soltanto il file.
- [x] Task 5 — Pianificare refresh periodici con shutdown ordinato.
- [x] Task 6 — Esporre il refresh manuale con contratto OpenAPI.
- [x] Checkpoint 3 — Flusso completo verificato end-to-end.

## Phase 4: Quality and handoff

- [x] Task 7 — Documentare l'operatività e chiudere i quality gate.
- [x] Checkpoint 4 — Definition of Done completata salvo review umana finale.

## Final gate

- [x] Tutti i criteri di successo di `SPEC.md` soddisfatti.
- [x] `cd codesync && .venv/bin/python -m pytest -q` passa.
- [x] `cd codesync && .venv/bin/ruff check .` passa.
- [x] Verifica runtime locale completata.
- [ ] Review umana completata prima di merge o deploy.
