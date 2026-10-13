# Agentic AI: Conversational Agents: labs

Hands-on labs for developers who know Python and HTTP APIs and want to build a conversational agent that remembers,
answers from documents, acts through an API with a person's approval, and is measured, guarded and deployed. Every
lab works on the same case: a support copilot for the reps of Chinook, a fictional online music shop. The labs follow
the two-day course *Agentic AI: Conversational Agents*. The course slides teach every idea on their own, and each lab
gives you the practice and the measurements behind them.

The stack: LangChain 1.4 on LangGraph 1.2, an OpenAI chat model through the Responses API (set in `models.env`),
LangChain's in-memory vector store for search (FAISS in Lab 07), a small FastAPI service for the shop's operations,
and Gradio for the chat page.

## The labs

The labs follow the course: Labs 00 to 06 on Day 1, Labs 07 to 13 on Day 2. [OUTLINE.md](OUTLINE.md) gives each
day's goal and its labs. Labs marked *self-study* are complete on their own; the in-class labs never depend on them.

| Day | Lab | What you do |
|---|---|---|
| 1 | [00 How to set up the lab environment](00_Environment_Check/README.md) | Set up on Colab or locally (with `uv` or `pip`), then check the packages, the data files, the Ops API and your key in one run |
| 1 | [01 How to build a tool-calling agent](01_First_Chain_And_Tool/README.md) | Run the tool-calling loop by hand on the Responses API, then the same loop with `@tool` and `create_agent` |
| 1 | [02 How to write a dialogue prompt and test it](02_Dialogue_Prompt_Versions/README.md) | Grow a plain-string prompt into sections kept in files, test it on fixed questions with checks in code, and fix a failing case with one example |
| 1 | [03 How to give an agent memory](03_Thread_Memory_Three_Settings/README.md) | Keep a conversation in a thread, read it back from a SQLite file after a restart, keep a long thread short, and keep an email address out of what the thread stores |
| 1 | [04 How to remember a rep across conversations, and forget a customer](04_Long_Term_Memory_And_Privacy/README.md) (self-study) | Save a rep's preference in a store and read it in new threads, watch a wrong memory come back, and delete one customer's data |
| 1 | [05 How to turn an API into tools an agent can call](05_Tools_Over_The_Ops_API/README.md) | Call the Ops API by hand, write typed tools and a lookup agent, keep the rep's identity in context, return errors the model can recover from, retry a failing call and cap the calls |
| 1 | [06 How to choose between a workflow and an agent](06_Chain_And_Router/README.md) | Write a workflow as plain `if`/`else` on a typed label, run the same requests through it and the lookup agent, and compare calls, tokens and outcomes |
| 2 | [07 How to search documents by meaning](07_FAISS_Index_Handbook/README.md) (self-study) | Compute cosine similarity by hand, split the handbook two ways, build and search a FAISS index, and test whether a score can tell a covered question from an uncovered one |
| 2 | [08 How to give an agent a document search tool](08_RAG_Citations_Abstention/README.md) | Put the handbook in a vector store, give the agent search as a tool, cite each rule's file, say when the handbook has no answer, and check citations in code |
| 2 | [09 How to ask a person before an agent acts](09_Approval_Before_A_Write/README.md) | File a refund by hand, stop a hand-written loop before the write, then approve, edit or reject the call with `HumanInTheLoopMiddleware`, and make a retried request file one refund |
| 2 | [10 How to evaluate an agent](10_Evaluation_Set/README.md) | Write test cases as dicts, check the tools and arguments from the agent's messages, cover seven kinds of case, label each run, and ask a judge whether replies are grounded |
| 2 | [11 How to measure an agent's latency and cost](11_Latency_Streaming_And_Cost/README.md) (self-study) | Time a streamed reply to its first words, time the evaluation cases with each check beside its seconds, keep a ledger of every model call, price each case, and read the prompt cache |
| 2 | [12 How to guard an agent against misuse and failure](12_Guardrails_And_Injection_Test/README.md) | Run ticket 16 against the copilot with and without guards, and measure what each guard stops and what it breaks |
| 2 | [13 How to put the agent on a web page](13_Deploy_To_A_Space/README.md) | Serve the guarded copilot as a Gradio chat page with one thread per visitor and approval in the chat, then assemble the folder a Hugging Face Space builds from |

All labs run on a CPU. Every lab except Parts A to C of Lab 00 needs an OpenAI API key; the cost of a full lab
is a few US cents. Nothing needs a paid plan: Lab 13's push to a Hugging Face Space is optional, because creating a
Gradio Space needs a paid Hugging Face plan.

## Setup

Follow [Lab 00](00_Environment_Check/README.md) before the first class. Its README walks through three routes, step by
step, and its notebook checks the result in one run:

- **Colab:** the *Open in Colab* badge in each lab's README, and your OpenAI key under Secrets. Nothing to install.
- **Local with `uv`:** `git clone` (or the ZIP), `uv sync`, copy `.env.example` to `.env` with your key, then
  `uv run jupyter lab`.
- **Local with `pip`:** Python 3.13, a virtual environment, `pip install -r requirements.txt jupyterlab==4.6.4
  ipykernel==7.4.0`, the same `.env`, then `jupyter lab`.

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

## Colab setup

Use it with Github Colab spaces,  
- install python and Jupyter extensions 
- create a copy of .env file and add open ai token value
- run the command from colab terminal curl -LsSf https://astral.sh/uv/install.sh | sh
