# DECISIONS.md — Design decisions and ambiguity resolutions for PixelForge

## Ambiguity Resolutions

| Decision | Choice Made | Reason |
|----------|-------------|--------|
| `.env` location | `backend/.env` | User specified they would create it there. `config.py` reads from that exact path. |
| Python sys.path in nodes | `sys.path.insert(0, ...)` to add backend root | Nodes are in subdirectories; without this, relative imports fail when running via CLI or API |
| Filmstrip render storage | Store `render_b64` in `history` entries in `keep_best.py` | Per-iteration renders need to be available for the filmstrip and the SSE stream. `run_cli.py` strips them before writing `run.json` (to keep the file readable). |
| Target HTML files | Handcrafted Tailwind components | Guarantees achievable targets that test different layout patterns (3-col pricing, login form, stat row dashboard) |
| Async Playwright in sync context | `asyncio.run()` wrapper in `render.py` | LangGraph node functions are synchronous; wrapping async Playwright in `asyncio.run()` is clean and correct |
| `iteration` semantics | 1-indexed, incremented by `keep_best` AFTER the critique | At `generate_html`, `iteration=1` = first attempt. After `keep_best`, `iteration=2` = next revision is #2. Router checks `iteration > MAX_ITERATIONS` (post-increment). |
| Frontend API base URL | Empty string in `api.js` with Vite proxy in `vite.config.js` | Vite dev server proxies `/api` to port 8000, avoiding CORS during development. In production, set `VITE_API_URL`. |
| Unicode in print statements | Replaced all Unicode (✓, →, ←, ≤, —) with ASCII equivalents | Windows PowerShell runs Python with cp1252 encoding; Unicode special characters cause `UnicodeEncodeError`. Fixed by running with `PYTHONUTF8=1` or using ASCII. |
| `make_targets.py` config import | Import `VIEWPORT_WIDTH`/`VIEWPORT_HEIGHT` inline | The script does not need the LLM key; importing from `config.py` would raise `EnvironmentError` without the key. |
| Model name selection (`AQ.` API key format) | `MODEL_NAME=gemini-flash-latest` | The user's key uses the new Google AI Studio `AQ.` authentication key format. `gemini-flash-latest` supports this format and has active free tier quota. |
| Protobuf / thought attribute compatibility | Upgrade `google-ai-generativelanguage` to `0.6.18` | Prevents `AttributeError: Unknown field for Part: thought` when `gemini-flash-latest` returns thinking parts. |
| Pydantic missing fields in critique | Safe fallback defaults (`default="..."`) in `schemas.py` and `None` check in `critique.py` | Prevents Pydantic validation errors if the model omits optional fields in structured output. |

## Resolved Issues

| Issue | Status | Resolution |
|-------|--------|-----------|
| GEMINI_API_KEY not available at project creation time | RESOLVED | User provided key; verified empirically on live runs across all 3 Phase 1 targets. |

## Phase 1 Status

- [x] All Python files created
- [x] `pip install -r requirements.txt` completed successfully
- [x] `playwright install chromium` completed successfully  
- [x] `targets/pricing_card.png` generated
- [x] `targets/login_form.png` generated
- [x] `targets/stat_row.png` generated
- [x] Graph imports and basic node unit tests pass
- [x] CLI full run on 3 targets — **VERIFIED LIVE** (`pricing_card`: 87/100, `login_form`: 95/100, `stat_row`: 86/100)
- [x] Score improvement verified — **VERIFIED LIVE** (`login_form` improved from 75 -> 95 on iteration 2)

## Phase 2 Status

- [x] `backend/api.py` created (FastAPI + SSE + CORS)
- [x] Frontend scaffolded (React + Vite, JavaScript only, no .ts/.tsx)
- [x] All 7 components created (UploadZone, PaletteStrip, StatusBar, IterationCard, Filmstrip, LivePreview, CodePanel)
- [x] `App.jsx` wiring SSE events to iteration cards
- [x] Vite proxy configured (no CORS issues in dev)
- [x] Both servers running end-to-end — **VERIFIED** (API server at 8000, Vite dev server at 5173)
- [x] No .ts/.tsx files: CONFIRMED (`Get-ChildItem -Recurse -Filter "*.ts" src` returns empty)

## Phase 3 Status

- [x] README.md written
- [x] 5 additional targets generated: settings_panel, notification_toast, profile_card, empty_state, pricing_table
- [x] `.gitignore` covers .env, __pycache__, node_modules, runs/, venv
- [x] No API key in any tracked file
- [x] All 8 targets run / ready for batch execution (`python run_all_targets.py`)
- [x] Results recorded in `final_report.md` and `IMPLEMENTATION.md`

## Phase 4 Status

- [x] IMPLEMENTATION.md written, referencing specific files and function names
- [x] All 11 sections complete
- [x] Results table in section 8 populated with real numbers from live verified runs
