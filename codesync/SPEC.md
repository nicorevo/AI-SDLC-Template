# Spec: Codesync Scheduled XML Snapshot

## Status

Approvata dall'utente il 2026-07-28. Questa specifica autorizza la successiva
fase di pianificazione; implementazione e deploy richiedono ancora un piano
approvato.

## Objective

Codesync deve generare e conservare su disco uno snapshot XML del progetto,
aggiornarlo automaticamente a intervalli configurabili e pubblicare l'ultimo
snapshot valido senza scansionare il filesystem durante ogni richiesta `GET /`.

L'utente è una persona o un sistema che deve fornire la struttura e i contenuti
di un repository a una AI raggiungibile soltanto tramite prompt o URL.

### User stories

- Come operatore, voglio che lo snapshot sia disponibile subito dopo uno startup
  riuscito.
- Come consumatore, voglio che `GET /` risponda usando un file già pronto.
- Come operatore, voglio configurare frequenza e destinazione senza cambiare il
  codice.
- Come operatore, voglio forzare un aggiornamento e conoscere il suo risultato.
- Come consumatore, voglio continuare a ricevere l'ultimo XML valido quando una
  rigenerazione fallisce.

## Functional Requirements

### Startup

1. Durante il lifespan FastAPI, Codesync deve tentare una rigenerazione completa
   prima di dichiararsi pronto.
2. La directory di output deve essere creata se non esiste e se il processo ha i
   permessi necessari.
3. Se la generazione iniziale fallisce ma esiste già uno snapshot XML valido,
   Codesync può avviarsi in stato `degraded` e pubblicare quel file.
4. Se la generazione iniziale fallisce e non esiste uno snapshot valido, lo
   startup deve fallire: il servizio non deve dichiararsi healthy.

### Scheduled refresh

1. Il valore predefinito dell'intervallo è 180 secondi.
2. Il conteggio dell'intervallo riparte al termine di ogni tentativo, evitando
   esecuzioni sovrapposte.
3. Un intervallo pari a `0` disabilita soltanto il timer; generazione iniziale e
   refresh manuale restano attivi.
4. Valori negativi o non numerici devono causare un errore di configurazione allo
   startup.
5. Lo shutdown deve cancellare e attendere ordinatamente il task schedulato.

### Atomic snapshot

1. Il documento deve essere generato in un file temporaneo collocato nella stessa
   directory del file finale.
2. Prima della pubblicazione il documento deve essere validato come XML.
3. La sostituzione finale deve essere atomica sul filesystem locale.
4. In caso di errore, il temporaneo deve essere eliminato e il file valido
   precedente deve rimanere invariato.
5. Il percorso di output deve essere escluso esplicitamente dalla scansione,
   anche quando si trova sotto `PROJECT_ROOT`.

### HTTP API

#### `GET /`

- Legge e restituisce l'ultimo snapshot valido.
- Non avvia mai una scansione o una rigenerazione.
- Risponde `200` con `Content-Type: application/xml` quando il file è disponibile.
- Risponde `503` con un errore JSON quando nessuno snapshot valido è disponibile.
- Il parametro esistente `pretty` viene applicato solo alla risposta e non altera
  il file memorizzato.
- Il parametro esistente `cache` viene rimosso o deprecato perché lo snapshot è
  sempre la fonte della risposta.

#### `POST /refresh`

- Avvia una rigenerazione sincrona e attende il risultato.
- Risponde `200` con stato, timestamp UTC, durata in millisecondi, dimensione in
  byte e percorso dello snapshot.
- Se una rigenerazione è già in corso, risponde `409` senza avviarne una seconda.
- Se la rigenerazione fallisce, risponde `500`, registra l'errore e mantiene lo
  snapshot precedente.

#### `GET /health`

- Restituisce `ok` se l'ultimo refresh è riuscito.
- Restituisce `degraded` se l'ultimo refresh è fallito ma esiste uno snapshot
  valido.
- Espone almeno: `project_root`, `snapshot_path`, `snapshot_exists`,
  `last_success_at`, `last_attempt_at`, `last_refresh_duration_ms`,
  `snapshot_size_bytes` e `scheduler_interval_seconds`.
- Non restituisce la metrica fittizia `cache_hits`.

## Configuration

La configurazione YAML introduce una sezione `snapshot` con:

| Campo | Default | Vincolo |
| --- | --- | --- |
| `interval_seconds` | `180` | intero maggiore o uguale a zero |
| `output_path` | `data/project-context.xml` | assoluto o relativo a `codesync/` |

Le variabili d'ambiente hanno precedenza sul file YAML:

| Variabile | Campo |
| --- | --- |
| `CODESYNC_INTERVAL_SECONDS` | `snapshot.interval_seconds` |
| `CODESYNC_OUTPUT_PATH` | `snapshot.output_path` |

`PROJECT_ROOT` continua a indicare esclusivamente la directory da scansionare.
`CODESYNC_CONFIG` indica esclusivamente il file YAML. L'implementazione deve
correggere l'attuale ambiguità che tratta il percorso YAML come project root.

## Tech Stack

- Python 3.12 o successivo.
- FastAPI e lifespan asincrono esistente.
- Uvicorn come server ASGI.
- PyYAML per la configurazione.
- Libreria standard per scheduling asincrono, file temporanei, sostituzione
  atomica e validazione XML; nessuna nuova dipendenza runtime prevista.

## Commands

- Ambiente: `cd codesync && source .venv/bin/activate`
- Avvio: `python main.py --host 127.0.0.1 --port 9000 --project-root ..`
- Test: `python -m pytest -q`
- Lint: `ruff check .`
- Verifica manuale: `curl -fsS http://127.0.0.1:9000/health`
- Refresh manuale: `curl -fsS -X POST http://127.0.0.1:9000/refresh`

