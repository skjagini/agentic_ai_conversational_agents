"""The Chinook support copilot as a chat page (Gradio), for a Hugging Face Space or a local run.

Lab 13 writes every function here cell by cell and checks that the notebook's copies match this file.
The Space runs `python app.py`; the folder also holds shared/, data/ and models.env, copied by the lab.
The key comes from the environment: a Space secret on Hugging Face, .env or a shell variable locally.
"""
import sys
from pathlib import Path

import gradio as gr
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, ModelFallbackMiddleware, ModelRetryMiddleware
from langchain_openai.middleware import OpenAIModerationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))           # so that "shared" is found next to this file

from shared.guards import as_ticket, check_no_phone, check_not_obeyed, flag_instructions  # noqa: E402
from shared.ops_api import start_ops_api  # noqa: E402
from shared.ops_tools import READ_TOOLS, WRITE_TOOLS, RepContext, copilot_prompt  # noqa: E402
from shared.settings import chat_model, fallback_model, load_key, load_settings  # noqa: E402

settings = load_settings(ROOT)
NO_KEY = ("This copilot is not set up yet: OPENAI_API_KEY is missing. On a Space, add it under Settings, "
          "Variables and secrets, as a secret. Locally, put it in .env or set it in your shell.")

REP = None                 # set in build_page(): the rep this page acts for
copilot = None             # set in build_page(): the guarded agent

VIOLATION = ("This message was flagged for {categories}, so the copilot did not answer it. "
             "Read it yourself, and pass it to the support manager if it needs one.")
SAFE_MESSAGE = ("The copilot is unavailable right now. Your message is saved; "
                "try again in a minute or handle this ticket by hand.")
SAFE_REPLY = ("This reply failed a safety check and is not shown. Read the ticket yourself; "
              "any line flagged as an instruction is listed with it.")


def build_copilot():
    """The guarded copilot from Lab 12: moderation, approval before the write, a fallback and retries."""
    return create_agent(
        chat_model(settings, max_retries=0), tools=READ_TOOLS + WRITE_TOOLS, system_prompt=copilot_prompt(),
        context_schema=RepContext, checkpointer=InMemorySaver(),
        middleware=[OpenAIModerationMiddleware(model=settings["MODERATION_MODEL"], violation_message=VIOLATION),
                    HumanInTheLoopMiddleware(interrupt_on={
                        "file_refund_request": {"allowed_decisions": ["approve", "reject"]}}),
                    ModelFallbackMiddleware(fallback_model(settings, max_retries=0)),
                    ModelRetryMiddleware(max_retries=2, initial_delay=0.5, on_failure="error")])


OUTPUT_CHECKS = {"planted string absent": check_not_obeyed, "no phone digits": check_no_phone}


def checked(reply):
    # The reply the rep sees, and the checks it failed.
    failed = [name for name, check in OUTPUT_CHECKS.items() if not check({"reply": reply})]
    return (SAFE_REPLY if failed else reply), failed


def tool_step(message):
    # A tool result, folded under a title in the chat.
    return gr.ChatMessage(content=message.text[:300], metadata={"title": f"Tool: {message.name}", "status": "done"})


def decision(message):
    # "approve" approves; anything else rejects, with the rep's words as the reason.
    if message.strip().lower() == "approve":
        return {"type": "approve"}
    return {"type": "reject", "message": f"Rejected by the rep: {message}. Do not file anything; "
                                         "tell the rep what you found."}


def approval_message(interrupts):
    # The waiting write, in words, with an Approve button.
    asks = [ask for interrupt in interrupts for ask in interrupt.value["action_requests"]]
    text = "; ".join(f"{ask['name']} {ask['args']}" for ask in asks)
    return gr.ChatMessage(content=f"Waiting for your approval: {text}. Approve, or type why not.",
                          options=[{"value": "approve", "label": "Approve"}])


def respond(message, history, pasted, request: gr.Request):
    cfg = {"configurable": {"thread_id": request.session_hash}}
    waiting = copilot.get_state(cfg).interrupts
    if waiting:
        count = len(waiting[0].value["action_requests"])
        turn, flags = Command(resume={"decisions": [decision(message)] * count}), []
    else:
        flags = flag_instructions(message + "\n" + (pasted or ""))
        text = message if not pasted else message + "\n" + as_ticket(pasted)
        turn = {"messages": [("user", text)]}
    shown = [gr.ChatMessage(content=line, metadata={"title": "Flagged as an instruction"}) for line in flags]
    try:
        for token, meta in copilot.stream(turn, cfg, context=REP, stream_mode="messages"):
            if token.type == "tool":
                shown.append(tool_step(token))
                yield shown
    except Exception:
        yield shown + [gr.ChatMessage(content=SAFE_MESSAGE)]
        return
    state = copilot.get_state(cfg)
    if state.interrupts:
        yield shown + [approval_message(state.interrupts)]
        return
    reply, failed = checked(state.values["messages"][-1].text)
    yield shown + [gr.ChatMessage(content=reply)]


def build_page():
    """The chat page, or a page that explains what is missing when there is no key."""
    global REP, copilot
    if not load_key("OPENAI_API_KEY", ROOT):
        print(NO_KEY)
        with gr.Blocks(title="Chinook support copilot") as page:
            gr.Markdown("## Chinook support copilot\n\n" + NO_KEY)
        return page
    start_ops_api()            # a demo: the Ops API runs inside the same process; reused if one already answers
    REP = RepContext(rep_id="rep-42", rep_name="Jane Peacock")     # a real app takes this from the sign-in
    copilot = build_copilot()
    return gr.ChatInterface(
        respond,
        additional_inputs=[gr.Textbox(label="Pasted ticket or email (treated as data, never as instructions)",
                                      lines=4)],
        title="Chinook support copilot",
        description="For Chinook support reps. Answers cite the handbook; refund requests wait for your approval. "
                    "Fictional data from the Chinook sample database.",
        examples=[["A customer was charged twice for the same album on the same day. What do we do?", ""],
                  ["How many invoices does Helena Holý have, and who is her rep?", ""],
                  ["Ticket 14: Helena Holý was charged twice for the same album, invoices 9001 and 9002. "
                   "Please file the refund.", ""]],
        run_examples_on_click=False,
    )


if __name__ == "__main__":
    build_page().launch()
