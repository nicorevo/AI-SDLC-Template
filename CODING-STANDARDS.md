# Standard di Codice

## Java

- Java 21+ con record, sealed classes, pattern matching
- Maven come build system (no Gradle)
- Spring Boot 3.x come framework principale
- Naming: `camelCase` per metodi/variabili, `PascalCase` per classi
- Nessun commento ovvio; commenta solo il PERCHÉ
- Massimo 500 righe per file (Rule of 500)
- Test con JUnit 5 + AssertJ + Mockito

## C#

- .NET 8+ con record, pattern matching, nullable reference types abilitati
- SDK-style `.csproj` con `dotnet` CLI come build system
- ASP.NET Core 8.x come framework principale
- Naming: `camelCase` per variabili/parametri locali, `PascalCase` per classi/metodi/proprietà
- Nessun commento ovvio; commenta solo il PERCHÉ
- Massimo 500 righe per file (Rule of 500)
- Test con xUnit + FluentAssertions + Moq
- Dependency injection nativa di ASP.NET Core (no Autofac salvo casi eccezionali)
- OpenAPI tramite Swashbuckle o Scalar

## Node.js

- Node.js 22 LTS + TypeScript 5.x in strict mode
- `npm` come package manager (no Yarn/pnpm salvo decisione esplicita nel progetto)
- Framework: Express 5.x oppure Fastify 4.x (scegliere uno per progetto)
- Naming: `camelCase` per variabili/funzioni, `PascalCase` per classi e tipi, `UPPER_SNAKE_CASE` per costanti
- Nessun commento ovvio; commenta solo il PERCHÉ
- Massimo 500 righe per file (Rule of 500)
- Test con Vitest (unit + integration) + Supertest per le API HTTP
- Linting: ESLint flat config + Prettier; nessuna regola `any` implicita
- OpenAPI-first tramite Zod + `zod-to-openapi` oppure `@fastify/swagger`

## Python

- Python 3.12+ con type hints ovunque (`from __future__ import annotations`)
- `uv` come package/project manager (no pip diretto, no Poetry)
- Framework: FastAPI 0.11x per REST API; script/CLI con Typer
- Naming: `snake_case` per variabili/funzioni/moduli, `PascalCase` per classi, `UPPER_SNAKE_CASE` per costanti
- Nessun commento ovvio; commenta solo il PERCHÉ
- Massimo 500 righe per file (Rule of 500)
- Test con pytest + pytest-cov; `httpx` per testare le API HTTP
- Linting/formatting: Ruff (sostituisce flake8, isort, black); nessun `type: ignore` senza commento esplicativo
- OpenAPI-first automatico tramite FastAPI + Pydantic v2

## Generale

- Commit atomici compilabili
- Nessun secret nel codice sorgente
- Variabili d'ambiente per configurazione sensibile
- OpenAPI-first per tutte le API REST