## Project Structure

| Percorso | Responsabilità prevista |
| --- | --- |
| `codesync/app.py` | lifespan, endpoint HTTP e stato del servizio |
| `codesync/scanner/config.py` | configurazione validata di snapshot e scanner |
| `codesync/scanner/generator.py` | produzione del contenuto XML, senza scheduling |
| `codesync/scanner/snapshot.py` | orchestrazione, lock e pubblicazione atomica |
| `codesync/tests/test_snapshot.py` | test unitari di scheduling e atomicità |
| `codesync/tests/test_app.py` | test di integrazione degli endpoint |
| `codesync/data/` | output runtime, escluso dal versionamento e dalla scansione |

## Code Style

- Type hint Python moderni e `from __future__ import annotations`.
- Funzioni e moduli in `snake_case`, classi in `PascalCase`, costanti in
  `UPPER_SNAKE_CASE`.
- Nessun file oltre 500 righe; commentare il perché, non il comportamento ovvio.
- Lo stato mutabile dello snapshot deve essere racchiuso in un componente
  dedicato, non aggiunto come ulteriori globali indipendenti in `app.py`.
- Ogni nuovo blocco di codice deve includere la marcatura AI richiesta da
  `AGENTS.md` con data di generazione.

## Testing Strategy

### Unit tests

- Parsing e precedenza YAML/variabili d'ambiente.
- Validazione di intervalli zero, negativi e non numerici.
- Scrittura temporanea, validazione XML e sostituzione atomica.
- Conservazione del file precedente quando generazione o validazione falliscono.
- Esclusione del file di output dalla scansione.
- Lock che impedisce refresh concorrenti.

### Integration tests

- Startup con generazione riuscita.
- Startup degradato con snapshot precedente valido.
- Startup fallito senza snapshot valido.
- `GET /` non invoca il generatore.
- `POST /refresh` aggiorna file e metadati.
- `POST /refresh` concorrente restituisce `409`.
- `/health` rappresenta correttamente stati `ok` e `degraded`.

### Regression and quality gates

- Tutti i test esistenti devono continuare a passare.
- Il test che prova `GET /` deve fallire se il generatore viene chiamato.
- `ruff check .` deve passare senza errori.
- Nessun test deve dipendere da attese reali di 180 secondi: tempo e sleep devono
  essere controllabili o sostituiti nei test.
- Ripartizione obiettivo: 80% unit, 15% integration, 5% end-to-end.

## Operational and Security Boundaries

### Always

- Usare un solo scheduler per processo e impedire refresh sovrapposti.
- Registrare in modo strutturato inizio, successo, errore, durata e dimensione di
  ogni tentativo.
- Servire soltanto snapshot XML validati.
- Eseguire test e lint prima di dichiarare completata l'implementazione.

### Ask first

- Aggiungere dipendenze runtime.
- Cambiare formato XML o struttura dei nodi esistenti.
- Abilitare più worker o più repliche dello stesso servizio.
- Esporre Codesync su un'interfaccia diversa da localhost.

### Never

- Cancellare l'ultimo snapshot valido dopo un refresh fallito.
- Includere lo snapshot dentro sé stesso.
- Restituire stack trace o contenuti sensibili negli errori HTTP.
- Inserire secret nel file YAML o nel codice.
- Dichiarare healthy un servizio senza alcuno snapshot valido.

## Observability

Ogni tentativo deve produrre log con causa (`startup`, `scheduled`, `manual`),
esito, durata, dimensione e timestamp. Gli errori devono includere il tipo di
fallimento senza registrare il contenuto dei file sorgente.

## Success Criteria

1. Dopo uno startup riuscito esiste un XML valido nel percorso configurato.
2. `GET /` restituisce quel file senza chiamare `generate_project_xml`.
3. Con intervallo configurato, una nuova versione sostituisce la precedente dopo
   il ciclo previsto senza sovrapposizioni.
4. Con intervallo zero non parte alcun refresh automatico.
5. `POST /refresh` aggiorna lo snapshot e restituisce metadati verificabili.
6. Un errore di refresh lascia byte-per-byte invariato lo snapshot precedente.
7. Il file XML non compare nell'albero né nei contenuti che esso descrive.
8. Configurazione YAML e override d'ambiente producono valori corretti.
9. Tutti i test passano e Ruff non segnala errori.
10. La documentazione spiega avvio, configurazione, refresh manuale e limiti di
    sicurezza.

## Risks

- Più worker avvierebbero più scheduler: il deploy MVP deve usare un worker.
- Repository grandi possono produrre snapshot troppo costosi o troppo grandi per
  un prompt; metriche e limiti saranno definiti in una specifica successiva.
- `POST /refresh` sincrono può durare diversi secondi; timeout e modalità asincrona
  saranno valutati soltanto con misure reali.
- Il servizio espone contenuti sorgente senza autenticazione; l'MVP rimane locale.

## Out of Scope

- Autenticazione e autorizzazione.
- Versionamento o storico degli snapshot.
- Filesystem watcher.
- Generazione incrementale o differenziale.
- Coordinamento multi-processo/distribuito.
- Compressione, chunking o adattamento automatico al limite token delle AI.

## Open Questions

- Quali soglie massime di durata, dimensione e memoria devono rendere il refresh
  fallito o degraded?
- Il formato della risposta `POST /refresh` dovrà diventare un contratto OpenAPI
  esplicito tramite modello Pydantic durante la pianificazione tecnica.
