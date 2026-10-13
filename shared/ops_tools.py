"""The copilot's Day 2 tools: model-facing contracts backed by the Chinook Ops API over HTTP.

Lab 05 writes the read tools cell by cell; Lab 09 writes the write tool, the approval step and the idempotency key.
Later labs import them from here. Read a lab's notebook to learn them; this file only collects the
finished pieces. (Lab numbers follow the revision plan; the folders are renamed in session D.)

Each tool is a name, a description and typed arguments the model sees; the body is ordinary code that calls the API
with a timeout and turns HTTP errors into text the model can read. The rep's identity comes from the run's context
(`RepContext`), which the model never sees.

Copied from the course's tools/D02/ops_tools.py (5 Oct 2026). Changes: `search_policies` and `load_prompt` come from
shared/copilot.py (the content_and_artifact version from Lab 08); no model client here (use
shared.settings.chat_model()); the API address is a constant, not read from the environment; prompts are read from
shared/prompts/; `search_tickets` (it needs Lab 12's guards) and the course's dry-run block are left out.
`file_refund_request` keeps the course's idempotency key (thread, invoice, amount), the key Lab 09 builds: a retry
in the same conversation files nothing new; a second conversation about the same refund files again.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

import httpx
from langchain.tools import ToolRuntime, tool

from shared.copilot import load_prompt, search_policies

API = "http://127.0.0.1:8765"          # shared.ops_api.start_ops_api() serves here
TIMEOUT = httpx.Timeout(5.0)            # seconds: a slow API must not hang a turn
Reason = Literal["duplicate_charge", "damaged_media", "other"]


@dataclass
class RepContext:
    rep_id: str        # set by your app from the sign-in, never by the model
    rep_name: str


def _get(path: str, **params) -> str:
    try:
        r = httpx.get(API + path, params=params, timeout=TIMEOUT)
    except (httpx.TimeoutException, httpx.ConnectError):
        return "The Ops API did not answer. Try again in a moment."
    if r.status_code == 404:
        return "Not found: " + r.json()["detail"]
    r.raise_for_status()
    return json.dumps(r.json(), ensure_ascii=False)


@tool(parse_docstring=True)
def find_customer(name: str) -> str:
    """Find customers by name: id, name, country and rep.

    Args:
        name: Full or partial name, e.g. "Helena Holý".
    """
    return _get("/customers", name=name)


@tool(parse_docstring=True)
def get_customer_invoices(customer_id: int) -> str:
    """List one customer's invoices, with count, total and rep.

    Args:
        customer_id: The customer_id that find_customer returned.
    """
    return _get(f"/customers/{customer_id}/invoices")


@tool(parse_docstring=True)
def get_invoice(invoice_id: int) -> str:
    """Return one invoice: date, total, customer and albums.

    Args:
        invoice_id: The invoice number, digits only.
    """
    return _get(f"/invoices/{invoice_id}")


@tool(parse_docstring=True)
def file_refund_request(invoice_id: int, amount: float,
                        reason: Reason,
                        runtime: ToolRuntime[RepContext]) -> str:
    """File a refund request. A person reviews it first.

    Use it only after the policy and the invoice show a refund
    is due.

    Args:
        invoice_id: The invoice to refund, digits only.
        amount: US dollars, at most the invoice total.
        reason: Why the refund is due.
    """
    conf = runtime.config.get("configurable", {})
    key = f"{conf.get('thread_id')}:{invoice_id}:{amount:.2f}"
    body = {"invoice_id": invoice_id, "amount": amount,
            "reason": reason, "rep_id": runtime.context.rep_id}
    try:
        r = httpx.post(API + "/refund-requests", json=body,
                       headers={"Idempotency-Key": key},
                       timeout=TIMEOUT)
    except (httpx.TimeoutException, httpx.ConnectError):
        return ("Outcome unknown: the Ops API did not answer. "
                "A retry with the same arguments cannot file twice.")
    if r.status_code in (404, 422):
        return "Not filed: " + json.dumps(r.json()["detail"])
    r.raise_for_status()
    return json.dumps(r.json(), ensure_ascii=False)


READ_TOOLS = [search_policies, find_customer,
              get_customer_invoices, get_invoice]
WRITE_TOOLS = [file_refund_request]


def copilot_prompt() -> str:
    """Prompt v2 from Day 1, unchanged, then the Day 2 actions section."""
    return load_prompt("copilot_system_v2.md") + "\n\n" + load_prompt("copilot_actions_v1.md")
