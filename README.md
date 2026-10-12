# Agentic AI: Conversational Agents: labs

Hands-on labs for developers who know Python and HTTP APIs and want to build a conversational agent that remembers,
answers from documents, acts through an API with a person's approval, and is measured, guarded and deployed. Every
lab works on the same case: a support copilot for the reps of Chinook, a fictional online music shop. The labs follow
the two-day course *Agentic AI: Conversational Agents*. The course slides teach every idea on their own, and each lab
gives you the practice and the measurements behind them.

The stack: LangChain 1.4 on LangGraph 1.2, an OpenAI chat model through the Responses API (set in `models.env`), `faiss-cpu` for vector search,
a small FastAPI service for the shop's operations, and Gradio for the chat page.

## The labs

The labs are being built in the order below. A lab without a link is not built yet.

| Lab | What you do | Runtime |
|---|---|---|
| [00 Environment check](00_Environment_Check/README.md) | Install, check the data hashes and row counts, start the Ops API, make one model call | CPU |
| [01 How to build a tool-calling agent](01_First_Chain_And_Tool/README.md) | A first call and its token usage, one tool, the tool call round trip by hand, then the same loop with `create_agent` | CPU |
| [02 How to write a dialogue prompt and test it](02_Dialogue_Prompt_Versions/README.md) | Keep prompts in versioned files, test a weak and a structured prompt on six fixed questions with checks in code over three runs, measure what examples cost, control length, get a typed intent label, and test ticket 16's planted line against a prompt rule | CPU |
| [03 Thread memory](03_Thread_Memory_Three_Settings/README.md) | Keep a conversation in a thread, restart it from disk, and compare full, trimmed and summarised history | CPU |
| [04 How to remember a rep across conversations, and forget a customer](04_Long_Term_Memory_And_Privacy/README.md) | Save a rep's preference in a store and use it in new threads, redact an email address and read what the thread really kept, watch a wrong memory come back in later conversations, and delete one customer's data | CPU |
| [05 How to search documents by meaning](05_FAISS_Index_Handbook/README.md) | Compute cosine similarity by hand, split the handbook two ways, build, save and search an exact FAISS index, predict the top file for rep questions, and test whether a search score can tell a covered question from an uncovered one | CPU |
| [06 RAG with citations and abstention](06_RAG_Citations_Abstention/README.md) | Answer from the handbook with citations, abstain when it has no answer, check each citation in code, and catch a citation that does not support the claim | CPU |
| [07 How to turn an API into tools an agent can call](07_Tools_Over_The_Ops_API/README.md) | Call the Ops API, write typed read tools and a lookup agent, keep the rep's identity in context, and test bad arguments, call limits and idempotency | CPU |
| [08 Approval before a write](08_Approval_Before_A_Write/README.md) | Pause before filing a refund request, approve, edit or reject it, and keep one request per refund | CPU |
| [09 Chain and router](09_Chain_And_Router/README.md) | Build a chain and an intent router in LangGraph, run the same requests through the router and the agent, and compare calls, tokens and outcomes | CPU |
| [10 How to measure an agent's latency and cost](10_Latency_Streaming_And_Cost/README.md) | Time a streamed reply to its first words, report p50 and p95 over ten runs, keep a ledger of every model call (the summariser's included), price a resolved case, and read when the prompt cache was used | CPU |
| [11 How to evaluate an agent's replies](11_Evaluation_Set/README.md) | Label five saved replies, score them with code checks, a reference check and a model judge, then run your own copilot on the same inputs and read each check's misses case by case | CPU |
| [12 How to guard an agent against misuse and failure](12_Guardrails_And_Injection_Test/README.md) | Run ticket 16 against the copilot with and without guards, and measure what each guard stops and what it breaks: a flag and a reply check in code, moderation, a search filtered by rep, retries and a fallback, and approval before the write | CPU |
| [13 How to put the copilot on a web page](13_Deploy_To_A_Space/README.md) | Serve the guarded copilot as a Gradio chat page with one thread per visitor, checked replies and approval in the chat, then assemble and check the folder a Hugging Face Space builds from | CPU |
| Capstone: Chinook copilot (optional) | Join the labs into one copilot, evaluate it and present it | CPU |

All labs run on a CPU. Every lab except Parts A to D of Lab 00 needs an OpenAI API key; the cost of a full lab
is a few US cents. Nothing needs a paid plan: Lab 13's push to a Hugging Face Space is optional, because creating a
Gradio Space needs a paid Hugging Face plan.

## Setup

**Colab.** Open a lab's README and use its *Open in Colab* badge. Add your OpenAI key under Secrets (the key icon
in the left bar) as `OPENAI_API_KEY` and allow the notebook to read it. The first cell copies this repository into
the Colab session and installs the packages.

**Local.** Install [uv](https://docs.astral.sh/uv/), then from the repository folder:

```bash
uv sync
cp .env.example .env
```

Fill in the keys you need in `.env`, open a notebook in JupyterLab or VS Code and pick the `.venv` kernel.

**Models.** Every lab reads its model names and prices from `models.env` in the repository root. The default chat
model is `gpt-4o-mini`. To switch every lab to another model, change that file once; to try one on your own machine
only, set the same variable in your `.env`.

## How to read a lab

Each lab is a guided notebook. Read the markdown even if you skip the code: it says what each step does, why, and
what the output means, and the saved outputs come from a real run. Each part ends with a checkpoint, and each lab
ends with a short challenge and a list of resources.

## Data

`data/` holds the shop's policies and tickets, the support handbook, the Chinook sample database (MIT licence,
Luis Rocha) and a prebuilt search index. `data/README.md` gives each file's source, licence and checksum.
