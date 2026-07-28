# Implementation Plan: Codesync Scheduled XML Snapshot

## Status

Approvato e implementato il 2026-07-28. Test, lint, review automatica e verifica
runtime sono completati; resta la review umana prima di merge o deploy.

## Overview

Codesync passerà da una scansione eseguita durante `GET /` a un modello con un
singolo snapshot XML persistente. Un componente dedicato gestirà generazione,
validazione, scrittura atomica, metadati e mutua esclusione. FastAPI effettuerà il
refresh iniziale nel lifespan, avvierà un timer configurabile, servirà il file già
pronto e offrirà un refresh manuale.

## Baseline osservata

- I 14 test esistenti passano nell'ambiente virtuale.
- `ruff check .` fallisce attualmente con 28 rilievi; la feature non sarà
  considerata completa finché il baseline non sarà ripristinato.
- Il servizio genera correttamente un XML di circa 2,28 MB per questo repository.
- `CODESYNC_CONFIG` è ambiguo: il percorso YAML viene trattato come project root.
- `GET /` invoca oggi direttamente `generate_project_xml`.

## Architecture Decisions

- Un `SnapshotManager` possiede stato, lock, metadati e pubblicazione atomica;
  `app.py` non accumula nuovi globali indipendenti.
- Il timer è interno a un singolo processo e attende la fine del refresh prima di
  contare l'intervallo successivo.
- Il file viene validato prima di una sostituzione atomica nella stessa directory.
- `GET /` è privo di effetti collaterali e legge soltanto lo snapshot pubblicato.
- `POST /refresh` è sincrono; una richiesta concorrente riceve `409`.
- Non vengono aggiunte dipendenze runtime.
- Contratti di risposta e stato health saranno modelli Pydantic espliciti, così
  OpenAPI documenta il comportamento.

## Dependency Graph

1. Contratto di configurazione
2. Snapshot manager atomico, dipendente dalla configurazione
3. Startup e lettura HTTP, dipendenti dallo snapshot manager
4. Scheduler, dipendente dal lifecycle funzionante
5. Refresh manuale, dipendente da lock e metadati
6. Documentazione e quality gate, dipendenti dal flusso completo

Le attività condividono file centrali e devono essere eseguite in sequenza. Test
e documentazione possono essere preparati in parallelo soltanto dopo che il
contratto del relativo task è stabile.

## Phase 1: Configuration Foundation

### Task 1: Configurare intervallo e percorso senza ambiguità

**Description:** Separare nettamente `PROJECT_ROOT` da `CODESYNC_CONFIG` e
introdurre una configurazione snapshot immutabile con precedenza environment su
YAML. Il task parte da test fallenti per default, override e input invalidi.

**Acceptance criteria:**

- [ ] `CODESYNC_CONFIG` identifica soltanto un file YAML e non modifica il project root.
- [ ] Default, YAML e variabili d'ambiente producono intervallo e percorso risolto corretti.
- [ ] Intervalli negativi o non numerici falliscono con un messaggio di configurazione chiaro.

**Verification:**

- [ ] Test rosso iniziale documentato per l'attuale bug `CODESYNC_CONFIG`.
- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_generator.py -k config`.
- [ ] Regressione generatore: `cd codesync && .venv/bin/python -m pytest -q tests/test_generator.py`.

**Dependencies:** None.

**Files likely touched:**

- `codesync/scanner/config.py`
- `codesync/config.yaml`
- `codesync/tests/test_generator.py`

**Estimated scope:** Medium, 3 file.

### Checkpoint 1: Configuration

- [ ] Configurazione approvata rispetto alla sezione Configuration della spec.
- [ ] Test del generatore completamente verdi.
- [ ] Nessuna nuova dipendenza runtime.

## Phase 2: Persistent Snapshot

### Task 2: Pubblicare atomicamente uno snapshot valido

**Description:** Introdurre `SnapshotManager` per generare XML, validarlo, scriverlo
in un temporaneo nella directory finale e sostituire atomicamente il file. Il
manager mantiene metadati e conserva il precedente file valido dopo ogni errore.

**Acceptance criteria:**

- [ ] Un refresh riuscito crea un XML valido e metadati coerenti.
- [ ] Un errore di generazione, validazione o sostituzione lascia invariato il file precedente.
- [ ] Due refresh contemporanei non eseguono due scansioni e il secondo segnala conflitto.

**Verification:**

- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_snapshot.py`.
- [ ] I test confrontano byte-per-byte lo snapshot precedente dopo un errore.
- [ ] I test usano filesystem temporaneo e non scrivono in `codesync/data/`.

