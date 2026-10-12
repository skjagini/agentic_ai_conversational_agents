# Lab 01: How to build a tool-calling agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/01_First_Chain_And_Tool/01_first_chain_and_tool.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Follows: Day 1 D1-M03, steps 3.2 to 3.6 (D1-M03-08 to D1-M03-52, slides 61–101)**

## Goal

In Lab 00 the model answered a question about Chinook's download links fluently and wrongly. In this lab you give it
a tool and run the tool call round trip yourself: the model asks for `get_policy`, your code runs it, you send the
result back, and the model answers from the policy. Then you let `create_agent` run the same loop and count its model
calls. The moment that teaches it: the same question that got a confident wrong answer now takes two or three model
calls, and the tool ran in your code each time, never in the model.

## What you will learn

- How to build the chat client from `models.env`, what each argument does, and why `reasoning_effort` is left out for
  `gpt-4o-mini`.
- How to read a model's reply (its text, its tool calls and its token counts), and why a fluent answer can still be
  wrong.
- How a tool's signature and docstring become the schema the model reads.
- How to run one tool call round trip by hand: the model asks, your code runs the tool, you send the result back, and
  the model answers.
- How `create_agent` runs the same loop for you, and how to count its model calls and tokens.
- How to recognise the older `prompt | model | parser` and `LLMChain` styles in code you read.

## Coming from

Lab 00 checked the environment and asked the chat model one question; the answer was fluent and wrong for Chinook.
This lab starts from that call. You need only Lab 00 and a little Python: no LangChain is assumed.

## What you will do

**Part A: One model call and its token usage.** Build `ChatOpenAI` by hand from `CHAT_MODEL` in `models.env` and see
what each argument does, including why `reasoning_effort` is left out for `gpt-4o-mini`. Ask how long a download link
lasts, compare the reply with `policy_digital_downloads.md`, and read `usage_metadata`. An optional demo, for an
account that can use a reasoning model, runs the same question on `gpt-5` at three reasoning efforts.
**Part B: Recognise an older composition style (an aside).** Run `prompt | model | parser` once and see the
deprecation warning that `LLMChain` prints, so you can read both in older tutorials. Current code builds agents with
`create_agent` and fixed paths as LangGraph workflows ([Lab 09](../09_Chain_And_Router/README.md)).
**Part C: A tool and its schema.** Write `get_policy`, print the JSON schema the model receives, and call the tool
with a known name and an unknown one.
**Part D: The agent decides.** Let the model ask for the tool, run it yourself, send the result back and print the
answer; finish the loop by hand with `while`. Then let `create_agent` run the same loop, print every message, count
the model calls and watch the input tokens grow.
**Part E: Label the run.** Label each message of your run with its role, who produced it and its turn step, then
say in two sentences what the single call in Part A could not do.
**Challenge.** Put the policy names in the tool's description, cap the agent loop with a call limit, and check which
policy an answer really came from.

## Checkpoints

| After | You should see |
|---|---|
| Part A | `reasoning_effort="low"` on `gpt-4o-mini` refused with status 400 (`Unsupported parameter: 'reasoning.effort' ...`; a reasoning model accepts it); a reply that does not give Chinook's 90 days (ours: 24 to 48 hours); `tool_calls` `[]`; 30 input and 31 output tokens in our run (`gpt-4o-mini`, 11 Oct 2026), 0 reasoning |
| Part A, optional demo | `gpt-5` at effort `low`: 512 of 587 output tokens were reasoning; at `minimal`, `low`, `high`: 0, 384, 1,920 reasoning tokens (seconds vary: 11.9, 5.3, 16.9); no answer gives 90 days (`gpt-5`, 11 Oct 2026) |
| Part B | the chain is a `RunnableSequence` and returns a string, still without 90 days; `LangChainDeprecationWarning`: `LLMChain` "was deprecated in LangChain 0.1.17 and will be removed in 2.0.0" |
| Part C | 20 policy names; schema `get_policy` with one required string `name`; `get_policy("vip")` returns `No policy named 'vip'. Known: ...` with all 20 names |
| Part D | the step by hand returns no text and one tool call (ours: `digital downloads`, a wrong name); sent back with the `ToolMessage`, the model asks again with `digital_downloads`, and the `while` loop ends on the answer: 90 days after purchase and one new link that lasts 7 days (ours: 3 model calls); `create_agent` returns a `CompiledStateGraph` and gives the same facts; 6 messages and 3 model calls in our run, a wrong name first (input 96, 181, 292 tokens; `gpt-4o-mini`, 11 Oct 2026), or 4 messages and 2 calls when the first name is right |
| Part E | every message labelled: the rep's question (step 1), each tool call from the model (step 4), each tool message from your code (step 5), the reply from the model (step 4, then 6) |

Values come from a run on 11 Oct 2026 (`gpt-4o-mini-2024-07-18`, and `gpt-5` for the optional demo; Python 3.13.5,
macOS, a fresh `uv sync`). Model replies and token counts change from run to run, and from model to model if
`models.env` names another one: check the facts (90 days, 7 days) and the shape of the run, not the wording. A
reference run with `gpt-6-luna` (5 Oct 2026) said "24 hours" in Part A and made three model calls in Part D.

## Before you start

- **Lab 00 first.** Its Part E proves that your key reaches the chat model.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the 20 policy files in `data/corpus/` (course-authored), read in place. Nothing is downloaded.
- **Cost:** about eight `gpt-4o-mini` calls, a few thousand tokens in all: well under one US cent.
- **Optional reasoning demo (end of Part A):** four calls to `gpt-5`, the model named by `REASONING_MODEL` in
  `models.env`, for about two US cents. It is there for the instructor to show reasoning effort. ⚠️ If your account can
  use only `gpt-4o-mini`, set `RUN_REASONING_DEMO = False` in that cell before you run it; the notebook shows our
  results, and nothing later needs the demo.

The notebook ends with a troubleshooting table for the usual failures: the refused `reasoning_effort`, a tool result
missing when you send it back by hand, a docstring the tool decorator cannot read, a reasoning model your account cannot use, an agent that never calls the tool, a
missing key.

## Resources

- [LangChain: models](https://docs.langchain.com/oss/python/langchain/models) and [`ChatOpenAI`](https://docs.langchain.com/oss/python/integrations/chat/openai): the client and its arguments
- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools) and [agents](https://docs.langchain.com/oss/python/langchain/agents): `@tool` and `create_agent`
- [LangGraph: workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents): fixed paths such as prompt chaining and routing, the current way to build what Part B's chain does ([Lab 09](../09_Chain_And_Router/README.md))
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): the model call limit in the challenge
- [OpenAI: function calling](https://developers.openai.com/api/docs/guides/function-calling) and [reasoning models](https://developers.openai.com/api/docs/guides/reasoning)

Next: [Lab 02: How to write a dialogue prompt and test it](../02_Dialogue_Prompt_Versions/README.md). Back to [the lab list](../README.md).
