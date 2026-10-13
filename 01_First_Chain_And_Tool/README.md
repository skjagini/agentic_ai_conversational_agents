# Lab 01: How to build a tool-calling agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/01_First_Chain_And_Tool/01_first_chain_and_tool.ipynb)

**CPU | API key: `OPENAI_API_KEY`**

## Goal

Build an agent from its parts: call a model, describe a tool, run the tool when the model asks for it, and loop until
the model answers. You write that loop by hand on OpenAI's Responses API, then rebuild it in a few lines with
LangChain's `create_agent`. Watch the reply when the model needs a shop policy: it is a request to run `get_policy`,
and nothing runs until your code runs it.

## What you will learn

- How to call a model with `client.responses.create` and read the reply's text and token usage.
- Why your code sends the whole conversation with every call.
- How to describe a tool to the model as a JSON schema.
- How to read a `function_call`, run the function and send back a `function_call_output`.
- How to write the agent loop, and how the model decides on each question whether to call a tool.
- How `@tool` and `create_agent` replace your schema and your loop, and what is still your job.

## Coming from

Lab 00 checked the environment and asked the chat model one question. This lab starts from that call. You need a
little Python; no LangChain is assumed.

## What you will do

**Part A: Call the model once.** One `client.responses.create` call with the download-link question from Lab 00. Read
the reply, its token usage and its output items, and compare the reply with `policy_digital_downloads.md`.
**Part B: Send the conversation with every call.** Ask a follow-up alone, then again with the history, and see that
the model keeps nothing between calls.
**Part C: Describe a tool to the model.** Write `get_policy` in plain Python, describe it as a JSON schema, and read
the `function_call` the model sends back instead of text.
**Part D: Run the tool and send the result back.** Parse the arguments, run the function, return a
`function_call_output`, then write the loop that runs until a reply has no function call.
**Part E: Ask a question that needs no tool.** Join the pieces in one function and ask a policy question and a
wording request with the same tool: the model decides which needs it.
**Part F: Build the same agent with LangChain.** Wrap `get_policy` with `tool`, print its schema beside yours, build
the model with `ChatOpenAI` and read the `chat_model` helper later labs use, run `create_agent` and display its graph,
and list what LangChain now does for you and what is still yours.
**Challenge.** Put the policy names in the tool's description and check which policy an answer really came from,
with a cell that counts the model calls; as an extension, cap the loop with a call limit.

## Checkpoints

| After | You should see |
|---|---|
| Part A | a period that is not Chinook's 90 days (ours: 14 days); about 30 input tokens and 0 reasoning tokens; one `message` item |
| Part B | the follow-up alone knows nothing about download links; with the history it shortens the first answer, with more input tokens |
| Part C | `output_text` empty and one `function_call` for `get_policy` with a JSON string of arguments |
| Part D | the answer gives 90 days after purchase and one new link that lasts 7 days, after 2 model calls, or 3 when the first policy name is wrong |
| Part E | the download question reads `digital_downloads` (after a wrong name, in our run); the wording request reads no policy |
| Part F | the same name, description and argument in both schemas; `chat_model`'s source builds the same `ChatOpenAI`; a `CompiledStateGraph` whose `model` and `tools` nodes are your loop; the agent's messages map onto your loop; the wording request gives 2 messages |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026. Replies and counts change from run to run, and from model
to model if `models.env` names another one: check the facts (90 days, 7 days) and the shape of the run, not the
wording.

## Before you start

- **Lab 00 first.** It checks that your key reaches the chat model.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the 20 policy files in `data/corpus/` (course-authored), read in place. Nothing is downloaded.
- **Cost:** about 20 calls to the chat model, a few thousand tokens in all: well under one US cent with `gpt-4o-mini`.

The notebook ends with a troubleshooting table for the usual failures: a function call sent back without its output
(or the other way round), a strict schema without `additionalProperties`, arguments used without `json.loads`, a
docstring the tool wrapper cannot read, a graph that will not draw offline, a missing key.

## Resources

- [OpenAI: function calling](https://developers.openai.com/api/docs/guides/function-calling): tools, `function_call`, `function_call_output`, strict mode, reasoning items
- [OpenAI: migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses): `instructions`, `input`, output items, `previous_response_id`
- [LangChain: tools](https://docs.langchain.com/oss/python/langchain/tools) and [agents](https://docs.langchain.com/oss/python/langchain/agents): `@tool` and `create_agent`
- [LangChain: `ChatOpenAI`](https://docs.langchain.com/oss/python/integrations/chat/openai): `use_responses_api`, `reasoning_effort`
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): the model call limit in the challenge

Next: [Lab 02: How to write a dialogue prompt and test it](../02_Dialogue_Prompt_Versions/README.md). Back to [the lab list](../README.md).
