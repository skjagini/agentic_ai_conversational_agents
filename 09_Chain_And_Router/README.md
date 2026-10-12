# Lab 09: How to choose between a chain, a router and an agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/09_Chain_And_Router/09_chain_and_router.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Part A runs without one) | Follows: Day 2 D2-M04, steps 4.1 to 4.7 (D2-M04-01 to D2-M04-39, slides 89–125; MCP, step 4.5, only in the optional Part H)**

## Goal

Choose the shape for a job from measurements: build a chain and a router in LangGraph, run the same requests through
the router and the agent, and compare their model calls, tokens, seconds and outcomes. The moment that teaches it:
request 5 asks for a policy and an order count. It was labelled `policy_question` in 3 of 3 runs, and the policy handler, which has no customer tool, searched the handbook 12 to 34 times for the count and never gave it: 13 to 35 model calls and 97,000 input tokens on average, where the agent answered both parts in 3 or 4 calls and about 4,100 tokens (`gpt-4o-mini`, 12 Oct 2026).

## What you will learn

- How to write a fixed sequence of steps as plain function calls, then as a LangGraph `StateGraph` with typed state,
  nodes and edges, and how to read the graph's structure and each step's update.
- How to find a chain's missing step by checking its output against the rule in code, and add the step.
- How to label a request with `with_structured_output` and a `Literal`, route on the label with an `if` and then a
  conditional edge, and test the labels against your own over several runs.
- How to put agents behind a router, each with only its tools, and resume a paused handler on the router's thread.
- How to measure model calls, tokens and seconds per request for a router and an agent, and how to split a request
  with two needs and send each part to its own handler with `Send`.
- How to choose a chain, a router or an agent for a job by asking who decides the next step, with evidence.

## Coming from

In Lab 08 the copilot became one agent with every tool, a person approving each refund. This lab puts fixed paths
beside it: a chain whose steps your code sets, and a router that labels a request and sends it to a handler with only
the tools that job needs. It imports the tools from `shared/ops_tools.py` and the handbook search from
`shared/copilot.py`, so you can start here. You need Lab 01's `create_agent`, Lab 02's typed intent label, Lab 05's
`search`, and Lab 08's approval and resume.

## What you will do

**Part A: Write a chain as a graph.** Write ticket 14's chain (extract, fetch, draft) as three functions with scripted
models, then as a `StateGraph`; print its nodes and edges and stream each step's update.
**Part B: Run the chain on ticket 14 and add the missing step.** Count every model call with a callback, run the chain
three times, check each note against the refund rule in code, then add a `rule` node and run it three times again.
**Part C: Route a request on a typed label.** Label the five requests, route with an `if`, compare labels with and
without definitions over three runs, build the router graph with a conditional edge, and count the calls on the
`out_of_scope` path.
**Part D: Put agents behind the router.** Give each handler only its tools, pause ticket 14 at the approval, find the
handler's messages, resume on a wrong thread and then on the router's, and run the other four requests.
**Part E: Measure the router against one agent.** Write a check for each request, run the five requests three times
through both shapes, and compare passes, calls, tokens and seconds.
**Part F: Split a request with two needs.** Ask for parts instead of one label, send each part to its handler with
`Send`, join the answers in code, and add the result to Part E's table.
**Part G: Choose the shape for a job.** Read the measurements, choose a shape for five support jobs, and decide the
copilot's shape.
**Part H (optional): Load tools from an MCP server.** Serve two read tools with FastMCP and load them through
`langchain.mcp.MCPAdapter`.
**Challenge.** A gate in front of the agent, a cap on the wrong handler, and a check inside the chain.

## Checkpoints

| After | You should see |
|---|---|
| Part A | nodes `__start__`, `extract`, `fetch`, `draft`, `__end__`; four edges in that order; invoices 9001 and 9002, both 9.99 on 2013-11-02, `course fixture`; each node adds its own key |
| Part B | three notes without the rule, none naming the refund (ours: 0 of 3); with the `rule` node all three name invoice 9002 (ours: 3 of 3); 2 chat calls per run either way |
| Part C | without definitions request 1 is labelled `refund_request` (ours: 3 of 3); with them every label is as expected; request 5 gets one label, `policy_question` (3 of 3); the poem's path makes 1 call, the label |
| Part D | ticket 14 waits at `('refund_request',)` with the router's messages `['human']` and the refund on 9002 pending; a resume on a thread named `refund_request` raises `IndexError`; on the router's thread request 1 is filed, `pending_review`; request 5 goes to the policy handler, which cannot give the order count (ours: 14 searches, 15 calls) |
| Part E | router: requests 1 to 4 pass 3 of 3, request 5 0 of 3 at 13 to 35 calls; agent: requests 1, 2, 3 and 5 pass 3 of 3 at 2 to 4 calls, the poem 0 of 3 |
| Part F | request 5 split into a policy part and an account part, 3 of 3 at 6 calls and about 4,170 input tokens, close to the agent's 4,085 |
| Part G | the worksheet: 1 chain, 2 router, 3 agent, 4 chain, 5 agent, each with its deciding fact |
| Part H | the beta warning, `find_customer` and `get_customer_invoices` loaded through `MCPAdapter`, and Puja's 6 invoices answered through them |

Values come from a run on 12 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Part A uses a scripted
model and gives the same values every time. Model runs vary: compare the counts and the kinds of failure, not our
wording.

## Before you start

- **Lab 00 first.** Its Part D starts the Ops API this lab uses, and its Part E proves your key works.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db` and the handbook index in `data/index/`, read in place. Invoices 9001–9003 are a course
  fixture inside `shared/ops_api.py`. The Ops API writes refund requests to a temporary database.
- **Optional Part H** installs `fastmcp` 4.1.0 into the notebook's environment; it changes no pinned package.
- **Cost:** about 270 `gpt-4o-mini` calls and 440,000 input tokens in our run, under 10 US cents; most of it is the router on request 5 in Part E, and that number varies most between runs.

The notebook ends with a troubleshooting table: a resume on the wrong thread, a missing `thread_id`, two `Send`
workers writing one key, a path name that is not listed, a missing node, a used-up scripted model, a paused run that
shows no tool calls, `asyncio.run` in a notebook, and the optional MCP package.

## Resources

- [LangGraph: workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents): prompt chaining, routing with `with_structured_output`, orchestrator-worker with `Send`, and agents, each as a graph
- [LangChain: multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent): the five patterns and when one agent is enough
- [LangChain: the router pattern](https://docs.langchain.com/oss/python/langchain/multi-agent/router): splitting a query and fanning out with `Send`
- [LangGraph: subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs): an agent as a node, its state and its interrupts
- [LangChain: Model Context Protocol](https://docs.langchain.com/oss/python/langchain/mcp): `MCPAdapter`, its install and its beta status
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): workflows beside agents, and when to use which

Next: [Lab 10, how to measure an agent's latency and cost](../10_Latency_Streaming_And_Cost/README.md). Back to [the lab list](../README.md).
