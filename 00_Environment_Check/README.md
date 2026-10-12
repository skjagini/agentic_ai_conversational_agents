# Lab 00: How to check your setup

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/00_Environment_Check/00_environment_check.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Part E only | Follows: Day 1 step 1.2 (D1-M01-10 to D1-M01-14, slides 10–13) and the Day 2 versions slide (D2-M01-11)**

## Goal

Prove the four things every later lab assumes: the pinned packages are installed, the data files are unchanged, the
Chinook Ops API starts, and your key reaches the chat model. Each part ends with a check that passes or fails, so a
broken install shows up here and not halfway through Lab 06. The moments that teach it: a copy of the handbook with
one added line break reads the same and has a completely different hash; and the model answers a question about
Chinook's download links confidently and wrongly, because it has never seen the shop's rules.

## What you will learn

- How every lab in this repository starts, on Colab or on your own machine, and what its first two cells do.
- How to check that the installed packages match their pins, and why one pin (`langgraph`) is held back.
- How to prove a data file is unchanged with a SHA-256 hash.
- What the Chinook database holds, with SQL row counts and two customers the later labs use.
- How to start the shop's Ops API and call it over HTTP (needed from Lab 07).
- How to make one model call with your key, read its token usage and price it.

## Coming from

This is the first lab: run it before any other. You need to know a little Python and how to run a notebook cell, and
you need an OpenAI API key for Part E. Nothing about LangChain or agents is assumed; Lab 01 starts there. Every
later lab opens with this notebook's first two cells, setup and config, and relies on the checks you run here.

## What you will do

**Setup and config.** On Colab, copy the repository and install the packages; then read the model names from
`models.env` and find your key without printing it.
**Part A: Python and package versions.** Compare every installed package with its pin in `requirements.txt`.
**Part B: Data hashes.** Hash every file in `data/`, compare with `data/SHA256SUMS.txt`, and see why adding one line
break to a file breaks its hash.
**Part C: Chinook database.** Count the rows of six tables, look up Helena Holý and Puja Srivastava, and watch the
read-only database refuse an update.
**Part D: Ops API.** Start the shop's FastAPI service in the notebook, call `/health` and find Helena over HTTP.
The Day 2 labs (07 to 13) need this part.
**Part E: One model call.** Ask the chat model one question, read its token usage and price the call. Without a key
this part's cells fail; Parts A to D do not need one.
**Challenge.** Look up Puja through the API, find the largest invoice, and override a model name without editing a
file.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Python 3.13.x; 0 of 20 packages differ from their pin; langgraph 1.2.12 |
| Part B | 41 of 41 files match; handbook `d27874b8…effaea`; `chinook.db` `d6c11e2c…a18cb`; an edited copy with the same words has a different hash |
| Part C | customers 59, invoices 412, invoice_items 2240, employees 8, tracks 3503, albums 347; Helena Holý 7 invoices, 49.62, Steve Johnson; Puja Srivastava 6 invoices, 36.64, Jane Peacock; the update is refused |
| Part D | `/health` 200; `/customers?name=Helena` returns customer 6, Czech Republic, Steve Johnson; her invoices 7 and 49.62, the same as Part C; a second start reuses the server |
| Part E | a reply that does not state Chinook's 90-day download rule (ours: "7 to 30 days, depending on the provider"); `usage_metadata` with 30 input and 31 output tokens in our run and 0 reasoning tokens; model `gpt-4o-mini-2024-07-18`; about $0.000023 |

Values come from a run on 10 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`); Part E used `gpt-4o-mini`. Part E's
wording and token counts change from run to run, and from model to model if `models.env` names another one.

## Before you start

- **Colab:** use the badge above. For Part E, add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** install [uv](https://docs.astral.sh/uv/), run `uv sync` in the repository folder, copy `.env.example`
  to `.env` and fill in `OPENAI_API_KEY`. Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose
  the `.venv` kernel.
- **Data:** everything is in the repository's `data/` (see `data/README.md`). Nothing is downloaded.
- **Cost:** Part E makes one short call, a small fraction of a US cent. Parts A to D need no key.

The notebook ends with a troubleshooting table for the usual failures: a wrong kernel, a changed data file, a busy
port, a missing key.

## Resources

- [uv: working on projects](https://docs.astral.sh/uv/guides/projects/): `uv sync`, `.python-version` and the lock file
- [SQLite URI filenames](https://www.sqlite.org/uri.html): what `?mode=ro` does
- [Chinook Database](https://github.com/lerocha/chinook-database): the sample database's origin and licence
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) and [HTTPX quickstart](https://www.python-httpx.org/quickstart/): the service and the client in Part D
- [LangChain `ChatOpenAI`](https://docs.langchain.com/oss/python/integrations/chat/openai): the client in Part E
- [OpenAI: gpt-4o-mini](https://developers.openai.com/api/docs/models/gpt-4o-mini): the model's prices and limits, the values in `models.env`

Next: [Lab 01, how to build a tool-calling agent](../01_First_Chain_And_Tool/README.md). Back to [the lab list](../README.md).
