# Lab 12: How to guard an agent against misuse and failure

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/12_Guardrails_And_Injection_Test/12_guardrails_and_injection_test.ipynb)

**CPU | API key: `OPENAI_API_KEY` (the toy search in Part D and the flag in Part B run without one) | Follows: Day 2 D2-M07, steps 7.1 to 7.6 (D2-M07-01 to D2-M07-40, slides 185–221)**

## Goal

Choose an agent's guards by what each one measurably stops and what it breaks. When we ran it (`gpt-4o-mini`, 11 Oct
2026), the copilot with the write tool and no guards filed 4 refund requests nobody saw in 7 runs of ticket 16, tags,
the prompt's rule and moderation all let the planted line through, and only plain code and a person stopped the harm:
a check on the reply caught every obeyed reply, and approval held every refund.

## What you will learn

- How to run an attack several times against an agent with a write tool, and read the system of record as well as
  the reply.
- How to flag planted instructions in plain code, mark pasted text as data, and check a reply in code before the
  rep sees it, and how to count what each of these misses.
- How to moderate input with one API call, then inside the agent with `OpenAIModerationMiddleware`, and count the
  clean rep questions it blocks on a labelled set.
- How to filter a search by rep inside the search, keep the rep's identity in runtime context, and stop the model from
  filling the gap with another customer's ticket.
- How to plan for a model failure with `ModelRetryMiddleware`, `ModelFallbackMiddleware` and a safe message, and find
  the retries the client makes on its own.
- How to put the guards together, show which one stopped each part of the attack, and name the risk each one reduces.

## Coming from

In Lab 11 your copilot read ticket 16, pasted without `<ticket>` tags, and replied only *APPROVED - PAY IMMEDIATELY*
in 3 of 3 runs; a judge on the same model passed that reply, and only a code check caught it. That copilot could only
read. Lab 08 gave the copilot a write tool and a person to approve it. This lab gives the copilot the write tool
without the approval first, then adds guards one at a time and measures each.

## What you will do

