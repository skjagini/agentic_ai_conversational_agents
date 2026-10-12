# Lab 04: How to remember a rep across conversations, and forget a customer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/04_Long_Term_Memory_And_Privacy/04_long_term_memory_and_privacy.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Parts B, D and E and the end of Part C | Follows: Day 1 D1-M06, steps 6.1 to 6.4 (D1-M06-01 to D1-M06-35, slides 181–209)**

## Goal

You give the copilot a memory that outlives one conversation: a rep's preferences, saved by a tool in a store and
read into every new thread. Then you check what that memory really holds: what the model chose to save, what a
redacted message left in the saved thread, and what deleting one person's data removes. The moments that teach it:
a redacted email address is still in the thread's saved history; and a rep's mistaken remark, *refunds take 2 to 3
business days*, saved once, comes back in later conversations, where the copilot repeats it instead of opening the
refunds policy.

## What you will learn

- How to keep facts outside any thread in a store, under a namespace per rep, with `put`, `get`, `search` and
  `delete`, and why the rep's id comes from your code, never from the model.
- How to let the copilot save a preference with a tool that writes through `runtime.store`, read it into the prompt
  with `@dynamic_prompt`, and check over several runs that a new thread uses it.
- How to read back what the model saved, and make saving and using a preference reliable with fixed keys and a
  clear prompt section.
- How to redact an email address with `PIIMiddleware`, find where the raw address is still kept (the thread's
  checkpoint history), and keep it out with `durability="exit"`.
- How a wrong memory returns in every later conversation, and what limits it: saved preferences that may change how
  a reply looks, never what it says.
- How to delete one rep's memory and one customer's data, prove both are gone, and say what deletion in your code
  does not reach.

## Coming from

Lab 03 kept a conversation in a thread, across restarts; a new thread starts empty. This lab adds long-term memory:
a store of a few facts per rep, written by a tool and read into every thread, with the `v1` prompt from Lab 02 and
`get_policy` from Lab 01. Lab 07 later passes the rep's identity to tools the same way, through the context, and
Lab 12 returns to redaction and permissions as guards.

## What you will do

**Part A: Keep facts in a store, filed by rep.** Put, get, search, replace and delete memories for two reps in an
`InMemoryStore`, and see that a short namespace prefix reaches every rep. No key needed.
**Part B: Save a preference in one thread and use it in another.** Write a `save_preference` tool that writes through
`runtime.store` and a dynamic prompt that reads the rep's memories; rep 42 states a preference in thread A, asks in
thread B, rep 77 asks in thread C. Read the store, run three times with checks in code, then fix the keys (an enum)
and the prompt section (an instruction), three runs each.
**Part C: Redact an email address, then read what the thread saved.** With a scripted model and `PIIMiddleware`,
compare what the model received, the thread's state, its checkpoint history and the rows of a SQLite file; save with
`durability="exit"` and count again. Then run the real copilot on a customer message with an address and a wish.
**Part D: See a wrong memory come back in later threads.** Save a rep's mistaken remark, ask in five new threads and
in five with an empty store; see a customer's language reach the next customer; then limit what a memory can do
with the tool's description and the prompt, and count again.
**Part E: Delete a rep's memory and a customer's data.** Delete the wrong memory and ask again; record each memory's
source thread, run one rep's day, delete one customer's threads and memories, and read back what is left; list what
deleting in your code does not reach.
**Challenge.** Decide what to keep, redact or never store, with a card mask; a customer namespace for customer
wishes; count what memory adds to every call.

## Checkpoints

| After | You should see |
|---|---|
| Part A | `{'value': 'three bullet points'}` for rep 42; rep 77 sees only its own memory; `search(("rep",))` returns all three; after a second `put` and a delete, `two bullet points` and `['reply_format']` |
| Part B | the model sees `['key', 'value']` only; rep 77's thread never gets the preference; the free-key tool: key names vary and the sign-off is often lost (ours: 1 of 3); fixed keys: both saved 3 of 3 but rarely used (ours: signed 0 of 3); with the section as an instruction: 3 of 3 |
| Part C | the model and the state get `[REDACTED_EMAIL]`; 5 checkpoints, step 0 with the raw address; SQLite: 2 of 5 checkpoint rows and 1 of 7 write rows hold it; with `durability="exit"`: 0, one checkpoint; the real copilot saves the customer's *Czech* as rep 42's `language` (ours: 3 of 3) |
| Part D | the mistaken remark saved under `reply_format` (ours: 3 of 3); new threads say 2 to 3 days (ours: 4 of 5, `get_policy` 1 of 5) against 0 of 5 with an empty store; the next customer answered in Czech (3 of 3); with the guarded tool and prompt the remark is still saved (3 of 3), the wrong time gone (0 of 5), Czech still used (3 of 3) |
| Part E | after the delete, 5 to 10 days (3 of 3); Helena's thread and her memory deleted, Puja's thread and the sign-off left, Helena's state `{}`; the client's `store` setting `None` by default, `False` when set |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Model replies change
from run to run, and from model to model if `models.env` names another one: compare the pattern (what was saved,
which threads repeated it), not the exact counts. Parts A and C up to the real copilot have no model in them and give
the same values every time.

## Before you start

- **Labs 00 to 03 first.** Lab 01 writes `get_policy`, Lab 02 the `v1` prompt in `shared/prompts/`, Lab 03 threads,
  checkpointers and `@dynamic_prompt`.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the policy files in `data/corpus/` (course-authored). The customer's address is
  `helena.h@example.com`, an `example.com` address reserved for examples. Part C writes two small SQLite files to
  the system temp folder. Nothing is downloaded.
- **Cost:** about 130 `gpt-4o-mini` calls, under two US cents.

The notebook ends with a troubleshooting table for the usual failures: no store or no context passed, a preference
not used in a new thread, an address still found after redaction, a name not redacted, a deleted thread whose
customer is still remembered.

## Resources

- [LangChain: long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory): a store passed to `create_agent`, tools that read and write through `runtime.store`
- [LangGraph: stores](https://docs.langchain.com/oss/python/langgraph/stores): namespaces, keys, `put`, `get`, `search`, `delete`, and database-backed stores
- [LangChain: memory concepts](https://docs.langchain.com/oss/python/concepts/memory): short-term and long-term memory, and the kinds of things worth remembering
- [LangChain: guardrails](https://docs.langchain.com/oss/python/langchain/guardrails): `PIIMiddleware`, its built-in types and strategies
- [LangGraph: checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers): checkpoints per step, `get_state_history`, `delete_thread`, and the durability modes
- [OWASP: Top 10 for Agentic Applications](https://genai.owasp.org/): ASI06, memory and context poisoning
- [OpenAI: data controls in the API](https://developers.openai.com/api/docs/guides/your-data): what OpenAI keeps, for how long, and `store=False`

Next: [Lab 05: How to search documents by meaning](../05_FAISS_Index_Handbook/README.md). Back to [the lab list](../README.md).
