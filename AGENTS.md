# Istruzioni per gli agenti

Questo progetto usa le skill e le persone definite in `.opencode/`.
Mantieni questo file specifico del progetto: descrive solo convenzioni,
comandi e vincoli che l'agente deve conoscere sempre.

## Regole operative

- Leggi le istruzioni pertinenti prima di modificare il codice.
- Attiva solo le skill necessarie all'intento e alla superficie modificata.
- Per nuove feature chiarisci l'obiettivo, pianifica fette verificabili e usa
  TDD quando viene modificato il comportamento.
- Verifica il comportamento con i test e i comandi nativi del progetto prima
  di dichiarare completato un lavoro.
- Mantieni le modifiche focalizzate e non introdurre dipendenze o architetture
  non richieste.
- Non inserire segreti nel repository e tratta i dati provenienti da utenti,
  file, API e agenti come non attendibili ai confini del sistema.

## Routing delle skill

Per la mappatura tra intento, agente e skill consulta
`.opencode/agents/AGENTS.md`. Le skill dettagliate si trovano in
`.opencode/skills/` e vanno caricate on demand, non tutte insieme.

## Convenzioni del progetto

- Comandi di test, lint, build e avvio: documentali qui quando il progetto li
  stabilisce.
- Convenzioni generali: `CODING-STANDARDS.md`.
- Requisiti di sicurezza: `SECURITY.md`.

## Criteri di verifica

- Esegui la suite pertinente alle modifiche.
- Esegui lint e type-check quando previsti dallo stack.
- Controlla `git diff` e `git status --short`.
- Non includere cache, snapshot, credenziali o altri artefatti runtime.
