# Codesync Scheduled Snapshot

## Problem Statement

Come possiamo fornire a una AI uno snapshot XML stabile del progetto senza
scansionare il filesystem durante ogni richiesta HTTP?

## Recommended Direction

Codesync mantiene un singolo snapshot XML su disco. All'avvio genera subito un
nuovo snapshot; successivamente un task interno al processo lo rigenera a
intervalli configurabili. `GET /` pubblica esclusivamente l'ultimo file valido.

La rigenerazione usa un file temporaneo nella stessa directory e una sostituzione
atomica. Un errore non deve corrompere né rimuovere lo snapshot precedente. Un
endpoint `POST /refresh` permette inoltre di richiedere un aggiornamento manuale.

Questa direzione è preferita a cron, filesystem watcher e generazione
incrementale perché soddisfa il caso d'uso con un solo processo e senza nuova
infrastruttura.

## Key Assumptions to Validate

- [ ] Una scansione completa ogni 180 secondi ha un costo sostenibile sul
  repository target; misurare durata, dimensione e utilizzo memoria.
- [ ] In produzione viene eseguita una sola istanza dello scheduler; verificare
  la configurazione di deploy prima di abilitare più worker.
- [ ] Il processo ha accesso in scrittura alla directory dello snapshot;
  verificarlo durante lo startup.
- [ ] Pubblicare l'ultimo snapshot valido, anche se non aggiornato, è preferibile
  a rendere indisponibile il servizio.

## MVP Scope

- Snapshot iniziale durante lo startup.
- Rigenerazione completa con intervallo predefinito di 180 secondi.
- Intervallo e percorso configurabili via YAML e variabili d'ambiente.
- Snapshot predefinito in `codesync/data/project-context.xml`.
- Scrittura atomica e mantenimento dell'ultimo snapshot valido.
- `GET /`, `POST /refresh` e stato dello snapshot in `/health`.
- Possibilità di disabilitare il timer impostando l'intervallo a zero.

## Not Doing (and Why)

- Autenticazione e autorizzazione: richiedono un requisito di distribuzione
  separato; il servizio resta consigliato solo su interfaccia locale.
- Storico degli snapshot: non necessario per pubblicare il contesto corrente.
- Filesystem watcher: maggiore complessità e rischio di rigenerazioni a raffica.
- Aggiornamento XML incrementale: complesso in presenza di rinominazioni,
  cancellazioni e cambiamenti a `.gitignore`.
- Coordinamento multi-processo o distribuito: il primo rilascio supporta un solo
  scheduler attivo.

## Open Questions

- Qual è il limite massimo accettabile per dimensione e durata della scansione?
- In futuro sarà necessario proteggere gli endpoint quando esposti fuori da
  `localhost`?

