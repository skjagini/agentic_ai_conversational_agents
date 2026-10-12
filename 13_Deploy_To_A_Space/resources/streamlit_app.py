"""The same copilot as a Streamlit page, for comparison with app.py (Lab 13, Part G).

Copy this file into the assembled Space folder, next to app.py, and run it there:
    uv run --with streamlit==1.65.0 streamlit run streamlit_app.py

Streamlit reruns this whole script on every click or message. What must survive a rerun for one visitor lives in
st.session_state; what is built once for everybody lives in an @st.cache_resource function.
"""
import uuid

import streamlit as st
from langgraph.types import Command

import app        # the Gradio app's module: the same copilot, checks and decisions

st.title("Chinook support copilot")
if not app.load_key("OPENAI_API_KEY", app.ROOT):
    st.error(app.NO_KEY)
    st.stop()


@st.cache_resource            # once per server process, not on every rerun
def setup():
    app.start_ops_api()
    return app.build_copilot()


copilot = setup()
REP = app.RepContext(rep_id="rep-42", rep_name="Jane Peacock")
if "thread_id" not in st.session_state:          # the first run for this visitor
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.shown = []
cfg = {"configurable": {"thread_id": st.session_state.thread_id}}

for role, text in st.session_state.shown:        # draw the conversation again on every rerun
    st.chat_message(role).write(text)


def run(turn):
    # One turn of the copilot; the reply is shown only after the check, as in app.py.
    with st.spinner("The copilot is working"):
        copilot.invoke(turn, cfg, context=REP)
    state = copilot.get_state(cfg)
    if not state.interrupts:
        reply, failed = app.checked(state.values["messages"][-1].text)
        st.session_state.shown.append(("assistant", reply))


waiting = copilot.get_state(cfg).interrupts
if waiting:
    asks = [ask for interrupt in waiting for ask in interrupt.value["action_requests"]]
    st.warning("Waiting for your approval: " + "; ".join(f"{a['name']} {a['args']}" for a in asks)
               + ". Approve, or type why not.")
    if st.button("Approve"):
        run(Command(resume={"decisions": [app.decision("approve")] * len(asks)}))
        st.rerun()

if message := st.chat_input("Ask about a policy, a customer or a refund"):
    st.session_state.shown.append(("user", message))
    if waiting:                                  # typed, not clicked: a rejection with a reason
        run(Command(resume={"decisions": [app.decision(message)] * len(asks)}))
    else:
        run({"messages": [("user", message)]})
    st.rerun()                                   # draw again: a new approval needs its button
