# Lab 03: How to give an agent memory

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/03_Thread_Memory_Three_Settings/03_thread_memory_three_settings.ipynb)

**CPU | API key: `OPENAI_API_KEY` (most of Part A runs without one) | Follows: Day 1 D1-M05, steps 5.1 to 5.6 (D1-M05-01 to D1-M05-38, slides 145–180)**

## Goal

The agent from Lab 01 forgets everything between calls: ask it a follow-up and it has no idea who "she" is. In this
lab you give the copilot memory within a conversation and across a restart, then keep long conversations short
without losing the facts that matter. The moment that teaches it: on the same seven turns, the trimmed copilot answers
turn 7 politely and without an error, and it is wrong, because the invoice total and the rep from turn 2 are no longer
in what it is sent. Summarising kept the facts but used the most tokens; the fix that holds is to keep the case facts
in the agent's state, where no trim can reach them.

## What you will learn

- Why a chat model forgets between calls, and how a checkpointer and a `thread_id` give an agent memory within one
  conversation.
- How to keep a conversation across a restart with `SqliteSaver`.
- What full history, trimming and summarising cost per turn, and what each one can lose, measured on the same seven
  turns.
- The difference between trimming the saved thread and trimming only what the model is sent.
- How to keep facts that must never be lost in the agent's state instead of the message history.
- How to test any memory setting: ask late for a fact stated early.

## Coming from

Lab 01 built a tool-calling agent, and each call to it started from nothing. This lab gives it a thread, so it
remembers, and then deals with the cost: every turn sends the whole conversation again. It uses the prompt file
v1 from `shared/prompts/`, which [Lab 02](../02_Dialogue_Prompt_Versions/README.md) tested on fixed questions.

## What you will do

**Part A: What the model receives.** Ask the real model a follow-up that shares nothing with the first call and see
it forget, then resend the conversation by hand and see it remember. Then, with a scripted stand-in model (no API
call), send three turns on one thread and one on a new thread, and print what the model received each time. Trim an eight-message history with `trim_messages`
by message count and by a token budget, and see which message held the answer. Optionally, delete one exchange with
`RemoveMessage(id=...)`.
**Part B: A thread that survives a restart.** Save one turn with `SqliteSaver` in a temporary file, open a new
connection, ask "Which customer am I working on?", and list the checkpoints saved for the thread.
**Part C: Seven turns under four memory settings.** Run the same seven turns under full history, a `before_model` trim hook
(the saved thread shrinks), a `wrap_model_call` trim (only the request shrinks) and `SummarizationMiddleware`, each on
its own thread, and see where `ContextEditingMiddleware` fits when old tool results drive the growth. A callback
handler logs every model call; you chart the input tokens per turn and total the calls,
the summariser's and cached tokens included.
**Part D: Ask for an early fact at turn 7.** Check each setting's turn-7 reply for $49.62 and Steve Johnson, look at
what the trimmed threads still hold, and find the summary line that kept the facts. Then load the case facts from
`data/chinook.db` into the agent's state (`state_schema`, `@dynamic_prompt`) and run the seven turns again.
**Part E: Choose a strategy.** Choose a memory setting for three conversations, name what each could lose and the
question that would test it, then check your answers, including where to keep the invoice number in a long refund
dispute.
**Challenge.** Let the copilot save case facts itself with a tool that writes to its state, try a 30-message summary
trigger on a longer thread, and compare one all-day thread with a thread per customer.

## Checkpoints

| After | You should see |
|---|---|
| Part A | the follow-up with nothing shared does not know the customer, the list resent by hand does (ours: *Her name is Helena Holý.*); turns 1, 2 and 3 send 2, 4 and 6 messages; a new thread sends 2; the saved thread has 6 messages and no system prompt; `trim_messages(max_tokens=5, start_on="human", include_system=True)` keeps 4, and the dropped ones include *7 invoices, $49.62, rep Steve Johnson.*; by tokens the history is 86, a 60-token budget keeps 4 messages and 70 keeps 6, the total included; after deleting one exchange the next turn sends 6 |
| Part B | the second connection's reply names Puja Srivastava; 6 checkpoints for `case-puja-01`, three per turn |
| Part C | full history grows every turn (ours: 459 to 991 input tokens on the first call); trim and window stay in a band (459 to 684, 459 to 632), but trim saved 4 messages and window 20; summarise rises until the first summary at turn 4, then stays in a band (703 to 821). Over all calls summarise used the most input tokens (8,271, 3 summariser calls), then full (6,460), window (5,534) and trim (5,168); nothing cached |
| Part D | full and summarise have both facts at turn 7; trim and window have neither (*I'm unable to access customer-specific details ...*); turn 2 is gone from the trimmed thread; the summary's `SUMMARY` section opens with the facts; with the case facts in state, turn 7 has both facts for 4,664 input tokens, less than trim's 5,168 |
| Part E | 1 full history; 2 the invoice number kept where no setting can lose it (in the case state), tested with "Which invoice?" at turn 40; 3 a thread per customer, or trim |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). After its first three
calls, Part A uses a scripted model and an offline token estimate, so those values are exact. Replies and token counts in the first three calls and Parts B to D change from run
to run: check the shapes, the order and the two facts, not our numbers. A summarising run that loses a fact is a valid
finding; report it. A reference run with `gpt-6-luna` (5 Oct 2026) had turn-7 inputs of 1,672, 625 and 870 for
full, trim and summarise, with the same three results.

## Before you start

- **Lab 00 first.** Its Part E proves that your key reaches the chat model. Lab 01 explains the agent and the
  `get_policy` tool this lab reuses.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the policy files in `data/corpus/` and the prompt file `shared/prompts/copilot_system_v1.md`, read in
  place. The SQLite thread file goes in a temporary folder outside the repository.
- **Cost:** about 55 `gpt-4o-mini` calls (54 in our run) and 31,000 input tokens: well under one US cent.

The notebook ends with a troubleshooting table for the usual failures: a missing `thread_id`, a SQLite connection used
from another thread or after closing, a tool call left without its result, a summary that never appears, case facts
that do not reach the model, a missing key.

## Resources

- [LangChain: short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory): checkpointers, `thread_id`, trimming, deleting and summarising
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in) and [custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom): `SummarizationMiddleware`, `before_model`, `wrap_model_call` and `@dynamic_prompt`
- [LangChain: context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering): transient and persistent changes to what the model sees
- [OpenAI: prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): when input tokens are cached
- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence): threads, checkpoints and the checkpointer libraries
- [OpenAI: conversation state](https://developers.openai.com/api/docs/guides/conversation-state): why each request is stateless

Next: [Lab 04: How to remember a rep across conversations, and forget a customer](../04_Long_Term_Memory_And_Privacy/README.md). Back to [the lab list](../README.md).
