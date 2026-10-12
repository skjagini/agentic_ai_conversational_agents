# Lab 05: How to search documents by meaning

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/05_FAISS_Index_Handbook/05_faiss_index_handbook.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Parts A, D, E, F and G (Parts B and C run without one) | Follows: Day 1 D1-M07, steps 7.1 to 7.6 (D1-M07-01 to D1-M07-45, slides 210–250)**

## Goal

A rep who asks *when does the link stop working?* has no policy file name to give, so the copilot needs to find a
policy by what the question means. In this lab you build that search yourself: you compute cosine similarity by hand,
build an exact FAISS index of the support handbook, choose how to split the handbook, and test the search on
questions whose answer you know. The moment that teaches it: the search always returns three chunks with scores, and
the scores do not tell you whether any of them answers. *Do we take Bitcoin?*, which the payment policy answers,
scores about the same as *Do we match a lower price from another store?*, which no policy covers, and *Can a customer
pay in monthly instalments?*, which no policy covers either, scores higher than five of the twelve covered questions.
Nearest is not the same as relevant, and Lab 06 builds on that.

## What you will learn

- How to compute cosine similarity by hand, and why it is a plain dot product for OpenAI's embeddings.
- How to build, save and load an exact FAISS index (`IndexFlatIP`) and search it for the nearest chunks.
- How to choose a split for a handbook by checking where one rule lands and whether its chunk still names its file.
- How to predict the top file for a question, check the prediction, and explain a miss from what each chunk holds.
- Why a search score is not a probability, measured on questions the handbook covers and questions it does not.
- Optional: how keyword search (BM25) and reciprocal rank fusion work, and what hybrid search gains and loses, one
  question at a time.

## Coming from

[Lab 04](../04_Long_Term_Memory_And_Privacy/README.md) and the labs before it gave the copilot a policy only when it
could name the file (`get_policy("refunds")`). This lab builds the search that finds a policy from the rep's own words.
It uses no chat model, only `EMBED_MODEL` from `models.env`.

## What you will do

**Part A: Measure closeness with cosine similarity.** Dot product, lengths and cosine on two-number vectors, then on
three embedded rep questions; check that OpenAI's vectors have length 1.
**Part B: Build an exact index with FAISS.** Toy vectors in `IndexFlatIP`, raw and after `normalize_L2`; what
normalising does to real OpenAI vectors; save and load; exact against approximate indexes, and what production uses.
**Part C: Split the handbook two ways.** By size (`RecursiveCharacterTextSplitter`, 1,000 characters, 200 overlap)
and by heading (`MarkdownHeaderTextSplitter`); find the duplicate-charge rule in each; write the heading split as a
function and compare it with `shared/copilot.py`.
**Part D: Build, save and search the handbook index.** Count and price the tokens, embed the 20 chunks, build, save
and load the index, write `search`, check each piece against `shared/copilot.py`, measure split A's citation problem,
and run the same search through LangChain's `InMemoryVectorStore`.
**Part E: Predict the top file, then search.** Four rep questions: predict, search, and explain question 4's miss.
**Part F: Ask a question no policy covers.** The three chunks it still returns, then 18 labelled questions and four
score thresholds.
**Part G (optional): Add keyword search and fuse the rankings.** BM25 and reciprocal rank fusion by hand, compared
with vector search on 12 questions.
**Challenge.** Reword question 4; split by heading, then by size; test a threshold on new questions.

## Checkpoints

| After | You should see |
|---|---|
| Part A | toy cosines A 1.0, B 0.7071; `(3, 1536)`; lengths 1.0; cosines 1–2 0.7059, 2–3 0.2407, 1–3 0.1140 |
| Part B | raw inner product ranks B (5.0) above A (2.0); after `normalize_L2` A 1.0, B 0.7071, as numpy's cosine; normalising real OpenAI vectors changes no number by more than 0.000015; after reload `ntotal 2 d 2`, same results |
| Part C | split A: 10 chunks (289, 945.5, 991 characters), 1,443 repeated, the rule whole in chunk 6 with `policy_returns.md` and `policy_shipping.md`; split B: 20 chunks (277, 345, 493), the rule in chunk 13 with `policy_refunds.md`; your function matches `shared/copilot.py` |
| Part D | 1,605 tokens ($0.000032); `ntotal 20 d 1536`; `handbook.faiss` 122,925 bytes; the bought-twice question: `policy_refunds.md` 0.4423, `policy_damaged_media.md` 0.3791, `policy_digital_downloads.md` 0.3496, the same as `search`; under split A the rule's chunk comes first (0.4034) and its first `Source:` line is `policy_returns.md` |
| Part E | questions 1–3 rank the answering file first; question 4 ranks `policy_shipping.md` (0.3875) above `policy_international.md` (0.3680) |
| Part F | the price-match question returns `policy_exchanges.md` 0.3252, `policy_student_discount.md` 0.3118, `policy_payment.md` 0.2955; lowest covered score 0.3248 (Bitcoin), highest uncovered 0.4915 (instalments); no threshold separates them |
| Part G | answering file first: vector 11, BM25 10, hybrid 11 of 12; hybrid gains question 4 and loses *Is support open on Saturday?* (rank 3) |

Values come from a run on 11 Oct 2026 (`text-embedding-3-small`, faiss-cpu 1.15.1, Python 3.13.5, macOS, a fresh
`uv sync`). Parts B and C call no model, so their values are exact. Embedding scores repeated to four decimals in
three exploration runs the same day, but the API does not return exactly the same numbers on every call: expect the
fourth decimal to move and check the order of the files.

## Before you start

- **Lab 00 first.** Its Part E proves that your key reaches OpenAI.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the handbook in `data/handbook/support_handbook.md`, read in place. The prebuilt index in `data/index/`
  is used only for a comparison in Part D. Your own index is saved in `05_FAISS_Index_Handbook/my_index/`, which git
  ignores.
- **Cost:** about 45 embedding calls, under 10,000 tokens: about $0.0002. No chat model.

The notebook ends with a troubleshooting table: a missing index file, a query embedded with another model, an array
that is not `float32`, a missing key.

## Resources

- [OpenAI: embeddings guide](https://developers.openai.com/api/docs/guides/embeddings): models, vector length, and why cosine and dot product agree for OpenAI vectors
- [OpenAI: retrieval guide](https://developers.openai.com/api/docs/guides/retrieval): hosted vector stores, default chunking, `score_threshold` and hybrid ranking
- [LangChain: text splitters](https://docs.langchain.com/oss/python/integrations/splitters) and [split markdown by headers](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
- [LangChain: vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores): the common interface, `InMemoryVectorStore`, Chroma, Qdrant
- [FAISS wiki: guidelines to choose an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [Anthropic: contextual retrieval](https://www.anthropic.com/news/contextual-retrieval): BM25 with embeddings and reranking

Next: [Lab 06: How to answer from documents with citations](../06_RAG_Citations_Abstention/README.md). Back to [the lab list](../README.md).
