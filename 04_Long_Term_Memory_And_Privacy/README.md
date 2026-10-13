# Lab 04: How to remember a rep across conversations, and forget a customer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/04_Long_Term_Memory_And_Privacy/04_long_term_memory_and_privacy.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Self-study**

## Goal

A thread keeps one conversation, so in a new one the copilot has forgotten how the rep likes replies written. In this
lab you give the copilot a long-term memory: a store of a few facts per rep, written and read by tools, in every
thread. Then you meet its risk and its duty. The moment that teaches it: a customer's wish, *reply to her in Czech*,
saved once as the rep's own preference, comes back in every later conversation of that rep, and their replies to other
customers come out in Czech until someone deletes it.

## What you will learn

- How a store keeps memories under a namespace and a key, by building one from a dictionary, then using LangGraph's
  `InMemoryStore`.
- How to give the copilot a tool that saves a preference and a tool that reads it, both through `runtime.store`,
  with the rep's id taken from the context, never from the model.
- How to check that a preference saved in one thread is used in a new thread, and never in another rep's.
- How a wrong memory comes back in every new conversation, and how to find it by reading the store.
- How to delete one memory with `store.delete()`, and everything about one customer with
  `checkpointer.delete_thread()` and the memories saved from her threads.

## Coming from

Lab 03 kept a conversation in a thread with a checkpointer; a new thread starts empty. This lab is self-study and
stands on its own: it opens with a short recap of threads and checkpointers, explains the context before using it,
and brings in the copilot's prompt file (`shared/prompts/copilot_system_v1.md`) and `get_policy`. No later lab depends
on it.

## What you will do

**Recap.** Ask an agent with a checkpointer the same question on its thread and on a new one.
**Part A: Build a store from a dictionary.** Write `put`, `get`, `search` (by namespace prefix) and `delete` by hand,
for two reps.
**Part B: Use LangGraph's `InMemoryStore`.** The same four calls on the store LangChain agents use.
**Part C: Give the copilot tools that save and read preferences.** A `save_preference` tool with fixed keys and a
`get_preferences` tool, both through `runtime.store`, the rep's id from the context, and a prompt section that says
when to use them. Rep 42 states two preferences in thread A; rep 42 asks in thread B, rep 77 in thread C.
**Part D: See a wrong memory come back in new conversations.** Helena's wish for Czech is saved as rep 42's
own preference; count the Czech replies to rep 42's next five customers, and to rep 77's.
**Part E: Delete a wrong memory and a customer's data.** Delete the memory and ask again; record each memory's source
thread, run one rep's day, then delete one customer's threads and the memories saved from them.
**Going further.** Free key names; memories read in the prompt with `@dynamic_prompt`, as a plain list and as an
instruction; a save tool told what not to save; what deleting in your code does not reach (`store=False`).
**Challenge.** A namespace per customer for customer wishes, in three steps with starter cells; a tool that lets the
rep forget a preference, from a store that holds only the old mistake.

## Checkpoints

| After | You should see |
|---|---|
| Recap | thread 1 recalls the sign-off; thread 2 asks the rep to say it again |
| Part A | `{'value': 'three bullet points'}`, then `None`; 3 memories under `('rep',)`; after the second `put` and the delete, only `two bullet points` |
| Part B | the same, with `Item` objects that carry a creation time; rep 42 keeps `['reply_format']` |
| Part C | the model sees `['key', 'value']` only; thread A saves `reply_format` and `sign_off`; thread B uses both, thread C neither (ours: 5 of 5 more runs) |
| Part D | *Czech* saved as rep 42's `language`; most of rep 42's next replies in Czech (ours: 4 of 5; 39 of 40 in eight more runs), none of rep 77's |
| Part E | after the delete, no Czech (0 of 3); Helena's thread and her memory deleted, Puja's thread and the sign-off left, Helena's thread `{}` |

The saved outputs come from `gpt-4o-mini` on 12 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Replies change
from run to run, and from model to model if `models.env` names another one: compare the pattern (what was saved,
which threads used it), not the exact counts. Parts A and B have no model in them and give the same values every time.

## Before you start

- **Lab 00 first** (it checks your key and the packages). Labs 01 to 03 help but are not required.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the policy files in `data/corpus/` and the prompt file `shared/prompts/copilot_system_v1.md`, read in
  place. Nothing is downloaded or written to disk.
- **Cost:** about 100 calls to the chat model, about two US cents with `gpt-4o-mini`.

The notebook ends with a troubleshooting table for the usual failures: no store or no context passed, a copilot that
never reads its memories, a preference not used in a new thread, a deleted thread whose customer is still remembered.

## Resources

- [LangChain: long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory): a store passed to `create_agent`, tools that read and write through `runtime.store`
- [LangGraph: stores](https://docs.langchain.com/oss/python/langgraph/stores): namespaces, keys, `put`, `get`, `search`, `delete`, and database-backed stores
- [LangChain: memory concepts](https://docs.langchain.com/oss/python/concepts/memory): short-term and long-term memory, and what is worth remembering
- [LangGraph: checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers): threads, checkpoints and `delete_thread`
- [OWASP: Top 10 for Agentic Applications](https://genai.owasp.org/): ASI06, memory and context poisoning
- [OpenAI: data controls in the API](https://developers.openai.com/api/docs/guides/your-data): what OpenAI keeps, for how long, and `store=False`

Next: [Lab 05: How to turn an API into tools an agent can call](../05_Tools_Over_The_Ops_API/README.md). Back to [the lab list](../README.md).
