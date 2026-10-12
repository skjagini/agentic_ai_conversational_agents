"""The copilot's handbook search, for labs that use it after it was taught.

Lab 08 builds the vector store, `search()` and `search_policies` cell by cell. Later labs (09 to 13, the capstone)
import them from here instead of copying them. Read Lab 08's notebook to learn them; this file only collects the
finished pieces.

Adapted from the course's tools/D01/copilot.py (5 Oct 2026): the retrieval functions and the `search_policies`
tool, plus `load_prompt`. Changes: no settings read from the environment at import time; the data folder is found
from this file's location; the embedding client comes from shared.settings.embeddings(), which reads EMBED_MODEL
from models.env; no model client here (use shared.settings.chat_model()); `search_policies` returns its hits as the
tool message's artifact, so code can read the retrieved files and scores without parsing text.

Since 12 Oct 2026 (revision C08, decision D10) the search runs on LangChain's InMemoryVectorStore, built from the 20
policy files in data/corpus/ (the files the handbook is made from) the first time it is needed, so no lab reads the
prebuilt FAISS index in data/index/ any more. The store is built on first use, not at import, so importing this
module (for `load_prompt`, say) needs no key and makes no call. `build_index` (FAISS) stays only for
shared/guards.py's ticket search and Lab 12 until that lab moves to `build_store` and the `rep` filter.
"""
from __future__ import annotations

from pathlib import Path

from langchain.tools import tool
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

ROOT = Path(__file__).resolve().parents[1]           # the repository folder
DATA = ROOT / "data"
CORPUS = DATA / "corpus"
HANDBOOK = DATA / "handbook" / "support_handbook.md"
PROMPTS = ROOT / "shared" / "prompts"


def load_prompt(name: str = "copilot_system_v2.md") -> str:
    """A prompt file's text without its version header comment."""
    text = (PROMPTS / name).read_text(encoding="utf-8")
    return text.split("-->", 1)[-1].strip()


# ------------------------------------------------------------------ the vector store (Lab 08)
def load_documents(files) -> list[Document]:
    """One document per file, with its file name (`source`) and first heading (`section`) as metadata."""
    documents = []
    for path in sorted(files):
        text = Path(path).read_text(encoding="utf-8").strip()
        section = text.splitlines()[0].lstrip("#").strip()
        documents.append(Document(page_content=text, metadata={"source": Path(path).name, "section": section}))
    return documents


def build_store(documents: list[Document], emb=None) -> InMemoryVectorStore:
    """Embed every document once into an InMemoryVectorStore (EMBED_MODEL unless you pass a client)."""
    if emb is None:
        from shared.settings import embeddings
        emb = embeddings()
    store = InMemoryVectorStore(emb)
    store.add_documents(documents)
    return store


_STORES: dict = {}


def handbook_store() -> InMemoryVectorStore:
    """The 20 policies in a vector store, built on the first call and kept for the session."""
    if "handbook" not in _STORES:
        _STORES["handbook"] = build_store(load_documents(CORPUS.glob("policy_*.md")))
    return _STORES["handbook"]


def search(query: str, k: int = 4, store: InMemoryVectorStore | None = None,
           rep_name: str | None = None) -> list[tuple[Document, float]]:
    """The k documents closest to a query, best first, as (document, cosine score) pairs.

    With `rep_name`, only documents whose metadata has no `rep`, or that rep, can come back. The filter runs
    inside the search, so a hidden document never reaches the model. The policies carry no `rep` (every rep
    reads them); a store of tickets would set it.
    """
    store = store or handbook_store()
    keep = None
    if rep_name is not None:
        def keep(document: Document) -> bool:
            return document.metadata.get("rep") in (None, rep_name)
    return store.similarity_search_with_score(query, k=k, filter=keep)


# ------------------------------------------------------------------ the retriever tool (Lab 08)
@tool(parse_docstring=True, response_format="content_and_artifact")
def search_policies(query: str) -> tuple[str, list[dict]]:
    """Search the support handbook for the four passages closest to a query.

    Call it before answering any question about shop rules.
    Each passage starts with its source file in square brackets.

    Args:
        query: What the rep needs to know, in a short sentence.
    """
    hits = search(query)
    text = "\n\n".join(f"[{doc.metadata['source']}]\n{doc.page_content}" for doc, score in hits)
    found = [{"source": doc.metadata["source"], "score": round(score, 4)} for doc, score in hits]
    return text, found


# ------------------------------------------------------------------ FAISS, kept for shared/guards.py (Lab 12)
def build_index(chunks: list[dict], emb):
    """Embed every chunk once and add the unit vectors to an exact inner-product index (scores are cosines).

    Lab 07 teaches this; only shared/guards.py's ticket search and Lab 12 still use it.
    """
    import faiss
    import numpy as np
    vectors = np.array(emb.embed_documents([c["text"] for c in chunks]), dtype="float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index
