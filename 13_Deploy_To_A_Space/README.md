# Lab 13: How to put the copilot on a web page

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/13_Deploy_To_A_Space/13_deploy_to_a_space.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Part A and the sign-in check in Part E run without one) | Hugging Face account: only for the optional push in Part F | Follows: Day 2 D2-M08, steps 8.1 to 8.6 (D2-M08-01 to D2-M08-56, slides 222–269)**

## Goal

Serve the copilot as a chat page a colleague can open, with one conversation per visitor, a reply the rep sees only
after it is checked, and refunds that wait for a click. When we ran it (`gpt-4o-mini`, 11 Oct 2026), a page that
used one thread id for everyone answered a second visitor with the first visitor's customer and invoices in 3 of 3
runs, and a page that streamed the reply word by word showed the rep ticket 16's *APPROVED - PAY IMMEDIATELY* before
the reply check replaced it in 3 of 3 runs. One line (the visitor's session as the thread id) fixed the first;
streaming the tool steps and holding the reply until it passed the check fixed the second.

## What you will learn

- How to turn a Python function into a chat page with Gradio's `ChatInterface`, and drive the page from code as two
  visitors with `gradio_client`.
- How to give each visitor their own conversation by using the browser session as the agent's `thread_id`, and what
  happens when you do not.
- How to stream progress (the tool steps) while the reply waits for its check, and measure what the rep sees first.
- How to approve or reject a refund inside the chat with a button or a typed reason, and read the result from the API.
- How to keep the key out of your files, put a password on a page before you share its link, and check a Space
  folder (header, files, pins, secrets) before anyone builds it.
- How Streamlit runs the same copilot differently, and what a Space needs (and costs) to go live.

## Coming from

Lab 12 finished the guarded copilot: moderation, approval before the write, a fallback model and retries inside the
agent; the flag, the `<ticket>` tags and the reply check in the rep's app around it. This lab moves that app from a
notebook function to a web page, and the guards come with it unchanged.

## What you will do

**Part A: Put a function behind a chat page.** An echo function behind `gr.ChatInterface`, two visitors driven from
code with `gradio_client`, and the session id Gradio gives each visitor.
**Part B: Put the copilot behind the page, one thread per visitor.** Lab 12's guarded copilot behind the page, first
with one thread id for everyone (two reps, three runs), then with the visitor's session as the thread.
**Part C: Stream progress, and check the reply before the rep sees it.** A page that streams the reply word by word,
timed, and ticket 16 through it three times; then a page that streams the tool steps as folded messages and shows the
reply only after Lab 12's check. The planted string reaches the page only when the model obeys it, so both pages run
once more with a scripted model that always does.
**Part D: Approve a refund inside the chat.** The page function that joins every piece: a waiting refund with an
Approve button, one approval, one rejection with a typed reason, the API read back, and a reload while a refund waits.
**Part E: Keep the key secret and share the page safely.** Where the key lives, why a share link needs a password, and
a sign-in checked from code (a share link behind a switch).
**Part F: Prepare the files a Space needs.** The template in `space/`, its README header field by field, the app
checked against the notebook, the folder assembled and checked for four mistakes, and `app.py` run as the Space would
run it, without and with a key. The push to a Space is optional.
**Part G: Compare Streamlit's way of running the same copilot.** The rerun model side by side with Gradio, and
`resources/streamlit_app.py`, the same copilot in Streamlit.
**Challenge.** Keep a waiting refund across a reload with a sign-in, and file one request per refund whoever approves
it.

## Checkpoints

| After | You should see |
|---|---|
| Part A | The echo page counts 0, then 2 earlier messages for one visitor and 0 for a new one; each visitor has their own session id |
| Part B | With one thread for everyone, rep B's reply names Helena Holý, whom only rep A asked about (ours: 3 of 3 runs); with the session as the thread, it does not (ours: 0 of 3) |
| Part C | Word by word, the first words after a few seconds (ours: 2.5 s) and ticket 16's planted string shown before the check replaced it (ours: 3 of 3 runs); with tool steps streamed and the reply held, a folded tool step first (ours: 1.5 s) and the planted string never shown as a reply (ours: 0 of 3). With the scripted model: the whole string shown word by word on the first page, never on the second |
| Part D | Ticket 14 pauses with a refund for one invoice (ours: 9.99 for invoice 9002) and an Approve button; *approve* files it as `pending_review`; a typed reason rejects it and nothing is filed; after a reload, *approve* is a new message and nothing is filed |
| Part E | Without the password the page answers 401 and the client raises `AuthenticationError`; with it, the reply greets the user by name |
| Part F | The header says `sdk: gradio`, `sdk_version: 6.29.0`, `python_version: "3.13"`, `app_file: app.py`; six functions the same in the notebook and `app.py`; the assembled folder has 54 files and no problems, the broken copy 16; without a key the app serves a page that says so; with the key it answers from the folder |

Values come from a run on 11 Oct 2026, Part C's scripted check and Part F re-run the same day after the fallback
setting changed (`gpt-4o-mini` as the copilot and the fallback, `omni-moderation-latest`,
`text-embedding-3-small`, Gradio 6.29.0; Python 3.13.5, macOS, a fresh `uv sync`). Parts A, E and F's checks give the
same results every time; model replies and timings vary between runs. If `models.env` names another `CHAT_MODEL`,
expect different replies.

## Before you start

- **Labs 08 and 12 first** if you can: the page uses the approval step from Lab 08 and the guarded copilot from Lab 12.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session. The pages appear under
  their cells. Part G's Streamlit run is for your own machine. This lab has not yet been run on Colab.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel. Open each page's
  address in your browser to try it by hand.
- **Data:** `chinook.db`, the handbook index and the corpus in `data/`, read in place; Part F copies them into a folder
  in your system's temporary folder. The notebook starts the Ops API on your machine; the refund requests it files go
  to a temporary database, never to a real system.
- **Hugging Face:** creating a Gradio or Docker Space needs a paid plan for personal accounts (PRO), checked 11 Oct 2026.
  Everything else in the lab is free.
- **Cost:** about 90 `gpt-4o-mini` calls and a few dozen free moderation calls: a few US cents.

## What is in this folder

| File | What it is |
|---|---|
| `13_deploy_to_a_space.ipynb` | the lab |
| `space/` | the Space template: `README.md` (the header), `app.py`, `requirements.txt`, `.gitignore` |
| `resources/streamlit_app.py` | the same copilot as a Streamlit page, for Part G |
| `resources/lab13_page_flow.mmd`, `.png` | the diagram of one message through the page |

The notebook ends with a troubleshooting table: ports still in use, the page's API name, the Ops API not running, an
app that does not start, the Ops API reused in Part F, the page on Colab, and counts that differ from ours.

## Resources

- [Gradio: `ChatInterface`](https://www.gradio.app/docs/gradio/chatinterface): the function's arguments, `additional_inputs`, examples and streaming
- [Gradio: `Chatbot` and `ChatMessage`](https://www.gradio.app/docs/gradio/chatbot): `metadata` for folded steps and `options` for buttons under a message
- [Gradio: agents and tool usage](https://www.gradio.app/guides/agents-and-tool-usage): showing an agent's tool steps as folded messages
- [Gradio: the Python client](https://www.gradio.app/guides/getting-started-with-the-python-client): `Client`, `predict`, `submit` and authentication
- [Gradio: sharing your app](https://www.gradio.app/guides/sharing-your-app): share links, `auth` and `gr.Request`
- [Hugging Face: Spaces overview](https://huggingface.co/docs/hub/en/spaces-overview): SDKs, plans, secrets and variables, sleeping hardware
- [Hugging Face: Spaces configuration reference](https://huggingface.co/docs/hub/en/spaces-config-reference): every field of the README header
- [Hugging Face: the `hf` command line](https://huggingface.co/docs/huggingface_hub/en/guides/cli): `hf auth login`, `hf repos create`, `hf upload`, `hf spaces secrets`, `hf spaces logs`
- [Streamlit: how your app runs](https://docs.streamlit.io/develop/concepts/architecture/run-your-app): the rerun model, `st.session_state` and caching

Next (optional): [the capstone](../Capstone_Chinook_Copilot/README.md), which joins the whole copilot and evaluates it. Back to [the lab list](../README.md).
