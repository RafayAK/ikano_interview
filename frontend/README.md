# frontend

Astro + Tailwind UI for the Ikano onboarding sample. Server-rendered pages
that talk directly to the [backend](../backend) API from the browser. See the
[root README](../README.md) for the system-level architecture and demo
scenarios — this file covers running the frontend specifically.

## Setup

Prerequisites: Node.js 22.12+, the backend running on `http://localhost:8000`
(see [backend/README.md](../backend/README.md)).

```bash
npm ci
npm run dev -- --background
```

Use `npm run dev -- logs --follow` for logs and `npm run dev -- stop` to stop
the server. For the full Docker stack or combined local API/UI development,
see the [root development commands](../README.md#quick-start).

Open **http://localhost:4321**. `PUBLIC_API_BASE_URL` (defaults to
`http://localhost:8000/api/v1`) controls which backend it talks to.

## Project layout

```
src/
├── pages/
│   ├── index.astro     country/customer-type selector; also checks for an
│   │                    active resume-token cookie and redirects straight
│   │                    back into an in-progress application if one exists
│   ├── step/            renders the current step's form, generically, from
│   │                    the JSON Schema the backend returns for that step
│   ├── review/           shown once every step is complete; submits for a decision
│   └── result/           final decision + full audit trail
├── lib/
│   ├── api.js            fetch wrapper for the backend API (sends/receives
│   │                    the resume cookie via credentials: "include")
│   ├── form-renderer.js  builds/reads form inputs from a JSON Schema object —
│   │                    text, number, checkbox, and nested array-of-object
│   │                    fields (e.g. the business flows' beneficial owners)
│   └── progress.js       renders the step progress list
└── layouts/
    └── Layout.astro       shared shell; has the dev-only "Clear session" button
```

## Why forms are generated, not hand-written

There are six flows and ~40 distinct steps across them. Rather than hardcode
a form per country/step (which would just move the backend's "no giant
conditional" problem into the frontend), `GET .../steps/current` returns a
`schema` field, the Pydantic input model's `model_json_schema()` for
whatever that step resolves to. `form-renderer.js` walks it generically to
build the right inputs, required markers, and min/max constraints. Adding a
new step's form is a backend-only change; the frontend needs nothing.

## What's not here

No automated frontend tests, just didn't have the time. 
The full happy/rejected/manual-review paths for
all six flows were verified manually (see the root README's demo scenarios).
No client-side validation beyond HTML5 `required`/`min`/`max` — the backend's
Pydantic validation remains the single source of truth.

## 👀 Want to learn more?

Feel free to check [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).
