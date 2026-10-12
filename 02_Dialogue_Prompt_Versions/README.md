# Lab 02: How to write a dialogue prompt and test it

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/02_Dialogue_Prompt_Versions/02_dialogue_prompt_versions.ipynb)

**CPU | API key: `OPENAI_API_KEY`**

## Goal

Write the copilot's system prompt, and judge every change to it with a small test in code instead of by reading
replies. The moment that teaches it: asked whether a customer can pay with Bitcoin, the copilot replies that no
policy covers payment methods and the rep should ask the manager. It sounds careful and it is wrong: it asked for a
policy name that does not exist and gave up. The test catches it; one worked example in the prompt fixes it.

## What you will learn

- How to write a system prompt as a plain string, then grow it into sections: identity, instructions and context.
- How to keep each prompt version in a file with a header, and print what changed between two versions.
- How to build a small test: fixed questions, an answer key the model never sees, and checks written as plain
  functions that you test before you trust them.
- How to read a test result one row per question, and then the failing replies behind each row.
- How to add one worked example to a prompt (few-shot) to fix a failing case, and check every row after the change.

## Coming from

Lab 01 built an agent with one tool, `get_policy`, and a one-line system prompt. This lab keeps the tool and works on
the prompt.

## What you will do

**Part A: Write a first prompt and read its replies.** Give the agent a weak prompt, `v0`, and ask about a 150-dollar
refund three times.
**Part B: Build a test you can run after every change.** Six rep questions with an answer key the model never sees;
two checks, `right_policy` (did it read a file that answers the case?) and `has_fact` (does the reply say the key
point?), tried on one real run and on hand-written replies; then `run_tests` and `show` score `v0` three times per
question.
**Part C: Grow the prompt into sections.** Save each version to `prompts/` with a header, grow `v0` into identity,
instructions and context (`v1`), run the test and read the failing replies.
**Part D: Add one example to fix a failing case.** Add one worked example aimed at the Bitcoin question, save it as
`v2`, diff the versions, compare every row, and run a row that moved ten more times before deciding what moved it.
**Going further.** Score a rule (under 80 words) on the runs you already have; the 20 policy names in the tool's
description; a test question that repeats the prompt's example.
**Challenge.** Fix one more case as `v3`, then test `v1`, `v2` and `v3` on two questions none was written on.

## Checkpoints

| After | You should see |
|---|---|
| Part A | three replies worded differently; ours approved the 150-dollar refund 3 of 3 |
| Part B | Part A's question scored once: `right_policy` `True`, `has_fact` `False`; the hand-written replies pass and fail both checks; `v0` passes both in few runs (ours: 3 of 18, all `duplicate`) |
| Part C | `copilot_v0.md` and `copilot_v1.md` in `prompts/`; `v1` passes more (ours: 9 of 18), with `crypto` asking for `payment methods` and saying no policy covers it |
| Part D | a diff with one added `# Examples` section; `crypto` passes (ours: 0 of 3, then 3 of 3; 11 of 18 in all); a row that moved, run ten times (ours: `duplicate` 9 of 10 with `v1`, 10 of 10 with `v2`, which tried another policy name first in 9 of 10) |

The saved outputs come from `gpt-4o-mini` on 12 Oct 2026. Replies and counts change from run to run, and from model
to model if `models.env` names another one: compare which cases fail and why, not the exact numbers.

## Before you start

- **Labs 00 and 01 first.** Lab 01 writes `get_policy`, which this lab copies.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the 20 policy files in `data/corpus/` (course-authored), read in place. The notebook writes its prompt
  versions to `prompts/` in this folder (not part of the repository). Nothing is downloaded.
- **Cost:** about 200 calls to the chat model, a few US cents with `gpt-4o-mini`. Most are the test runs, so keep a
  test set small and fixed.

The notebook ends with a troubleshooting table for the usual failures: a prompt version loaded before it was saved, a
keyword check that misses a right reply or passes a wrong one, a test question that copies an example.

## Resources

- [OpenAI: prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering): message roles, prompt sections, few-shot examples, evaluations
- [OpenAI: evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): test sets written before the run, checks in code, judging every change
- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools): a tool's name, description and arguments

Next: [Lab 03: How to give an agent memory](../03_Thread_Memory_Three_Settings/README.md). Back to [the lab list](../README.md).
