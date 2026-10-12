"""Model names, prices and keys for every lab.

Model settings come from models.env in the repository folder (committed, no secrets). A value in
.env (local, gitignored) overrides it, and an environment variable overrides both. Keys never live
in models.env: load_key() looks in the environment, then .env, then Colab Secrets.

Nothing is read when this module is imported. Call load_settings() and load_key() in a lab's
config cell, then chat_model(), judge_model(), fallback_model() or embeddings() wherever the lab needs a client.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]          # the repository folder
DATA = ROOT / "data"


def load_settings(root: Path = ROOT) -> dict:
    """models.env, then .env, then environment variables; later sources win."""
    settings = dict(dotenv_values(root / "models.env"))
    local = dotenv_values(root / ".env")
    for name in settings:
        if local.get(name):
            settings[name] = local[name]
        if os.environ.get(name):
            settings[name] = os.environ[name]
    return settings


def load_key(name: str = "OPENAI_API_KEY", root: Path = ROOT) -> str | None:
    """Put a key into os.environ for the client libraries.

    Returns where the key was found ("environment", ".env" or "Colab Secrets"), or None.
    Never returns or prints the key itself.
    """
    if os.environ.get(name):
        return "environment"
    value = dotenv_values(root / ".env").get(name)
    if value:
        os.environ[name] = value
        return ".env"
    try:
        from google.colab import userdata
    except ImportError:                              # not on Colab
        return None
    try:
        value = userdata.get(name)
    except (userdata.SecretNotFoundError, userdata.NotebookAccessError):
        return None
    if value:
        os.environ[name] = value
        return "Colab Secrets"
    return None


def chat_model(settings: dict | None = None, **kwargs):
    """The copilot's chat model: CHAT_MODEL through the Responses API.

    Reasoning effort is passed only when REASONING_EFFORT is set, because models without it
    (gpt-4o-mini) reject the parameter.
    """
    from langchain_openai import ChatOpenAI
    settings = settings or load_settings()
    if settings.get("REASONING_EFFORT"):
        kwargs.setdefault("reasoning_effort", settings["REASONING_EFFORT"])
    return ChatOpenAI(model=settings["CHAT_MODEL"], use_responses_api=True, **kwargs)


def judge_model(settings: dict | None = None, **kwargs):
    """The evaluation judge (Lab 10): JUDGE_MODEL through the Responses API."""
    from langchain_openai import ChatOpenAI
    settings = settings or load_settings()
    return ChatOpenAI(model=settings["JUDGE_MODEL"], use_responses_api=True, **kwargs)


def fallback_model(settings: dict | None = None, **kwargs):
    """The model the copilot falls back to when CHAT_MODEL fails (Lab 12): FALLBACK_MODEL through the Responses API."""
    from langchain_openai import ChatOpenAI
    settings = settings or load_settings()
    return ChatOpenAI(model=settings["FALLBACK_MODEL"], use_responses_api=True, **kwargs)


def embeddings(settings: dict | None = None, **kwargs):
    """The embedding model for the handbook search (Lab 07, and Lab 08 on): EMBED_MODEL."""
    from langchain_openai import OpenAIEmbeddings
    settings = settings or load_settings()
    return OpenAIEmbeddings(model=settings["EMBED_MODEL"], **kwargs)
