# ✈️ AI Flight Adviser — SkyScout AI

A conversational flight-discovery assistant. Chat with **SkyScout AI** in plain English ("I need to fly from Lagos to London next month, cheapest option, no more than one stop") and it gathers your preferences, looks up real airport codes, fetches live fares, and returns a reasoned travel recommendation — not just a raw list of flights.

Built with an **OpenAI tool-calling agent** wrapped in a **Gradio** chat UI.

---

## What it does

SkyScout AI behaves like an experienced travel advisor:

- **Understands intent** — collects origin, destination, dates, cabin, budget, and priorities (cheapest / fastest / best-value / flexible / eco-friendly) through natural conversation, asking follow-up questions only when something important is missing.
- **Resolves airports** — turns city names into IATA codes (e.g. `London` → `LHR, LGW, LCY`) using a bundled airport dataset.
- **Searches live fares** — calls a flight-pricing API for one-way or round-trip routes.
- **Analyzes & recommends** — evaluates price, duration, stops, layovers, baggage, refundability, and emissions, then explains *why* it recommends an option rather than dumping data.

---

## How it works

The app is a small **agentic loop**: the model decides when to call tools, the tools run locally, and their results are fed back to the model until it produces a final answer.

```
User message
   │
   ▼
Gradio chat UI  ──►  OpenAI chat completion (model = gpt-4.1-mini)
                          │  with tool definitions
                          ▼
            finish_reason == "tool_calls"? ──► yes ──► run tool locally ──┐
                          │                                               │
                          │  no                                  feed result back
                          ▼                                               │
                   Final reply  ◄───────────────────────────────────────┘
```

### The three tools the model can call

| Tool | What it does |
|------|--------------|
| `set_user_preferences` | Records/normalizes the traveler's preferences gathered so far (origin, destination, dates, cabin, budget, priority, etc.). |
| `search_airports` | Looks up airports serving a city and returns their IATA codes, from `airports.json`. |
| `get_flight_prices` | Calls the flight-pricing API for the route + date, then wraps the raw results in an *analysis prompt* the model uses to produce the recommendation. |

### Project layout

| File | Role |
|------|------|
| [main.py](main.py) | Entry point — Gradio UI, OpenAI client, and the tool-calling loop. |
| [prompts.py](prompts.py) | The `system_prompt` (SkyScout's persona/rules) and `generate_analysis_prompt()` (formats fare results for analysis). |
| [tool_definition.py](tool_definition.py) | JSON schemas describing the three tools to the OpenAI API. |
| [tools.py](tools.py) | Python implementations of the three tools, including the live fare API call. |
| [script.py](script.py) | One-off data prep — converts `airports.csv` into `airports.json` grouped by city. Run only when regenerating the dataset. |
| `airports.csv` / `airports.json` | Airport reference data (source CSV and the city-grouped JSON the app actually reads). |

---

## Getting set up

### Prerequisites
- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) — fast Python package/venv manager. Install with `pip install uv` or see the uv docs.
- An **OpenAI API key**
- An **IGNAV API key** (for the flight-pricing API)

### 1. Configure environment variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

Then edit `.env`:

```ini
OPENAI_API_KEY=sk-...      # your OpenAI key
IGNAV_API_KEY=...          # your flight-pricing API key
PORT=7860                  # optional; defaults to 7860 if omitted
```

> `.env` is gitignored and never committed — it holds your secrets.

### 2. Install dependencies

Using **uv** (recommended):

```bash
uv sync                              # installs from pyproject.toml + uv.lock (reproducible)
# or, pip-style from requirements.txt:
uv pip install -r requirements.txt
```

Or with plain pip:

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
uv run main.py
# or, without uv:
python main.py
```

The app starts on `http://localhost:7860` (or whatever `PORT` you set) and opens in your browser.

---

## Deployment (e.g. Render)

The app already binds to `0.0.0.0` and reads `PORT` from the environment, so it's host-ready.

- **Build command:** `pip install -r requirements.txt`
  *(If `uv.lock` is committed, Render auto-detects it and uses uv — that's fine and faster.)*
- **Start command:** `python main.py`
- **Environment variables:** set `OPENAI_API_KEY` and `IGNAV_API_KEY` in the host's dashboard (your `.env` is not deployed).
- **Do not** set `PORT` manually on the host — the platform injects its own, which `os.getenv("PORT", 7860)` reads automatically.

---

## Regenerating airport data (optional)

`airports.json` is already built. To rebuild it from a fresh `airports.csv`:

```bash
uv run script.py
```

This filters airports that have both an IATA code and a municipality, then groups them by city into `airports.json`.

---

## Tech stack

- **[Gradio](https://www.gradio.app/)** — chat UI
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** — LLM + tool calling (`gpt-4.1-mini`)
- **[pandas](https://pandas.pydata.org/)** — airport data prep
- **[requests](https://requests.readthedocs.io/)** — flight-pricing API calls
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — environment configuration

---

## Notes & limitations

- SkyScout **does not** sell tickets, take payments, or make reservations — it only helps discover and evaluate options.
- Prices come from a live API and are not guaranteed.
