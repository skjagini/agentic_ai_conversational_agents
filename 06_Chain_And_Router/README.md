# Lab 06: How to choose between a workflow and an agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/06_Chain_And_Router/06_chain_and_router.ipynb)

**CPU | API key: `OPENAI_API_KEY`**

## Goal

Choose between a workflow and an agent from measurements: build the same support flow both ways, run the same four
requests through both, and compare model calls, tokens and outcomes. The moment that teaches it: on the three requests
it was written for, the workflow makes the same number of model calls in every run (two at most) and uses about half
the agent's tokens or less. Then a rep asks which albums were on Helena's first invoice. No step of the workflow reads
an invoice's albums, so it answers without them (0 of 5 runs pass), where the agent looks the invoice up and names
them (5 of 5 on `gpt-4o-mini`).

## What you will learn

- How to get a label and the arguments a step needs from one structured-output call, and why a valid label can still be wrong.
- How to write a workflow as plain `if`/`else`: fixed Ops API calls per branch and one call to write the reply.
- How to count a run's model calls and tokens with a callback, for a workflow and an agent alike.
- How to run the same requests through both shapes, check every reply in code, and read the table of runs.
- How to decide between a workflow and an agent by asking whether you can list the steps before the request arrives.

## Coming from

Lab 01 described a tool as a JSON schema, and Lab 05 built the lookup agent over the Ops API. This lab uses both: a
schema makes the model return a label that picks a workflow's branch, and the agent, with the same three read tools,
answers the same requests. The tools are imported from `shared/ops_tools.py`, so you can start here.

## What you will do

**Part A: Label a request and pull out its arguments.** Get a typed `Request` (a label from a fixed list, the
customer's name and the invoice numbers) from one `with_structured_output` call, and label the four requests three
times each.
**Part B: Write the workflow as plain Python.** Read `_get`, the function behind the shared tools, call the tools from your own code, write the account and refund steps,
write the reply from the fetched facts, and join the branches with `if` and `else`: a **router** whose paths are
short **prompt chains**.
**Part C: Rebuild the Lab 05 agent.** The same three tools and Lab 05's prompt; follow Puja's question through its
messages.
**Part D: Run the same requests through both.** Count calls and tokens with a callback, write a check for each request
(the answer key) and try it on one reply, run every request five times through each shape, and read the failures.
**Part E: Choose a workflow or an agent.** Read the runs, tell a misroute from a request no route covers, decide the
shape for four support jobs, and decide the copilot's.
**Going further.** The same workflow as a LangGraph `StateGraph`.
**Challenge.** A step for the albums, and a label in front of the agent.

## Checkpoints

| After | You should see |
|---|---|
| Part A | `label='account_lookup' customer_name='Puja Srivastava' invoice_ids=[]`; the same label and arguments for all four requests in 3 of 3 runs (an earlier run labelled the poem `policy_question` once) |
| Part B | Puja: customer 59, 6 invoices, 36.64; ticket 14: a note on two 9.99 charges for the same album on the same date, 2 calls; the poem: the fixed reply, 1 call |
| Part C | `find_customer`, then `get_customer_invoices` with `customer_id` 59; 6 invoices, 36.64; 3 model calls |
| Part D, one reply | check 1 `True` on the workflow's reply to request 1; `False` on a reply without the total |
| Part D | requests 1 and 2: 5 of 5 in both shapes, the workflow at 2 calls and about half the agent's tokens; the poem: workflow 5 of 5, agent 0 of 5; request 4: workflow 0 of 5, agent 5 of 5 at 4 calls and about 2,020 tokens |
| Part E | the four jobs: workflow, workflow, agent, agent, each with its deciding fact |
| Going further | `classify`, `account_lookup`, `draft`, each adding its own key, 2 calls |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Model runs vary,
and differ again if `models.env` names another model: compare the counts and the kinds of failure, not our wording.

## Before you start

- **Lab 00 first.** It starts the Ops API this lab uses and checks your key.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db`, read in place by the Ops API (`shared/ops_api.py`), opened read-only. Invoices 9001 and
  9002 are a course fixture inside the API (ticket 14's two charges). Nothing is written and nothing is downloaded.
- **Cost:** about 110 calls to the chat model, a few US cents with `gpt-4o-mini`.

The notebook ends with a troubleshooting table: a message with no customer name, the API not answering, a meter that
counts nothing, and two graph wiring errors.

## Resources

- [LangGraph: workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents): prompt chaining and routing as workflows, beside agents, each built as a graph
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): workflows (chaining, routing) beside agents, and when the extra freedom pays for itself
- [LangChain: structured output](https://docs.langchain.com/oss/python/langchain/structured-output): schemas with Pydantic and `Literal`
- [LangChain: models, token usage](https://docs.langchain.com/oss/python/langchain/models): `UsageMetadataCallbackHandler` and `get_usage_metadata_callback`
- [LangGraph: graph API](https://docs.langchain.com/oss/python/langgraph/graph-api): state, nodes, edges and conditional edges
- [LangChain: multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent): when one agent is enough, and the patterns for when it is not

Next: [Lab 07: How to search documents by meaning](../07_FAISS_Index_Handbook/README.md) (self-study), then
[Lab 08: How to give an agent a document search tool](../08_RAG_Citations_Abstention/README.md). Back to [the lab
list](../README.md).