**Dependencies:** Task 1.

**Files likely touched:**

- `codesync/scanner/snapshot.py`
- `codesync/tests/test_snapshot.py`

**Estimated scope:** Small, 2 file.

### Task 3: Escludere lo snapshot dalla propria scansione

**Description:** Estendere il generatore con un'esclusione esplicita del percorso
di output, indipendente da `.gitignore`, ed esercitarla attraverso un refresh
reale del manager.

**Acceptance criteria:**

- [ ] Il file finale e ogni temporaneo associato non compaiono nell'albero XML.
- [ ] L'esclusione funziona con output relativo o assoluto collocato sotto `PROJECT_ROOT`.
- [ ] File omonimi in directory diverse non vengono esclusi accidentalmente.

**Verification:**

- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_snapshot.py -k exclusion`.
- [ ] Regressione generatore: `cd codesync && .venv/bin/python -m pytest -q tests/test_generator.py`.

**Dependencies:** Task 2.

**Files likely touched:**

- `codesync/scanner/generator.py`
- `codesync/scanner/snapshot.py`
- `codesync/tests/test_snapshot.py`

**Estimated scope:** Medium, 3 file.

### Checkpoint 2: Snapshot core

- [ ] Test di configurazione, generatore e snapshot verdi.
- [ ] Fallimenti simulati non corrompono lo snapshot precedente.
- [ ] Nessun file prodotto si include ricorsivamente.
- [ ] Review umana del confine `SnapshotManager` prima dell'integrazione FastAPI.

## Phase 3: HTTP and Lifecycle

### Task 4: Generare allo startup e servire soltanto il file

**Description:** Integrare il manager nel lifespan. Lo startup tenta un refresh,
accetta uno snapshot precedente valido in modalità degraded e fallisce se non
esiste alcun file valido. `GET /` legge il file e `/health` pubblica metadati reali.

**Acceptance criteria:**

- [ ] Startup riuscito, degraded e fallito rispettano la spec.
- [ ] `GET /` non chiama il generatore e restituisce `200` XML oppure `503` JSON.
- [ ] `/health` espone stato e metadati reali senza `cache_hits` fittizio.

**Verification:**

- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_app.py -k 'startup or root or health'`.
- [ ] Un mock rende il test `GET /` fallente se viene invocato il generatore.
- [ ] `pretty=true` restituisce XML valido senza modificare il file su disco.

**Dependencies:** Tasks 2 e 3.

**Files likely touched:**

- `codesync/app.py`
- `codesync/tests/test_app.py`
- `codesync/scanner/snapshot.py`

**Estimated scope:** Medium, 3 file.

### Task 5: Pianificare refresh periodici con shutdown ordinato

**Description:** Avviare un task asincrono dopo lo startup iniziale, attendere
l'intervallo dalla conclusione di ogni tentativo e terminarlo correttamente nel
lifespan. Il tempo deve essere controllabile nei test senza attese reali.

**Acceptance criteria:**

- [ ] Intervallo positivo produce refresh sequenziali non sovrapposti.
- [ ] Intervallo zero non crea il task automatico.
- [ ] Shutdown cancella e attende il task senza warning o lavoro residuo.

**Verification:**

- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_snapshot.py -k scheduler`.
- [ ] Test lifespan: `cd codesync && .venv/bin/python -m pytest -q tests/test_app.py -k lifespan`.
- [ ] Nessun test contiene sleep reali di durata dipendente dai 180 secondi.

**Dependencies:** Task 4.

**Files likely touched:**

- `codesync/scanner/snapshot.py`
- `codesync/app.py`
- `codesync/tests/test_snapshot.py`
- `codesync/tests/test_app.py`

**Estimated scope:** Medium, 4 file.

### Task 6: Esporre il refresh manuale con contratto OpenAPI

**Description:** Aggiungere `POST /refresh` sincrono e modelli Pydantic per
successo, conflitto ed errore. Il refresh riusa esclusivamente lock e metadati del
manager.

**Acceptance criteria:**

- [ ] Il successo restituisce timestamp UTC, durata, dimensione e percorso.
- [ ] Un refresh già in corso produce `409` senza una seconda scansione.
- [ ] Un errore produce `500` senza stack trace e mantiene disponibile il file precedente.

**Verification:**

- [ ] Test focalizzati: `cd codesync && .venv/bin/python -m pytest -q tests/test_app.py -k refresh`.
- [ ] Lo schema OpenAPI documenta `200`, `409` e `500`.
- [ ] Controllo manuale locale con `curl -fsS -X POST http://127.0.0.1:9000/refresh`.

