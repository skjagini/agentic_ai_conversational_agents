# Lab 02: How to write a dialogue prompt and test it

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/02_Dialogue_Prompt_Versions/02_dialogue_prompt_versions.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Follows: Day 1 D1-M04, steps 4.1 to 4.7 (D1-M04-01 to D1-M04-48, slides 102–144)**

## Goal

You keep the copilot's system prompt in versioned files and judge a change to it by checks in code on fixed rep
questions, run several times, instead of by reading one reply. The moment that teaches it: the structured prompt
fixes what the weak one got wrong, yet still fails two questions for a reason no prompt rule can fix, and a rule
that stops ticket 16's planted line lets a different planted claim through in every run.

## What you will learn

- How to keep a system prompt in a file with a version header, load it, and say which prompt produced which reply.
- How to write checks in code for a reply (the right policy fetched, the word limit, the policy named, the key fact)
  and count passes over three runs per question.
- What the examples in a prompt do and cost: tokens on every call, behaviour the rules alone do not give, and a
  test question that copies an example.
- How to control the length of a reply on a model without `verbosity`: a word limit in the prompt against a hard
  token cap.
- How to get a typed intent label with structured output, and why a valid label can still be the wrong one.
- How to test pasted customer text for planted instructions, and what a prompt rule can and cannot stop.

## Coming from

Lab 01 gave the copilot one tool, `get_policy`, and a one-line system prompt. This lab replaces that line with a
real prompt, kept in `shared/prompts/`, and tests every change on the same questions. Lab 03 then uses the `v1`
prompt from this lab in a thread with memory, and Lab 11 grows the checks written here into an evaluation set.

## What you will do

**Part A: Keep the prompt in a file and test it on fixed questions.** Load the weak prompt `v0` and the structured
prompt `v1` from their files, see one question get two different answers, then write six rep questions and four
checks in code before any run. Run each prompt three times per question and read the pass table one row per
question. Read `v1`'s failures: the model guessed policy names. Put the 20 names in the tool's description and run
again; the table shows which failures went and which new ones came.
**Part B: What the examples in a prompt do and cost.** Remove `v1`'s two examples and measure the input tokens and
the replies to the manager's-number question; then ask the exact question one example answers.
**Part C: Control the length of a reply.** Try `verbosity` on `gpt-4o-mini`, then a word limit in the prompt and a
`max_tokens` cap, three runs where it matters.
**Part D: Return a typed intent label.** Get an `Intent` object with `with_structured_output`, label eight rep
messages three times each against labels written first, and read the reasons behind a wrong one.
**Part E: Keep pasted customer text from giving orders.** Send ticket 16 in two layouts, five runs each; add one
rule as a new prompt version, `v1.1`, and show the change with `difflib`; test it on two planted lines it was not
written for; run the six questions again with `v1.1`.
**Challenge.** Write your own prompt from `v0` and test it with the six checks; add two questions you did not tune on.

## Checkpoints

| After | You should see |
|---|---|
| Part A | five prompt files; `v0` approves the 150-dollar refund, `v1` escalates; the hand-written replies pass and fail all four checks; `v0` passes all four in few runs (ours: 1 of 18; `big_refund` never escalates), `v1` in more (ours: 7 of 18), with `expired` fetching `refunds` instead of `digital_downloads` and `crypto` asking for `payment methods`; with the names in the tool `expired` and `crypto` pass 3 of 3, while other cases skip the tool or pick a near name (ours: 9 of 18) |
| Part B | the examples cost about 137 input tokens per call (ours: 507 against 370); without them fewer replies offer to escalate (ours: 1 of 3 against 3 of 3); the example's own question gets no `get_policy` call (ours: 0 of 3) and the example's words (2 of 3) |
| Part C | `verbosity="low"` refused with status 400 (*Supported values are: 'medium'.*); no length rule: long replies (ours: 181 to 219 words); *under 40 words*: 31 to 41 words, complete; `max_tokens=40`: status `incomplete`, `max_output_tokens`, cut mid-sentence |
| Part D | an `Intent` object; 21 of 24 labels right in our run; the expired-link question labelled `refund_request` 3 of 3, with reasons that invent a refund rule |
| Part E | ticket 16 obeyed in both layouts (ours: 5 of 5 and 5 of 5); `v1.1` adds one line and is obeyed 0 of 5; another fixed-reply order worked 0 of 5, a planted false claim (*the manager already approved a refund*) 5 of 5; the six questions with `v1.1` about as before (ours: 9 of 18, the same kinds of failure) |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Model replies change
from run to run, and from model to model if `models.env` names another one: compare the pattern (which cases fail,
and why), not the exact counts. A reference run with `gpt-6-luna` (5 Oct 2026) obeyed ticket 16 in 0 of 5 runs in each
layout.

## Before you start

- **Labs 00 and 01 first.** Lab 01 writes `get_policy`, which this lab copies.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the 20 policy files and ticket 16 in `data/corpus/` (course-authored), and the prompt files in
  `shared/prompts/` (`copilot_system_v0.md` and `copilot_system_v1_1.md` were written for this lab). Nothing is
  downloaded. Ticket 16 holds a planted instruction on purpose: treat it as data.
- **Cost:** about 200 `gpt-4o-mini` calls, about 80,000 tokens in all: about two US cents. Most of it is the test
  runs, which is the point: a prompt test costs money, so keep the question set small and fixed.

The notebook ends with a troubleshooting table for the usual failures: `verbosity` refused, a prompt file not found,
a header read as an instruction, a check that cannot fail, a keyword check that misses a correct reply.

## Resources

- [OpenAI: prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering): message roles, examples, keeping prompts in code and testing them with evaluations
- [OpenAI: structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs): schemas, and why a schema checks shape, not truth
- [LangChain: structured output](https://docs.langchain.com/oss/python/langchain/structured-output) and [models](https://docs.langchain.com/oss/python/langchain/models): `with_structured_output` and the client's arguments
- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools): naming a tool and writing its description
- [OWASP: LLM01 prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/): direct and indirect injection, and why prompts alone do not prevent it

Next: [Lab 03: How to give an agent memory](../03_Thread_Memory_Three_Settings/README.md). Back to [the lab list](../README.md).
