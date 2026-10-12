# Lab 07: How to turn an API into tools an agent can call

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/07_Tools_Over_The_Ops_API/07_tools_over_the_ops_api.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Parts A and B run without one) | Follows: Day 2 D2-M02, steps 2.1 to 2.6 (D2-M02-01 to D2-M02-47, slides 13–54)**

## Goal

Turn the Ops API's endpoints into typed tools, let the copilot use them, and keep control in your code: the rep's
identity comes from your app, and every failure comes back as text the model can act on. The moment that teaches it:
asked about "Helena Holy" without the accent, the copilot answered that no such customer exists in 3 of 3 runs, with
no error anywhere, because the tool gave it an empty list and no hint of what to try next.

## What you will learn

- How to call an HTTP API with `httpx` and a timeout, and read its status codes, its bodies and a connection error.
- How to turn a Python function into a typed `@tool`, print the schema the model receives, and give an argument a
  fixed list of values.
- How to follow one question through the five steps of a tool call, check the reply against the API in code, and
  write tool results the model can act on when a search finds nothing.
- How to keep the rep's identity in `ToolRuntime` context, where nothing the rep types can change it.
- How the loop handles a malformed argument, a model that never fixes it, and the same request sent twice: schema
  validation, a call limit and an idempotency key.
- How to write two tool schemas of your own, and test whether the model follows the "when" in a description.

## Coming from

You have built an agent that calls one tool (Lab 01) and searches the handbook with citations (Lab 06). The copilot
still cannot see a customer or an invoice. This lab connects it to the Ops API through tools you write, and Lab 08
then makes it wait for a person before it writes.

## What you will do

**Part A: Call the Ops API directly.** Find Helena, list her invoices, read three invoices (Chinook, course fixture,
missing) and call a port where nothing runs: 200, 404 and a connection error.
**Part B: Write the read tools.** Write one HTTP helper and three typed tools, print the schema the model receives,
check that yours match the ones kept in `shared/ops_tools.py`, and read the write tool's enum and hidden `runtime`.
**Part C: Let the copilot look up a customer.** Run the lookup agent, map its messages to the five steps, check the
three facts in code over four runs, then ask about "Helena Holy" and fix the tool so the copilot finds her.
**Part D: Keep the rep's identity out of the model's hands.** Steve asks to file ticket 14's refund under his id
while Jane is signed in: with `rep_id` as an argument and with the rep from `ToolRuntime` context, three runs each;
read the filed requests back.
**Part E: Control what runs.** A malformed argument from a scripted model and the error it reads, the same question
on the real model, a loop stopped by `ToolCallLimitMiddleware`, and the API's own rules: an idempotency key sent
twice, an amount above the total, a number in words, a request over 100 dollars.
**Part F: Write two tool schemas.** Write `get_ticket` and `send_new_download_link`, mark the write and its controls,
and count over five runs whether the model follows *Use only after the 90 days*.
**Challenge.** Retry a tool that raises while the API is down, and add a fifth read tool for refund requests.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Helena: customer 6, Czech Republic, Steve Johnson; 7 invoices, 49.62; invoice 9001: 9.99 on 2013-11-02, `"source": "course fixture"`; 99999: 404 `No invoice 99999`; port 8799: `ConnectError` |
| Part B | `find_customer` with one string argument `name`; `same: True` for all four comparisons with `shared/ops_tools.py`; `file_refund_request` arguments `['invoice_id', 'amount', 'reason']`, reason enum `['duplicate_charge', 'damaged_media', 'other']`, runtime hidden: `True` |
| Part C | `find_customer`, then `get_customer_invoices` with `customer_id` 6, three model calls, all three facts (ours: 4 of 4 runs, 3.2 s for the first); "Helena Holy": `find_customer` returns `'[]'` and the copilot says it cannot find her (ours: 3 of 3); with `find_customer_v2` it searches again with "Helena" and answers 7 invoices (ours: 3 of 3) |
| Part D | `rep_id` as an argument: the model sends `rep-5` (ours: 3 of 3); from context: three arguments, no rep id, requests 1 to 3 all `rep-42`, `pending_review`; a scripted call that adds `"rep_id": "rep-5"` files for `rep-42` |
| Part E | scripted: *Input should be a valid integer ... Please fix the error and try again.*, then 9001, messages per call `[1, 3, 5]`; real model sends `9001` (ours: 3 of 3); no limit: 11 model calls; `run_limit=3`: 4 model calls and *run limit exceeded (4/3 calls)*; same key twice: 201 then 200 with `"replayed": true` and the same request (ours: 5); 19.98: 422; `"four hundred"`: 422; 120.00: 201, `needs_manager` |
| Part F | `get_ticket` returns ticket 2; `send_new_download_link` shows `['customer_id', 'invoice_id']`; a new link proposed after 100 days 5 of 5, for the 20-day new-laptop question 5 of 5 with either description, for "how long" 1 of 5 (weak) and 0 of 5 (with when) |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Parts A and B and
the scripted cells give the same values every time. Model runs vary: compare the tool calls, the facts and the API's
records, not our wording. If `models.env` names another model, expect different counts in Parts C to F.

## Before you start

- **Lab 00 first.** Its Part D starts the Ops API this lab uses, and its Part E proves your key works.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db`, the handbook index in `data/index/` and the tickets in `data/corpus/`, read in place.
  Invoices 9001–9003 are a course fixture inside `shared/ops_api.py`. The Ops API writes refund requests to a
  temporary database, never to `chinook.db`.
- **Cost:** about 95 `gpt-4o-mini` calls and a few embedding calls: a few US cents at most.

The notebook ends with a troubleshooting table: the API not running, docstring and type-hint errors in `@tool`, a
missing `context=`, a validation error the model reads, a replayed request, and a missing key.

## Resources

- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools): `@tool`, schemas from type hints and docstrings, and `ToolRuntime` (the `runtime` parameter is hidden from the model)
- [LangChain: runtime](https://docs.langchain.com/oss/python/langchain/runtime): context passed with each run, read by tools and middleware
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `ToolCallLimitMiddleware`, `ToolRetryMiddleware` and `ToolErrorMiddleware`
- [OpenAI: function calling](https://developers.openai.com/api/docs/guides/function-calling): the tool-calling flow, strict mode, and advice on descriptions, enums and values your code already knows
- [HTTPX: timeouts](https://www.python-httpx.org/advanced/timeouts/): what the timeout covers and how to set it
- [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests): how a payments API uses idempotency keys for safe retries

Next: [Lab 08, how to make an agent wait for approval](../08_Approval_Before_A_Write/README.md). Back to [the lab list](../README.md).
