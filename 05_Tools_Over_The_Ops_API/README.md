# Lab 05: How to turn an API into tools an agent can call

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/05_Tools_Over_The_Ops_API/05_tools_over_the_ops_api.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Parts A and B run without one)**

## Goal

Turn an API's endpoints into typed tools an agent can call, and keep control in your code: who the rep is, what a bad
argument does, what happens when the service fails, and how many calls one run may make. The moment that teaches it:
the rep asks about Helena's "first invoice, number 466", and the model requests an invoice that does not exist. With a
tool that raises, the whole run stops on an error. With a tool that returns *Not found* as data, the model reads it,
looks up her real invoices and tells the rep that her first invoice is number 46 (3 of 3 runs on `gpt-4o-mini`).

## What you will learn

- How to call an HTTP API with `httpx` and a timeout, and tell a 200, a 404 and a connection error apart.
- How to turn a function into a `@tool`, describe an argument with a Pydantic model, and print the schema.
- How to build a lookup agent with `create_agent` and check its answer against the API in code.
- How to pass the rep's identity as context through `ToolRuntime`, so nothing typed in the chat can change it.
- How to return errors as data so the model can recover, and what happens to a malformed argument.
- How to retry a failing call with `ToolRetryMiddleware` and cap a run's calls with `ToolCallLimitMiddleware`.

## Coming from

Lab 01 built an agent that calls one tool, and Lab 03 gave it memory. The copilot still cannot see a customer or an
invoice. This lab connects it to the Ops API through tools you write. It teaches `ToolRuntime` and context itself, so
Lab 04 (self-study) is not needed first. Lab 06 then compares this agent with a fixed workflow.

## What you will do

**Part A: Call the Ops API by hand.** Find Helena, list her invoices, read an invoice that exists and one that does
not, and call a port where nothing runs: 200, 404 and a connection error.
**Part B: Write the tools.** One `api_get` helper; `find_customer` from a function and its docstring; `get_invoice`
with a Pydantic argument (`Field(gt=0)`), its schema printed and 0 refused; `get_customer_invoices`.
**Part C: Build the lookup agent.** `create_agent` with the three tools, one question followed through its messages,
and the three facts checked in code over three more runs.
**Part D: Pass the rep's identity as context.** A tool that shows a customer's invoices only to the customer's rep:
first with the rep in the prompt and in an argument, then from `ToolRuntime` context.
**Part E: Return errors the model can read.** The question about invoice 466 with a tool that raises, then with
*Not found* returned as data; the scripted model's code, then a malformed argument from it.
**Part F: Handle a failing service and cap the calls.** The API stopped, `ToolRetryMiddleware` with your own failure
message, and `ToolCallLimitMiddleware` on a scripted model that never fixes its call.
**Going further.** The same tools served over MCP with `langchain.mcp`; a name typed without its accent; whether the
model follows the "when" in a tool description.
**Challenge.** Check the rep in `get_invoice` too; a missing invoice with no customer named.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Helena: customer 6, Czech Republic, Steve Johnson; 7 invoices, 49.62, the first is 46; invoice 466: 404 `No invoice 466`; port 8799: `ConnectError` |
| Part B | `find_customer` with one string argument `name`; `get_invoice`'s schema with `"exclusiveMinimum": 0`; 0 refused with *Input should be greater than 0* |
| Part C | `find_customer`, then `get_customer_invoices` with `customer_id` 6; all three facts (3 of 3 checked runs) |
| Part D | `rep_name` as an argument: `Jane Peacock` for a passing claim, `Steve Johnson` when the message asks for it (3 of 3 each); from context with Jane signed in: *Not allowed* every time; Steve signed in: 7 invoices |
| Part E | the tool that raises: `HTTPStatusError`, no reply; *Not found* as data: the model looks up her invoices and names invoice 46 (3 of 3 runs); scripted: an error tool message, then 46 |
| Part F | API stopped: `ConnectError`; with `ToolRetryMiddleware`: *failed after 3 attempts with ConnectError*, then your own message; scripted loop: 11 model calls, 4 with `run_limit=3` |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Parts A and B and
the scripted cells give the same values every time. Model runs vary, and differ again if `models.env` names another
model: compare the tool calls and the facts, not our wording.

## Before you start

- **Lab 00 first.** It starts the Ops API this lab uses and checks your key.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db`, read in place by the Ops API (`shared/ops_api.py`), opened read-only. Nothing is
  downloaded except `fastmcp` in Going further.
- **Cost:** about 110 calls to the chat model, a few US cents with `gpt-4o-mini`.

The notebook ends with a troubleshooting table: the API not running or started by another notebook, docstring errors
in `@tool`, a 404 that stops the run, a missing `context=`, and a missing key.

## Resources

- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools): `@tool`, schemas from type hints, docstrings or a Pydantic model, and `ToolRuntime`
- [LangChain: runtime](https://docs.langchain.com/oss/python/langchain/runtime): context passed with each run, read by tools and middleware
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `ToolRetryMiddleware`, `ToolCallLimitMiddleware` and `ToolErrorMiddleware`
- [LangChain: MCP](https://docs.langchain.com/oss/python/langchain/mcp): `MCPAdapter` and tools from MCP servers
- [OpenAI: function calling](https://developers.openai.com/api/docs/guides/function-calling): the tool-calling flow, strict mode, and advice on descriptions and values your code already knows
- [Pydantic: fields](https://docs.pydantic.dev/latest/concepts/fields/): `Field`, descriptions and constraints such as `gt`
- [HTTPX: timeouts](https://www.python-httpx.org/advanced/timeouts/): what the timeout covers and how to set it

Next: [Lab 06: How to choose between a workflow and an agent](../06_Chain_And_Router/README.md). Back to [the lab list](../README.md).
