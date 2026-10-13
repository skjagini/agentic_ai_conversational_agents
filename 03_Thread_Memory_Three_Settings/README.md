# Lab 03: How to give an agent memory

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/03_Thread_Memory_Three_Settings/03_thread_memory_three_settings.ipynb)

**CPU | API key: `OPENAI_API_KEY`**

## Goal

A chat model keeps nothing between calls, so the copilot forgets the customer as soon as the rep asks a follow-up.
In this lab you give it a thread that a checkpointer saves to a file, keep a long thread short, and keep a customer's
email address out of what the thread stores. The moment that teaches it: you restart the kernel, Python has forgotten
every variable, and the conversation is still there, read back from a SQLite file. Then you read what that file
actually holds, and find the address the rep pasted, in plain text.

## What you will learn

- Why a chat model forgets between calls, and how sending the conversation again as a list gives it memory.
- How a checkpointer and a `thread_id` keep each conversation for you.
- How to keep a thread across a kernel restart with `SqliteSaver`, and read what the file holds.
- How to keep a long thread short by trimming or summarising with middleware, and how to test both with a late
  question about an early fact.
- How to keep an email address out of the saved thread with `PIIMiddleware`, and check the file, not the reply.

## Coming from

Lab 01 built a tool-calling agent and sent the conversation history by hand. This lab lets a checkpointer keep that
history, in memory and then in a file. From Part D it uses the copilot's prompt file,
`shared/prompts/copilot_system_v1.md`, and `get_policy` from Lab 01.

## What you will do

**Part A: Send the conversation again yourself.** Ask a follow-up that shares nothing with the first call, then send
the conversation again as a list.
**Part B: Let a checkpointer keep the thread.** Give an agent an `InMemorySaver` and a `thread_id`; ask the follow-up
on the same thread and on a new one; read the saved thread with `get_state`.
**Part C: Keep the thread across a restart.** Save a turn that holds the customer's email address with `SqliteSaver`
in `threads.sqlite`, restart the kernel, read the thread back and ask a follow-up; then count the rows of the file
that hold the address.
**Part D: Keep a long thread short.** Run seven turns of one case under full history, a `before_model` trim and
`SummarizationMiddleware`, and ask at turn 7 for two facts from turn 2; run the trim and the summary three times each,
read what the trim left in the file, and read the summary.
**Part E: Keep an email address out of the saved thread.** Redact the address with `PIIMiddleware`, read the file
again, then save with `durability="exit"`.
**Going further.** Trim by tokens; delete one message with `RemoveMessage`; read the checkpoint history; clear old
tool results with `ContextEditingMiddleware`.
**Challenge.** From a starter cell with two named agents: mask a card number and count the rows that hold it;
compare one all-day thread with a thread per customer by what each thread saved.

## Checkpoints

| After | You should see |
|---|---|
| Part A | the follow-up with nothing shared does not know who "her" is; the list of 4 messages does |
| Part B | the follow-up on the same thread names Helena Holý, a new thread does not; 4 messages saved, no system prompt |
| Part C | after the restart, `False` for the agent and Part A's list (a ⚠️ line if you did not restart), and the 2 saved messages read back; the follow-up names Helena Holý and her address; every checkpoint row holds the address (ours: 6 of 6, writes 2 of 6) |
| Part D | full history grows every turn (ours: 18 messages, 459 to 977 input tokens in the last call) and keeps both facts; the trim keeps at most 6 messages and loses both facts (3 of 3 runs); the trimmed thread's newest state lacks the total while older checkpoint rows in the file still hold it (ours: 13 of 34); the summary keeps both (3 of 3), on a line of the summary |
| Part E | the saved message holds `[REDACTED_EMAIL]`; the file still holds the address in the first snapshot (ours: 2 of 10 checkpoint rows, 1 of 13 write rows); with `durability="exit"` no row holds it |

The saved outputs come from `gpt-4o-mini` on 12 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Replies change
from run to run, and from model to model if `models.env` names another one: check whether the facts and the address
are there, not the wording or the exact counts.

## Before you start

- **Labs 00 and 01 first.** Lab 00 proves your key reaches the chat model; Lab 01 writes `get_policy`.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session. A restart
  (**Runtime → Restart session**) keeps the files, so `threads.sqlite` survives it.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the policy files in `data/corpus/` and the prompt file `shared/prompts/copilot_system_v1.md`, read in
  place. The notebook writes `threads.sqlite` in this folder (gitignored). The customer's address,
  `helena.h@example.com`, uses `example.com`, a domain reserved for examples.
- **Cost:** about 85 calls to the chat model, under one US cent with `gpt-4o-mini`.

The notebook ends with a troubleshooting table for the usual failures: a missing `thread_id`, the restart cells run
in the wrong order, a SQLite connection used from another thread, a summary that never appears, an address still
found after redaction.

## Resources

- [LangChain: short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory): checkpointers, trimming, deleting and summarising
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `SummarizationMiddleware`, `PIIMiddleware`, `ContextEditingMiddleware`
- [LangChain: guardrails](https://docs.langchain.com/oss/python/langchain/guardrails): PII detection and its strategies
- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence): threads, checkpoints, durability modes
- [OpenAI: conversation state](https://developers.openai.com/api/docs/guides/conversation-state): why each request is stateless

Next: [Lab 04: How to remember a rep across conversations, and forget a customer](../04_Long_Term_Memory_And_Privacy/README.md). Back to [the lab list](../README.md).
