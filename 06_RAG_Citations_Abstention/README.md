# Lab 06: How to answer from documents with citations

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/06_RAG_Citations_Abstention/06_rag_citations_abstention.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Follows: Day 1 D1-M08, steps 8.1 to 8.7 (D1-M08-01 to D1-M08-49, slides 251–296)**

## Goal

The copilot can search the support handbook, but search alone answers nothing: it returns the three nearest
passages, even for a question no policy covers. In this lab you connect the search to the chat model so that the
copilot answers from the passages, names the file each rule came from and says so when the handbook is silent, and
you check every answer in code. The moment that teaches it: asked whether Chinook matches a lower price, which no
policy covers, the copilot (`gpt-4o-mini`, in every one of our runs) invents *we do not match lower prices*, cites a
real file it retrieved, and passes the citation check. A citation shows where the model looked, not that the source says it; a quote for each claim,
checked in code, closes that gap.

## What you will learn

- How to answer from retrieved passages two ways: retrieve in your own code (two-step RAG) or give the model a
  retriever tool (agentic RAG), and what each costs in model calls.
- How to build a retriever tool that also returns its hits as data (`response_format="content_and_artifact"`), so
  your code knows exactly which files the model was given.
- How to check a cited answer in code: every cited file was retrieved, the reply abstains when no policy covers the
  question, and no phone number was made up.
- How to test abstention with a question no policy covers, and how to notice when the agent skipped its search.
- Why a real citation does not prove a claim, and how to make each claim carry a quote that your code can check.
- When sending the whole handbook beats retrieval, measured in tokens on the same questions.

## Coming from

[Lab 05](../05_FAISS_Index_Handbook/README.md) builds a FAISS index of the support handbook's 20 policies step by
step, and shows that the search returns three chunks even when none answers. This lab loads the same index prebuilt
in `data/index/` with the functions Lab 05 wrote, kept in `shared/copilot.py`, and its first section recalls in two
paragraphs what an embedding and a vector index are, so you can also start here. Lab 01's agent and Lab 03's `wrap_model_call` (used
in the Challenge) are the other pieces it reuses.

## What you will do

**Part A: Two-step RAG.** Load the index, retrieve the top 3 for the duplicate-charge question, send prompt v2, the
passages and the question in one call, and check that every cited file was retrieved.
**Part B: A retriever tool.** Write `search_policies`, build the agent with it, print the messages and
count the model calls. Then give the tool `response_format="content_and_artifact"` so it returns the files and scores
as data, and read them from the tool message.
**Part C: A question no policy covers.** Search the corpus for a price-matching rule, print the top 3 for a short
query and a longer one, then ask the agent three times and check each reply for abstention and citations.
**Part D: Ask for the manager's number.** Ask three times, check each reply, find the prompt example the agent copied, and
read a reference reply's cited sentences against their chunks.
**Part E: Check each claim against its chunk.** Mark three cited answers (and the bonus), see that a
file check passes all three, then ask for a `CitedAnswer` (`covered`, claims with quotes) and check every quote in
code.
**Part F: RAG or the whole handbook.** Send the whole handbook with each question, compare input tokens, cached
tokens and replies with two-step RAG, and choose a route for the copilot.
**Challenge.** Try a score threshold for abstention, make the agent search first with middleware, and add an
abstention example to the prompt.

## Checkpoints

| After | You should see |
|---|---|
| Part A | 20 chunks of 1,536 numbers; top 3 `policy_refunds.md` 0.4595, `policy_damaged_media.md` 0.4195, `policy_digital_downloads.md` 0.3855; the reply gives the duplicate-charge rule and cites `[policy_refunds.md]`; 734 input tokens; every cited file retrieved |
| Part B | one `search_policies` call with the model's own query (ours: *charged twice for the same album*, refunds third at 0.3227); the reply cites `[policy_refunds.md]`; 2 model calls (1,338 input tokens); the artifact lists three files with scores |
| Part C | the corpus has no price-matching rule; the short query: exchanges 0.3252, student discount 0.3118, payment 0.2955; the longer query: exchanges 0.3108, refunds 0.2976, student discount 0.2840; the correct reply abstains and cites nothing. Ours abstained in 0 of 3 runs (*we do not match lower prices*, citing `policy_exchanges.md` twice and `policy_payment.md` once), and the citation check passed all three |
| Part D | the correct reply refuses, cites `[policy_escalations.md]`, has no digits. Ours: no search in 3 of 3, one model call, the prompt's example copied, citation check `False`, two replies mention email with no citation; in the reference reply, *Support is by email* cites `policy_support_hours.md`, which never says email |
| Part E | the three answers: 1 supported, 2 and 3 unsupported; a file check passes all three; a made-up quote fails the quote check; the structured answer abstains on price matching (`covered: False`, no claims) and every quote is found for the other two questions |
| Part F | 1,185 words; whole handbook about 2,038 input tokens a question against 734; cached tokens in one of our six calls (1,792); both price-match replies cite `policy_refunds.md`, one abstains and one still tells the customer *we don't match lower prices* |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini`, `text-embedding-3-small`, Python 3.13.5, macOS, a fresh
`uv sync`). Search scores are stable to about four decimals; replies change from run to run, so check the files, the
order and the facts, not our wording. Each planned failure was run several times while building the lab; the
notebook gives the counts. A reference run with `gpt-6-luna` (5 Oct 2026) abstained on price matching and
searched before refusing the manager's number: compare with it if `models.env` names that model.

## Before you start

- **Lab 00 first.** Its Part E proves that your key reaches the chat model. Lab 01 explains the agent.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the index in `data/index/`, the policy and ticket files in `data/corpus/`, the handbook in
  `data/handbook/` and prompt v2 in `shared/prompts/copilot_system_v2.md`, all read in place.
- **Cost:** about 22 `gpt-4o-mini` calls and 12 embedding calls: well under one US cent.

The notebook ends with a troubleshooting table for the usual failures: a missing index file, a query embedded with a
different model, a tool that returns no artifact, an agent that does not search, a citation or abstention the
regular expressions miss, a missing key.

## Resources

- [LangChain: retrieval](https://docs.langchain.com/oss/python/langchain/retrieval): two-step, agentic and hybrid RAG compared
- [LangChain: messages](https://docs.langchain.com/oss/python/langchain/messages): the tool message and its `artifact`
- [LangChain reference: `BaseTool.response_format`](https://reference.langchain.com/python/langchain-core/tools/base/BaseTool/response_format): `"content"` or `"content_and_artifact"`
- [LangChain models: structured output](https://docs.langchain.com/oss/python/langchain/models#structured-output): `with_structured_output` with a Pydantic schema
- [Anthropic: reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations): allow "I don't know", ground answers in quotes, verify each claim with a quote
- [Anthropic: contextual retrieval](https://www.anthropic.com/news/contextual-retrieval): upgrades to retrieval (contextual embeddings, BM25, reranking), and when to send the whole knowledge base instead
- [OpenAI: prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): when a long, repeated prompt is cached

Next: [Lab 07: How to turn an API into tools an agent can call](../07_Tools_Over_The_Ops_API/README.md). Back to [the lab list](../README.md).
