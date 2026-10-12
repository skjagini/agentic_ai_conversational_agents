# Lab 10: How to measure an agent's latency and cost

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/10_Latency_Streaming_And_Cost/10_latency_streaming_and_cost.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Follows: Day 2 D2-M05, steps 5.1 to 5.7 (D2-M05-01 to D2-M05-37, slides 126–161)**

## Goal

Measure an agent from your own runs: time to first token and total time over ten runs (p50 and p95), the share of
each turn spent in the model and in tools, a ledger of every model call with its tokens, and the cost of a resolved
case, with the prompt cache read correctly. The moments that teach it: a timer that waited for the first text stopped
at 1.18 s on the tool's JSON, while the rep's first words came at 2.45 s in the next run; a download-link question was
answered in about a second in 5 of 5 runs because the copilot skipped the handbook, and no reply gave the rule; the
saved thread showed 4 of a conversation's 9 model calls and 40% of its cost; and a long prompt was read from the cache
in 1 of 5 calls without a `prompt_cache_key` and 5 of 5 with one. All from `gpt-4o-mini`, 12 Oct 2026.

## What you will learn

- How to time a streamed reply with `stream_mode="messages"` and `version="v2"`: time to first token against total
  time, and why only the model's own text counts as the first words.
- How to report p50 and p95 over ten runs for a direct answer and a tool-using answer, and what ten runs cannot tell
  you.
- How to keep a ledger of every model call and tool call with a callback, and split a turn's seconds into model time
  and tool time.
- How to count the calls a middleware makes, which the saved thread does not show, and tag runs with the rep and the
  feature so a cost can be attributed.
- How to price a call, a conversation and a resolved case from `usage_metadata` and the prices in `models.env`,
  cached tokens included.
- How to tell when OpenAI's prompt cache was used, below and above 1,024 tokens, and how a `prompt_cache_key` changes
  it.

## Coming from

Lab 09 compared a chain, a router and an agent by counting calls and tokens with `Meter`, a callback that adds up a
run. This lab measures the copilot itself: seconds as the rep feels them, one row per call, and money. It imports the
tools from `shared/ops_tools.py` and the handbook from `shared/copilot.py`, so you can start here. You need Lab 01's
`usage_metadata`, Lab 03's `SummarizationMiddleware` and Lab 08's approval.

## What you will do

**Part A: Time one streamed reply.** Time `invoke`, then stream the same reply and read what each streamed item holds;
time the first chunk, the first text and the total; compare `invoke` and `stream` over five runs; catch a timer that
counts the tool's JSON as the first words, fix it, and see the same turn through `stream_events(version="v3")`.
**Part B: Report p50 and p95 over ten runs.** Write nearest-rank percentiles by hand, run a direct and a tool-using
question ten times each, chart them, and check what a fast run actually answered.
**Part C: Keep a ledger of every call.** Start from Lab 09's `Meter`, write a `Ledger` with one row per model call and
tool call, and split five turns into model time and tool time.
**Part D: Count the calls you do not see.** Run five turns through a summarising copilot and count them from the saved
thread and from the ledger; tag runs with rep, feature and thread; optionally send one run to LangSmith.
**Part E: Price a call, a thread and a resolved case.** Read the prices from `models.env`, price a call by hand and
with `call_cost`, price a ten-turn practice ledger, and resolve ticket 14 three times end to end, approval included.
**Part F: Read the prompt cache.** Send a short and a long prompt five times each, with and without a
`prompt_cache_key`, and price what a cache read saves.
**Part G: Choose the first cost control to add.** Put the measurements in one table, choose a control, and run
`ModelCallLimitMiddleware` on a thread.
**Challenge.** A token budget per thread with a handover message, streamed progress lines, and how steady p95 is.

## Checkpoints

| After | You should see |
|---|---|
| Part A | a direct reply's first text well before its total (ours: 0.56 s of 0.92 s); `invoke` and `stream` with about the same median total (0.90 s and 0.95 s); a "first text" from the `tools` node, then the fixed timer's first text after both tool calls (ours: 2.45 s) |
| Part B | `pct` gives p50 1.0 and p95 4.2 on the made-up times; first text p50/p95 direct 0.59/0.70 s, tool 2.53/3.31 s with 2 tool calls in every run; the download-link question in about a second with no tool call and no rule (5 of 5) |
| Part C | `Meter`: 3 calls, 2,656 input tokens; the ledger's five rows with input growing 764, 824, 1,068; model 97 to 98% of every turn, tools a few hundredths of a second; `search_policies` slower than the database tools |
| Part D | 4 calls and 5,033 input tokens in the saved thread, 9 calls and 10,029 in the ledger, one of them `summarization`; `copilot`, `rep-42`, `customer_lookup` and the thread id on every model call |
| Part E | the same cost by hand and by `call_cost`; the conversation at $0.000594 from the thread, $0.001482 from the ledger; the practice ledger 14,100 input and 600 output tokens, $0.002475 against $0.000369 for turn 10 alone; ticket 14 in 6 calls per run at $0.000955 to $0.001032, 23 to 29% less than without the cache |
| Part F | the short prompt (576 tokens) never cached; the long one (1,868) 1 of 5 without a key, 5 of 5 with one at 1,664 tokens a hit; a hit 42% cheaper |
| Part G | turns 1 to 3 with 3, 2 and 1 calls, then *Model call limits exceeded: thread limit (6/6)* twice |

Values come from a run on 12 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Seconds depend on your
network, region and load: compare the shapes (direct against tool, p50 against p95, model against tools) and the
counts, not our seconds. Token counts and the practice ledger repeat closely; cache hits vary by run.

## Before you start

- **Lab 00 first.** Its Part D starts the Ops API this lab uses, and its Part E proves your key works.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Prices:** `models.env` holds the chat model's four prices with their check date. Check them on OpenAI's pricing
  page before you teach, and change them there if you change the model.
- **Optional LangSmith:** Part D can send one run to LangSmith if you have `LANGSMITH_API_KEY` in `.env` or Colab
  Secrets and set `RUN_LANGSMITH = True`. Nothing else needs it.
- **Data:** `data/chinook.db` and the handbook index in `data/index/`, read in place. Part E files three refund
  requests (one per run) in the Ops API's temporary database.
- **Cost:** about 145 `gpt-4o-mini` calls and 145,000 input tokens in our run, about 3 US cents.

The notebook ends with a troubleshooting table: a timer that counts tool messages, `version="v2"` items against
tuples, the v3 warning, a cache that never reads, a missing price in an older `models.env`, a thread that undercounts,
a call limit that stays reached, and the Ops API.

## Resources

- [LangChain: streaming](https://docs.langchain.com/oss/python/langchain/streaming): stream modes, `version="v2"`, streaming tool calls and progress
- [LangChain: event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming): `stream_events(version="v3")` and its projections
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `SummarizationMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`
- [OpenAI: latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization): seven principles, streaming among them
- [OpenAI: prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): the 1,024-token minimum, `cached_tokens`, `prompt_cache_key`, differences by model
- [OpenAI: pricing](https://developers.openai.com/api/docs/pricing): the current price per model
- [LangSmith: observability](https://docs.langchain.com/oss/python/langchain/observability): tracing an agent with two environment variables

Next: [Lab 11, how to evaluate an agent's replies](../11_Evaluation_Set/README.md). Back to [the lab list](../README.md).
