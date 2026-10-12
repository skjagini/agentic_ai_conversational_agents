# Lab 00: How to set up the lab environment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/00_Environment_Check/00_environment_check.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Parts D and E**

## Goal

Set up the environment every later lab assumes, and prove that each piece works: the pinned packages, the data
files, the shop's Ops API and a call to the chat model. Watch the reply to that call: it names the model that
answered, and one line in `models.env` chose that model for every lab in this repository.

## What you will learn

- How every lab in this repository starts, on Colab or on your own machine, and what its first two cells do.
- How to check that the installed packages match their pins in `requirements.txt`.
- How to prove with SHA-256 hashes that the data files are unchanged, and how to open the Chinook database read-only.
- How to start the shop's Ops API in a notebook and call it over HTTP.
- How to call the chat model with the OpenAI SDK, read the reply's text and token usage, and make the same call
  through LangChain.
- How `models.env` chooses the model for every lab, and how to change it.

## Coming from

This is the first lab: run it before any other. You need a little Python and to know how to run a notebook cell, and
an OpenAI API key for Parts D and E. Nothing about LangChain or agents is assumed; Lab 01 starts there. Every later
lab opens with this notebook's first two cells, setup and config.

## What you will do

**Setup and config.** On Colab, copy the repository and install the packages; then read the model names from
`models.env` and find your key without printing it.
**Part A: Check the installed packages.** Compare every installed package with its pin in `requirements.txt`.
**Part B: Check the data files.** Hash every file in `data/`, compare with `data/SHA256SUMS.txt`, and count the
customers in the Chinook database, opened read-only.
**Part C: Start the Ops API.** Start the shop's FastAPI service in the notebook, call `/health` and find Helena over
HTTP.
**Part D: Call the model with the OpenAI SDK.** One `client.responses.create` call; read `output_text`, the token
usage and the model that answered.
**Part E: Make the same call through LangChain.** The same question through `init_chat_model`, to prove LangChain is
installed and reaches the same model.
**Part F: Find the line that chose the model.** Print the `CHAT_MODEL` line in `models.env` next to the model that
answered both calls.
**Going further.** Add one line break to a copy of the handbook and hash it; join the Chinook tables to find the two
customers the later labs use.
**Challenge.** Look up Puja through the Ops API, and change the model without editing a file.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Python 3.13.x; 0 of 20 packages differ from their pin |
| Part B | 41 of 41 files match; handbook `d27874b8…effaea`; `chinook.db` `d6c11e2c…a18cb`; 59 customers |
| Part C | `/health` 200; `/customers?name=Helena` returns customer 6, Czech Republic, Steve Johnson |
| Part D | a few lines on how long download links last; 16 input tokens and about 140 to 190 output (ours: 141); answered by `gpt-4o-mini-2024-07-18` |
| Part E | another wording of the same kind of answer; 16 input tokens; the same model |
| Part F | `CHAT_MODEL=gpt-4o-mini` in `models.env`, the same loaded setting, and the dated model behind it in both answers |

The saved outputs come from `gpt-4o-mini` on 12 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Parts D and E
change in wording and output tokens from run to run, and from model to model if `models.env` names another one.

## Before you start

- **Colab:** use the badge above. For Parts D and E, add your OpenAI key under Secrets (the key icon in the left bar)
  as `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** install [uv](https://docs.astral.sh/uv/), run `uv sync` in the repository folder, copy `.env.example`
  to `.env` and fill in `OPENAI_API_KEY`. Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose
  the `.venv` kernel.
- **Data:** everything is in the repository's `data/` (see `data/README.md`). Nothing is downloaded.
- **Cost:** Parts D and E make one short call each, a small fraction of a US cent. Parts A to C need no key.

The notebook ends with a troubleshooting table for the usual failures: a wrong kernel, a changed data file, a busy
port, a missing key, a model name your account cannot use.

## Resources

- [uv: working on projects](https://docs.astral.sh/uv/guides/projects/): `uv sync`, `.python-version` and the lock file
- [SQLite URI filenames](https://www.sqlite.org/uri.html): what `?mode=ro` does
- [Chinook Database](https://github.com/lerocha/chinook-database): the sample database's origin and licence
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) and [HTTPX quickstart](https://www.python-httpx.org/quickstart/): the service and the client in Part C
- [OpenAI: text generation](https://developers.openai.com/api/docs/guides/text): `client.responses.create` and `output_text`, the call in Part D
- [LangChain: models](https://docs.langchain.com/oss/python/langchain/models): `init_chat_model`, the call in Part E
- [OpenAI: models](https://developers.openai.com/api/docs/models): the models you can name in `models.env`, with their prices and limits

Next: [Lab 01, how to build a tool-calling agent](../01_First_Chain_And_Tool/README.md). Back to [the lab list](../README.md).
