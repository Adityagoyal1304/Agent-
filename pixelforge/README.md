# Shot2Code

> An AI agent that converts a UI screenshot into HTML by watching its own rendered output and correcting itself.

![Filmstrip example](docs/filmstrip_example.png)

## What it does

Shot2Code implements a **self-correcting feedback loop** for screenshot-to-code generation:

1. **Generate** — A vision model converts the target screenshot to a single-file Tailwind HTML page
2. **Render** — Playwright renders the HTML headlessly in Chromium at 1280×800
3. **Critique** — The model compares the render vs the target, scoring 0-100 and listing up to 6 specific discrepancies
4. **Revise** — The model applies only the called-out fixes (no regeneration from scratch)
5. **Repeat** — Until score ≥ 85 or 5 attempts are used

The result is a single self-contained HTML file that uses the Tailwind CDN.

## Architecture

```
START → extract_palette → generate_html → render_html → critique_render
      → keep_best ──────────────────────────────────────────────────────→ END
             └──────────── (if score < 85 and iterations < 5) ──────────┘
                                     (back to generate_html)
```

- **2 of 6 nodes** call a model (`generate_html`, `critique_render`)
- **4 of 6 nodes** are pure code (faster, deterministic, zero API cost)
- The cycle (back-edge from `keep_best` to `generate_html`) is what makes this a **graph, not a chain**

## Results

| Target | Start Score | Final Score | Iterations | ~Time |
|--------|------------|-------------|------------|-------|
| pricing_card | ~45 | ~85 | 3–5 | ~90s |
| login_form | ~55 | ~85 | 2–4 | ~70s |
| stat_row | ~40 | ~80 | 3–5 | ~90s |

*Times vary with API response latency.*

## Install

### Requirements
- Python 3.11+
- Node.js 18+

### Backend setup

```bash
cd pixelforge/backend
pip install -r requirements.txt
python -m playwright install chromium

# Copy and fill in your API key
cp .env.example .env
# Edit .env: GEMINI_API_KEY=your_key_here
```

### Generate target screenshots

```bash
python make_targets.py        # pricing_card, login_form, stat_row
python make_more_targets.py   # 5 additional targets for Phase 3
```

### Run the CLI

```bash
python run_cli.py targets/pricing_card.png
```

Output goes to `runs/<timestamp>_pricing_card/`:
- `best.html` — highest-scoring HTML
- `filmstrip.png` — horizontal strip of all attempts
- `iteration_N.html` / `iteration_N.png` — per-iteration artifacts
- `run.json` — scores, timing, discrepancy logs

### Run the web UI

**Terminal 1 — Backend:**
```bash
cd pixelforge/backend
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd pixelforge/frontend
npm install
npm run dev
```

Open `http://localhost:5173`, drop in a screenshot, click Start Run.

### Docker

```bash
docker-compose up
```

## Limitations

- **Single viewport only** — no responsive breakpoints tested
- **No component decomposition** — entire page in one HTML file
- **No image assets** — images are replaced with grey placeholder divs
- **No font matching** — uses Tailwind's default sans-serif
- **Works best on components, not full pages** — complex full-page layouts can exceed the model's context window for revision
- **Score can oscillate** — the critic is a model and is not perfectly consistent

## Project structure

```
pixelforge/
  backend/
    config.py          — constants and env loading
    schemas.py         — Pydantic Critique / Discrepancy models
    llm.py             — LLM factory (swap provider by changing env var)
    prompts.py         — Generator and critic system prompts
    graph/
      state.py         — GraphState TypedDict
      builder.py       — LangGraph with conditional cycle
      nodes/
        palette.py     — Pure Python colour extraction (Pillow)
        generate.py    — Multimodal HTML generator
        render.py      — Playwright headless renderer
        critique.py    — Vision model structured critic
        keep_best.py   — Best-score tracking and iteration log
    utils/
      images.py        — Base64 helpers and filmstrip builder
    api.py             — FastAPI with SSE streaming
    run_cli.py         — CLI with streaming output
    make_targets.py    — Generate Phase 1 targets
    make_more_targets.py  — Generate Phase 3 targets
  frontend/
    src/
      App.jsx          — Main layout
      api.js           — Fetch + EventSource wrappers
      components/
        UploadZone.jsx, PaletteStrip.jsx, StatusBar.jsx
        IterationCard.jsx, Filmstrip.jsx, LivePreview.jsx, CodePanel.jsx
  targets/             — Input screenshots (8 total)
  runs/                — Generated output (gitignored)
  DECISIONS.md         — Design decisions and ambiguity log
  IMPLEMENTATION.md    — Technical deep-dive for interviews
```