**Dependencies:** Tasks 4 e 5.

**Files likely touched:**

- `codesync/app.py`
- `codesync/tests/test_app.py`
- `codesync/scanner/snapshot.py`

**Estimated scope:** Medium, 3 file.

### Checkpoint 3: Complete user flow

- [ ] Startup crea o recupera uno snapshot valido.
- [ ] `GET /`, `/health` e `POST /refresh` funzionano end-to-end.
- [ ] Scheduler e refresh manuale non si sovrappongono.
- [ ] Tutta la suite Python è verde.

## Phase 4: Quality and Handoff

### Task 7: Documentare l'operatività e chiudere i quality gate

**Description:** Documentare configurazione, avvio, endpoint, modalità single
worker e limiti di sicurezza. Escludere `codesync/data/` dal versionamento e
risolvere i rilievi Ruff esistenti nei file toccati o necessari al gate globale.

**Acceptance criteria:**

- [ ] README descrive YAML, override environment, refresh e comportamento degraded.
- [ ] `codesync/data/` è ignorata da Git e il servizio resta consigliato su localhost.
- [ ] Suite completa e Ruff passano senza errori; nessun artifact runtime viene versionato.

**Verification:**

- [ ] Test completi: `cd codesync && .venv/bin/python -m pytest -q`.
- [ ] Lint completo: `cd codesync && .venv/bin/ruff check .`.
- [ ] Avvio reale e verifica manuale dei tre endpoint su localhost.
- [ ] `git status --short` non mostra snapshot, temporanei o cache Python nuovi.

**Dependencies:** Tasks 1-6.

**Files likely touched:**

- `README.md`
- `.gitignore`
- `codesync/app.py`
- `codesync/main.py`
- `codesync/scanner/config.py`

**Estimated scope:** Medium, massimo 5 file.

### Checkpoint 4: Definition of Done

- [ ] Tutti i criteri della `SPEC.md` sono soddisfatti.
- [ ] Il comportamento è verificato a runtime, non soltanto dai test.
- [ ] Nuovo comportamento coperto da test red-green-refactor.
- [ ] Test esistenti senza regressioni; lint e formattazione verdi.
- [ ] Nessun codice morto, debug output o refactor estraneo.
- [ ] Contratti API, configurazione e limiti operativi documentati.
- [ ] Implicazioni di sicurezza e rollback riesaminati.
- [ ] Review umana completata prima di merge o deploy.

## Commit Strategy

Ogni task produce al massimo un commit atomico, compilabile e verificato. Messaggi
imperativi suggeriti:

1. `Add snapshot configuration contract`
2. `Write snapshots atomically`
3. `Exclude generated snapshots from scans`
4. `Serve persisted snapshots`
5. `Schedule periodic snapshot refreshes`
6. `Expose manual snapshot refresh`
7. `Document scheduled snapshot operation`

Nessun commit verrà creato senza richiesta esplicita dell'utente.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Più worker avviano scheduler duplicati | Alto | documentare e verificare un solo worker nell'MVP |
| Snapshot corrotto durante scrittura | Alto | validazione, temporaneo nella stessa directory e replace atomico |
| Refresh lento blocca il loop | Medio | esecuzione sequenziale, metriche di durata e nessuna sovrapposizione |
| Output si include ricorsivamente | Alto | esclusione per percorso assoluto con test omonimi |
| Snapshot troppo grande per il prompt | Medio | misurare e rendere visibile la dimensione; filtri fuori scope |
| Endpoint espone sorgenti sensibili | Alto | localhost come default; autenticazione fuori scope ma necessaria prima di esposizione |
| Debito Ruff nasconde regressioni | Medio | gate globale obbligatorio nel Task 7 |

## Open Questions Deferred

- Le soglie massime di durata, memoria e dimensione richiedono misurazioni dopo
  l'MVP e non bloccano l'implementazione corrente.
- Autenticazione, chunking e compressione richiedono specifiche separate.
