# Lab 08: How to make an agent wait for approval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/08_Approval_Before_A_Write/08_approval_before_a_write.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Parts A and B run without one) | Follows: Day 2 D2-M03, steps 3.1 to 3.6 (D2-M03-01 to D2-M03-40, slides 55–88)**

## Goal

Make the copilot pause before every refund request, give the reviewer a screen with the facts needed to decide, and
resume the paused conversation with approve, edit or reject, even after a restart. The moment that teaches it: with a person
approving and four checks passing, ticket 14 still ends with three refund requests for one duplicate charge (ours,
`gpt-4o-mini`, 10 Oct 2026), because each new conversation about the ticket filed its own.

## What you will learn

- How to make a write tool wait for a person with `HumanInTheLoopMiddleware`, why the pause needs a checkpointer and
  a `thread_id`, and how to check that no write tool was left out.
- How to read a pending action from `result.interrupts` and resume the same thread with approve, edit or reject
  (`Command(resume=...)`), and what the model reads after each decision.
- How to give the reviewer a screen with the real arguments and the facts behind them (a `description` function).
- How to test a write with a real model: four checks on ticket 14, a 120.00 request run three times, and which layer
  acted: the prompt, the reviewer or the API's own rule.
- How to stop two conversations from filing the same refund, with an idempotency key built from the refund rather
  than the conversation, and how to end a case with a typed hand-off record.
- How to keep a paused approval across a restart with `SqliteSaver`, and check that a thread is waiting before you
  resume it.

## Coming from

In Lab 07 you wrote typed tools over the Ops API, kept the rep's id out of the model's hands, and saw three runs of
one message file three refund requests for one duplicate charge, with nobody seeing them first. This lab puts a person
in front of the write and asks whether that is enough. It imports the tools from `shared/ops_tools.py`, so you can
also start here without Lab 07. You need Lab 01's agent, Lab
03's checkpointer and thread (`InMemorySaver`, `SqliteSaver`) and Lab 06's `search_policies`, whose artifact the review
screen reads.

## What you will do

**Part A: Pause before the write.** Decide which of six tools need approval, configure `interrupt_on` (with
`"get_invoice": False`), check that every write tool has a setting, and pause a scripted ticket 14 run before
`file_refund_request`. Read the interrupt and the saved state, then approve.
**Part B: Edit, reject or respond.** Edit invoice 9001 to 9002, reject with a reason, try `respond` where it is not
allowed, and approve a scripted 120.00 request that the API files for the manager.
**Part C: Run ticket 14 with a real model.** Write a review screen (`description`), run ticket 14 to the pause, read the
screen, approve, and run four checks on the run.
**Part D: Run ticket 14 again, and the 120.00 request.** Run ticket 14 in two more conversations and the 120.00 request three
times; name the layer that acted; read the API's refund requests and find three for one duplicate charge.
**Part E: One refund request per invoice, and a hand-off record.** Build the idempotency key from the invoice and
amount, repeat the two conversations, and end the case with `response_format=HandoffRecord`.
**Part F: Approve after a restart.** Pause with `SqliteSaver`, reopen the file in a new agent, resume with a mistyped
thread id and then the right one, and write `resume_if_waiting`.
**Challenge.** Let the reviewer change the amount, answer two pending refunds in one step, and compare a rejection
with and without a reason.

## Checkpoints

| After | You should see |
|---|---|
| Part A | `interrupt_on` keeps only `file_refund_request` (`False` is dropped); the typo check finds `{'file_refund_request'}`; the scripted run pauses with six messages before `HumanInTheLoopMiddleware.after_model`, nothing filed; after approval request 1, `pending_review` |
| Part B | edit: the tool message starts *Note: a human reviewer replaced this tool call before it ran* and files 9002, while the model's message keeps 9001; reject: status `error`, the reason in the text, nothing filed; respond: `ValueError` naming the allowed decisions; 120.00 approved and filed as `needs_manager` |
| Part C | reads before the pause (ours: both invoices, then `search_policies`); pending call `{"invoice_id": 9002, "amount": 9.99, "reason": "duplicate_charge"}`; the screen shows 2013-11-02, total 9.99, customer 16, course fixture and the policies read; after approval request 1, `pending_review`; the four checks `True` |
| Part D | ticket 14 passes the four checks in each conversation (ours: 3 of 3); the 120.00 request is filed as `needs_manager` or not filed (ours: filed in 2 of 3, never escalated before proposing); the API holds **three** `pending_review` requests for invoice 9002, one per conversation |
| Part E | Monday files request 1; Tuesday gets request 1 back with `replayed: True`; the record: customer 16, invoices `[9001, 9002]`, `refund_requested`, request 1, `pending_review`, `['policy_refunds.md']` (ours: `ticket` held a sentence, not a number) |
| Part F | after the restart the thread still waits with the same screen; the mistyped thread runs the model on an empty conversation and files nothing; `resume_if_waiting` refuses it and resumes the real thread (request 1, `replayed: True`) |

Values come from a run on 10 Oct 2026 (`gpt-4o-mini`, Python 3.13.5, macOS, a fresh `uv sync`). Parts A and B use a
scripted model and give the same values every time. Model runs vary: compare the facts and the API's records, not our
wording. A reference run on 5 Oct 2026 with `gpt-6-luna` escalated the 120.00 request without filing it.

## Before you start

- **Lab 00 first.** Its Part D starts the Ops API this lab uses, and its Part E proves your key works.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db` and the handbook index in `data/index/`, read in place. Invoices 9001–9003 are a course
  fixture inside `shared/ops_api.py`. The Ops API writes refund requests to a temporary database, and Part F writes
  `lab08_approvals.sqlite` to your temporary folder.
- **Cost:** about 45 `gpt-4o-mini` calls and a few embedding calls: a few US cents at most.

The notebook ends with a troubleshooting table for the usual failures: a run that never pauses, a missing
`version="v2"` or `thread_id`, the wrong number of decisions (and a thread stuck after it), a decision the tool does
not allow, a resume on the wrong thread, a missing `context`, SQLite across threads, and an API that is not running.

## Resources

- [LangChain: human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop): `interrupt_on`, the four decisions, several pending actions, and the advice on edits and rejections
- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts): how a pause is saved and resumed with `Command(resume=...)`
- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence): threads, checkpoints and the savers for production
- [LangChain: structured output](https://docs.langchain.com/oss/python/langchain/structured-output): `response_format` on `create_agent`
- [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests): how a payments API uses idempotency keys for safe retries, and how long it keeps them

Next: [Lab 09: How to choose between a chain, a router and an agent](../09_Chain_And_Router/README.md). Back to [the lab list](../README.md).
