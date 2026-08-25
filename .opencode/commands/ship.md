---
description: Fan-out pre-merge (review + sicurezza + test)
---

Esegui una fan-out parallela pre-merge su: $ARGUMENTS

Lancia in parallelo gli agenti `code-reviewer`, `security-auditor` e
`test-engineer` e consolida i risultati in un verdetto go/no-go. Per contesti di
deploy coinvolgi anche `release-engineer`.
