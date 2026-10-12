# Lab 00: How to set up the lab environment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/00_Environment_Check/00_environment_check.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Part D**

## Goal

Get your environment ready for Lab 01. Run every cell from the top; when the last cell shows ✅ on every line, you are
ready. Two things in this lab come back in every lab: the two cells each lab starts with, and the line in
`models.env` that picks the model.

## What you will learn

- How every lab in this repository starts, on Colab or on your own machine, and what its first two cells do.
- How to check in one run that your packages, the data files, the shop's Ops API and your key all work.
- How to find what a failed check means and fix it with the troubleshooting table.
- How `models.env` chooses the model for every lab, and how to change it for every lab or only on your machine.

## Coming from

This is the first lab: run it before any other. You need a little Python and to know how to run a notebook cell, and
an OpenAI API key for Part D. Nothing about LangChain or agents is assumed; Lab 01 starts there.

## What you will do

**Setup and config.** The two cells every lab opens with: on Colab, copy the repository and install the packages;
then read the model names from `models.env` and find your key without printing it.
**Part A: Check the packages.** One cell compares every installed package with its pin in `requirements.txt`.
**Part B: Check the data files.** One cell hashes every file in `data/` and compares with `data/SHA256SUMS.txt`.
**Part C: Check the Ops API.** One cell starts the shop's service in the notebook, asks `/health` and stops it.
**Part D: Check that the model answers.** One question to the chat model with OpenAI's library.
**Part E: Find the line that chose the model.** The `CHAT_MODEL` line in `models.env` beside the model that answered,
and `load_settings`, the helper that reads it.
**Check that you are ready.** One ✅ or ❌ per part.
**Challenge.** Change the model without editing a file.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Python 3.13.x; 20 pinned packages, 0 different |
| Part B | 41 of 41 files match; changed: none |
| Part C | `200 {'status': 'ok'}` |
| Part D | a reply in any wording (ours: how long links usually last), answered by `gpt-4o-mini-2024-07-18` |
| Part E | `CHAT_MODEL=gpt-4o-mini` in `models.env`, the same loaded setting, and the dated model behind it |
| The last cell | ✅ on all four lines |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Part D's wording
changes from run to run, and from model to model if `models.env` names another one.

## Before you start

- **Colab:** use the badge above. For Part D, add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** install [uv](https://docs.astral.sh/uv/), run `uv sync` in the repository folder, copy `.env.example`
  to `.env` and fill in `OPENAI_API_KEY`. Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose
  the `.venv` kernel.
- **Data:** everything is in the repository's `data/` (see `data/README.md`). Nothing is downloaded.
- **Cost:** Part D makes one short call, a small fraction of a US cent. Parts A to C need no key.

The notebook ends with a troubleshooting table for the usual failures: a wrong kernel, a changed data file, a busy
port, a missing key, a model name your account cannot use.

## Resources

- [uv: working on projects](https://docs.astral.sh/uv/guides/projects/): `uv sync`, `.python-version` and the lock file
- [Python `hashlib`](https://docs.python.org/3/library/hashlib.html): the SHA-256 hashes in Part B
- [Chinook Database](https://github.com/lerocha/chinook-database): the sample database's origin and licence
- [OpenAI: text generation](https://developers.openai.com/api/docs/guides/text): `client.responses.create` and `output_text`, the call in Part D
- [OpenAI: models](https://developers.openai.com/api/docs/models): the models you can name in `models.env`, with their prices and limits

Next: [Lab 01: How to build a tool-calling agent](../01_First_Chain_And_Tool/README.md). Back to [the lab list](../README.md).
