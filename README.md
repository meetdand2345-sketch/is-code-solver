# IS Code Solver

Answer structural / RCC engineering questions and get a **step-by-step solution with
the exact Indian Standard (IS) code clause references** for every step — in **English or
Hindi**. The app also ships a **built-in IS code library** with links to open each code.

Built with **FastAPI**. Solvers are deterministic (rule-based) — not a language model —
so the numbers and clause references are reproducible and auditable.

```
 Question  ──►  intent + parameter parser  ──►  rule-based solver  ──►  steps + IS clauses + links
```

## What it does

- **Ask a question** in plain English or Hindi, e.g.
  *"Design a simply supported beam, b=300 mm, D=500 mm, fck=25, fy=500, Mu=120 kNm"*.
  The app detects the problem type, extracts the values, and returns the full solution.
  If values are missing, it tells you exactly which ones it needs.
- **Design Tools** — pick a problem and fill a form for a guaranteed precise solve.
- **IS Code Library** — the codes the app draws on, with clause summaries and links to a
  public reference copy and the official BIS source.
- **Bilingual** — toggle English / हिंदी. Every step, summary and warning is translated.

### Supported problem types (initial scope — RCC / structural)

| Type | What it solves | Key IS clauses |
|------|----------------|----------------|
| `beam_flexure` | Singly reinforced rectangular beam: Mu vs Mu,lim, area of tension steel, bar selection, deflection | IS 456 Cl. 38.1, Annex G-1.1, 26.5.1.1, 23.2.1 |
| `slab_oneway` | One-way slab: depth from span/depth, loads, Mu, main + distribution steel, spacing | IS 456 Cl. 22.2, 23.2.1, 24.1, 26.5.2.1, 26.3.3 |
| `shear` | Beam shear: τv, τc (Table 19), τc,max (Table 20), stirrup spacing | IS 456 Cl. 40.1, 40.2, 40.4, 26.5.1.5, 26.5.1.6 |
| `development` | Development length Ld and lap length | IS 456 Cl. 26.2.1, 26.2.1.1, 26.2.5.1 |
| `loads` | Factored design load and load combinations | IS 456 Cl. 36.4.1 (Table 18), IS 875 Parts 1/2/5 |
| `column_axial` | Short axially loaded column: required steel or capacity check | IS 456 Cl. 39.3, 26.5.3.1 |

### Codes in the library

- **IS 456:2000** — Plain and Reinforced Concrete — Code of Practice
- **IS 1786:2008** — High Strength Deformed Steel Bars and Wires for Concrete Reinforcement
- **IS 875 (Part 1):1987** — Dead Loads (unit weights)
- **IS 875 (Part 2):1987** — Imposed Loads
- **IS 875 (Part 3):2015** — Wind Loads
- **IS 875 (Part 4):1987 (rev. 2021)** — Snow Loads
- **IS 875 (Part 5):1987** — Special Loads and Load Combinations

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. Interactive API docs are at `/docs`.

### Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | The web app |
| GET | `/api/health` | Liveness probe |
| GET | `/api/codes` | Full IS code library |
| GET | `/api/codes/{code_id}` | One code with its clause index |
| GET | `/api/problem-types` | Catalogue + form fields |
| POST | `/api/solve` | `{"type": "...", "inputs": {...}, "lang": "en"}` |
| POST | `/api/ask` | `{"question": "...", "lang": "hi"}` |

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"shear design of a beam b=250 d=450 Vu=90 kN Ast=942 fck=20 fy=415"}' | jq
```

## Deploy

The repo includes a `Dockerfile` and a `render.yaml` blueprint.

- **Render / Railway / Fly / HF Spaces:** the container reads `$PORT` automatically —
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Docker:**
  ```bash
  docker build -t is-code-solver .
  docker run -p 8000:8000 is-code-solver
  ```

## Project layout

```
app/
  main.py            FastAPI app and routes
  codes/library.py   IS code metadata, clause index, open-links
  solvers/
    common.py        shared helpers + IS 456 tables (19, 20, bond, xu,max)
    registry.py      problem-type catalogue, dispatcher, question parser
    flexure.py  slab.py  shear.py  development.py  loads.py  column.py
  static/            index.html, style.css, app.js (the web UI)
tests/               pytest suite
```

## Scope and correctness notes

- The solvers implement the **limit state method** of IS 456:2000. Clause numbers and table
  values were taken from the code text (see `app/codes/library.py`).
- This is a **reference / study tool for preliminary design**. It is **not** a substitute for
  the judgement of a licensed structural engineer, and results must be verified against the
  current BIS codes before any real construction use.
- The clause links point to publicly available reference copies and to the official BIS
  e-sale pages. The **authoritative text is always the one published by BIS**.
- Scope is intentionally limited to the RCC problem types above. Extending it means adding a
  solver module and registering it in `app/solvers/registry.py`.

## License

MIT — see `LICENSE`.
