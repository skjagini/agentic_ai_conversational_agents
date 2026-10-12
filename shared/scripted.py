"""A scripted chat model: it returns AIMessages written in advance and makes no API call.

It stands in for the model only to show framework mechanics that do not depend on what a real
model would say: how a malformed argument comes back, how an approval interrupt pauses the run,
what a resume executes. Outputs that use it are labelled "SCRIPTED MODEL · NO API CALL". Real model
behaviour comes from cells that call CHAT_MODEL.

Copied from the course's tools/D02/samples/_scripted.py (5 Oct 2026), unchanged apart from this text.
"""
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage


class ScriptedModel(GenericFakeChatModel):
    sent: list = []

    def bind_tools(self, tools, **kwargs):          # create_agent binds tools; the script ignores them
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.sent.append([m.type for m in messages])
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def call(name, args, i=1):
    """An AIMessage that asks for one tool call."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call_{name}_{i}"}])


def scripted(*replies):
    """A model that answers with these messages, in order, one per call."""
    return ScriptedModel(messages=iter(list(replies)), sent=[])