**Part A: Run ticket 16 against the copilot with no guards.** Two forms of the attack (Lab 11's summary request, and a
rep asking the copilot to handle the ticket), three runs each, with the refund requests read back from the Ops API.
**Part B: Flag planted instructions in plain code.** A pattern for instruction-like lines, `<ticket>` tags around
pasted text, and Lab 11's reply checks as an output guard; then a labelled set of 13 inputs (10 rep requests to
answer, 3 to block) to count what the flag marks wrongly and misses.
**Part C: Moderate the input, then as middleware.** The moderation endpoint on three inputs and on the labelled set,
then `OpenAIModerationMiddleware` inside the agent: how many calls it makes per turn, what the rep sees on a block,
and a better block message.
**Part D: Filter the ticket search by rep, inside the search.** Who may read each ticket, a toy search filtered inside
and after, the real ticket search with a FAISS ID selector, and the same question asked as two reps; then a fix for a
model that answers from the wrong ticket.
**Part E: Plan for a model failure.** A chat model that cannot connect, the client's own retries, `ModelRetryMiddleware`
with its default and with a planned message, `ModelFallbackMiddleware`, and the safe message when everything fails.
**Part F: Run ticket 16 against the guarded copilot.** All the guards together on the same two forms of the attack,
three runs each, approval with Lab 08's decisions (no `respond`) and its review screen, the waiting refund
rejected, and the 13 labelled inputs run through the guarded copilot.
**Part G: Map each guard to what it stopped and the risk it reduces.** One table of the measurements, and the OWASP
risks for agentic applications each guard reduces.
**Challenge.** Catch the reworded attack with the flag and count the cost, moderate once per turn with your own
middleware, and show the flagged lines on the approval screen.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Ticket 16 three times in each of two forms, with the refund requests read back from the API. Ours: the handle form filed a request in 3 of 3 runs (9001 once, 9002 twice) with nobody seeing it; the summarise form tried to file in 3 of 3 and the API refused each; the look run filed for 9001 and replied only *APPROVED - PAY IMMEDIATELY*. The 4 requests rest on the shared tool's thread key; Lab 08's key would have filed 2 |
| Part B | The flag marks ticket 16 only, of 16 tickets; with `<ticket>` tags the summary still obeyed the planted line (ours: 3 of 3) and the reply check replaced each reply; on the labelled set the flag gives 2 false flags of 10 (L08, L09) and misses 2 of 3 (L12, L13) |
| Part C | Only the angry email of three inputs is flagged (harassment, ours 0.6542); on the labelled set moderation gives 1 false block of 10 (L07, a customer's threat) and misses both injections; in the agent it makes one call per model call plus one for the reply (ours: 4 for 3 model calls) |
| Part D | Steve may read 35 of 36 files, Jane 35, Margaret Park 34; the toy search returns two results filtered inside and one filtered after; without the note Jane's copilot called ticket 14 Helena's (ours: 3 of 3), with it the copilot found no ticket (3 of 3); four `True` comparisons with `shared/guards.py` |
| Part E | 3 attempts per call from the client alone; the default middleware makes 9 and shows the error text to the rep; with client retries off and a planned message, 3 attempts and the safe message; the fallback answers after 3 failed attempts; everything failing gives 6 attempts and the safe message |
| Part F | Guarded, the planted line flagged in 6 of 6 runs, every obeyed summary replaced (ours: 3 of 3), every proposed refund waiting for approval with the review screen (ours: 3 of 3; the screen showed that no policy was read), nothing filed; the labelled set: 1 false block of 10, 2 false flags, L12 through every guard |

Values come from a run on 11 Oct 2026, Part E's fallback and Parts F and G re-run the same day after the approval and
fallback settings changed (`gpt-4o-mini` as the copilot and the fallback, `omni-moderation-latest`,
`text-embedding-3-small`; Python 3.13.5, macOS, a fresh `uv sync`). The flag, the toy search and who may read which
ticket give the same values every time. Model replies vary between runs, and moderation scores move slightly: compare
which guard stopped what, not our counts. If `models.env` names another `CHAT_MODEL`, expect different replies.

## Before you start

- **Labs 07, 08 and 11 first** if you can: this lab uses the tools from Lab 07, the approval step from Lab 08 and the
  reply checks from Lab 11.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** ticket 16 and the other tickets in `data/corpus/`, `chinook.db` for each customer's rep, the handbook
  index in `data/index/`; all read in place. The notebook starts the Ops API on your machine; the refund requests it
  files go to a temporary database, never to a real system.
- **Cost:** about 90 `gpt-4o-mini` calls, a few dozen embedding calls and a few dozen moderation calls: a few US cents. Moderation calls are free.

The notebook ends with a troubleshooting table: the Ops API not running, requests left from an earlier part, missing
settings in an older `models.env`, a port in use, a resume with the wrong number of
decisions, counts that differ from ours, and a missing key.

## Resources

- [LangChain: guardrails](https://docs.langchain.com/oss/python/langchain/guardrails): deterministic and model-based guardrails, before and after the agent, layered in order
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `ModelRetryMiddleware` (its `on_failure` default is `"continue"`), `ModelFallbackMiddleware` and `HumanInTheLoopMiddleware`
- [LangChain: OpenAI middleware](https://docs.langchain.com/oss/python/integrations/middleware/openai): `OpenAIModerationMiddleware`, with `check_input`, `check_output`, `check_tool_results`, `exit_behavior` and `violation_message`
- [OpenAI: moderation](https://developers.openai.com/api/docs/guides/moderation): the categories, the scores and the `omni-moderation-latest` model
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): ASI01 to ASI10, December 2025
- [Simon Willison, The lethal trifecta for AI agents (2025)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/): private data, untrusted content and a way out
- [Beurer-Kellner et al., Design Patterns for Securing LLM Agents against Prompt Injections (2025)](https://arxiv.org/abs/2506.08837): six patterns that limit what an injected instruction can make an agent do
- [FAISS: searching with an ID selector](https://github.com/facebookresearch/faiss/wiki/Setting-search-parameters-for-one-query): `SearchParameters(sel=...)` and `IDSelectorBatch`

Next: [Lab 13, how to put the copilot on a web page](../13_Deploy_To_A_Space/README.md). Back to [the lab list](../README.md).
