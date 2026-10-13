# Course outline: Agentic AI: Conversational Agents

Two days, one case: a support copilot for the reps of Chinook, a fictional online music shop. Every lab adds one
piece to the same copilot. Labs marked *self-study* are complete on their own, and no in-class lab depends on them.

## Day 1: Build an agent that talks, remembers and uses tools

**Goal.** By the end of Day 1 you can tell a single model call, a fixed workflow and an agent apart; write the
model–tool loop by hand and then with LangChain; write a dialogue prompt and test it with checks in code; keep a
conversation's state and keep private data out of it; and turn an API into tools the agent calls safely.

| Lab | Title | In class or self-study |
|---|---|---|
| 00 | [How to set up the lab environment](00_Environment_Check/README.md) | in class |
| 01 | [How to build a tool-calling agent](01_First_Chain_And_Tool/README.md) | in class |
| 02 | [How to write a dialogue prompt and test it](02_Dialogue_Prompt_Versions/README.md) | in class |
| 03 | [How to give an agent memory](03_Thread_Memory_Three_Settings/README.md) | in class |
| 04 | [How to remember a rep across conversations, and forget a customer](04_Long_Term_Memory_And_Privacy/README.md) | self-study |
| 05 | [How to turn an API into tools an agent can call](05_Tools_Over_The_Ops_API/README.md) | in class |
| 06 | [How to choose between a workflow and an agent](06_Chain_And_Router/README.md) | in class |

## Day 2: Ground it, control it, measure it and ship it

**Goal.** By the end of Day 2 you can give the agent a document search tool and make it cite its sources or say it
has no answer; put a person's approval in front of every action that changes data; evaluate the agent on task
success, tool choice, arguments, grounding, latency and cost; guard it against misuse and failure; and put it on a web
page others can use.

| Lab | Title | In class or self-study |
|---|---|---|
| 07 | [How to search documents by meaning](07_FAISS_Index_Handbook/README.md) | self-study |
| 08 | [How to give an agent a document search tool](08_RAG_Citations_Abstention/README.md) | in class |
| 09 | [How to ask a person before an agent acts](09_Approval_Before_A_Write/README.md) | in class |
| 10 | [How to evaluate an agent](10_Evaluation_Set/README.md) | in class |
| 11 | [How to measure an agent's latency and cost](11_Latency_Streaming_And_Cost/README.md) | self-study |
| 12 | [How to guard an agent against misuse and failure](12_Guardrails_And_Injection_Test/README.md) | in class |
| 13 | [How to put the agent on a web page](13_Deploy_To_A_Space/README.md) | in class |
