# AI-SDLC Template

Template per avviare nuovi progetti con skill, agenti e convenzioni per lo
sviluppo assistito dall'AI. Il materiale operativo principale è in
`.opencode/`.

## Cosa viene usato nei nuovi progetti

- `.opencode/skills/`: workflow caricati on demand, ad esempio specifiche,
  TDD, debugging, sicurezza e code review;
- `.opencode/agents/`: persone specializzate e routing degli intenti;
- `.opencode/references/`: checklist consultate dalle skill;
- `AGENTS.md`: regole specifiche del progetto, da completare con comandi e
  convenzioni dello stack.
 
Le skill non devono essere caricate tutte in una sessione: l'agente sceglie
quelle pertinenti al task.

## Creare un nuovo progetto

Modalità non interattiva:

```bash
python3 clona-ai-sdlc-template.py URL_TEMPLATE NOME_PROGETTO DESTINAZIONE
```

Modalità interattiva:

```bash
python3 clona-ai-sdlc-template.py
```

Il cloner usa la branch `opcl`, rimuove la cronologia Git del template,
inizializza una nuova repository sulla branch `main` ed elimina gli artefatti
interni al template che non servono al progetto applicativo.

## Workflow consigliato

1. Definisci l'obiettivo e i vincoli.
2. Pianifica il lavoro in fette verificabili.
3. Implementa con test pertinenti e modifiche incrementali.
4. Verifica test, lint e comportamento runtime.
5. Esegui review e controlli di sicurezza prima del merge.

Per il routing dettagliato consulta `AGENTS.md`.

## Convenzioni

- `CODING-STANDARDS.md` raccoglie le convenzioni condivise per linguaggio, lasciare solo quelle utili
- `SECURITY.md` raccoglie i requisiti di sicurezza.
- I comandi di verifica specifici vanno aggiunti ad `AGENTS.md` nel nuovo
  progetto.
- Questo file puo' essere riscritto con lo scope del nuovo progetto.

## Strumenti del repository template

Il repository del template contiene anche strumenti di manutenzione e il
servizio opzionale `codesync/`. Questi componenti servono allo sviluppo del
template e non vengono copiati nei nuovi progetti dal cloner.
codesync fornisce uno snapshot xml dell'intero progetto.