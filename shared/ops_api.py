"""Chinook Ops API: the small HTTP service the copilot acts through.

You call this service in the labs; you do not write it. Day 2 of the course (D2-M02 to D2-M04)
teaches its contract:

    GET  /health                     is the service up?
    GET  /customers?name=...         find a customer (minimal fields)
    GET  /customers/{id}/invoices    invoices, count, total, support rep
    GET  /invoices/{id}              one invoice with its lines
    POST /refund-requests            file a REQUEST (Idempotency-Key header)
    GET  /refund-requests/{id}       read a filed request back

Reads come from data/chinook.db, opened read-only. Writes go to a separate ops database (a
temporary file) and only to refund_requests: the API never changes an invoice. A request over
100 dollars is filed as "needs_manager" (policy_escalations.md), so that rule lives in code,
not in a prompt.

Invoices 9001-9003 are a labelled COURSE FIXTURE, not Chinook data: ticket 14's two 9.99
charges and a synthetic 120.00 invoice for the escalation case. Real Chinook invoices never
exceed 25.86.

In a notebook:  from shared.ops_api import start_ops_api; server = start_ops_api()
Stop it with:   server.should_exit = True

Copied from the course's tools/D02/ops_api.py (5 Oct 2026). Changes: data found from this
file's location, no environment variables, start_ops_api() reuses a server that already answers.
"""
from __future__ import annotations

import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]          # the repository folder
CHINOOK = ROOT / "data" / "chinook.db"
OPS_DB = Path(tempfile.gettempdir()) / "chinook_ops.db"
ESCALATE_OVER = 100.00     # policy_escalations.md: "over 100 dollars"

MILES = [{"album": "The Essential Miles Davis [Disc 1]",
          "unit_price": 9.99, "quantity": 1}]
FIXTURE = {   # course fixture, labelled wherever it appears
    9001: {"customer_id": 16, "date": "2013-11-02", "total": 9.99,
           "lines": MILES, "note": "ticket 14, first charge"},
    9002: {"customer_id": 16, "date": "2013-11-02", "total": 9.99,
           "lines": MILES, "note": "ticket 14, second charge"},
    9003: {"customer_id": 16, "date": "2013-11-20", "total": 120.00,
           "lines": [{"album": "Box set (synthetic)",
                      "unit_price": 120.00, "quantity": 1}],
           "note": "synthetic escalation case"},
}

app = FastAPI(title="Chinook Ops API", version="1.0")


def chinook():
    """Read-only: the copilot can never change Chinook's records."""
    return sqlite3.connect(f"file:{CHINOOK}?mode=ro", uri=True,
                           check_same_thread=False)


def ops():
    con = sqlite3.connect(OPS_DB, check_same_thread=False)
    con.execute("""CREATE TABLE IF NOT EXISTS refund_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        idempotency_key TEXT UNIQUE, invoice_id INTEGER, amount REAL,
        reason TEXT, rep_id TEXT, status TEXT, created_at TEXT)""")
    return con


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers")
def find_customers(name: str):
    rows = chinook().execute(
        """SELECT c.CustomerId, c.FirstName || ' ' || c.LastName,
                  c.Country, e.FirstName || ' ' || e.LastName
           FROM customers c
           JOIN employees e ON e.EmployeeId = c.SupportRepId
           WHERE c.FirstName || ' ' || c.LastName LIKE ?""",
        (f"%{name}%",)).fetchall()
    return [{"customer_id": r[0], "name": r[1], "country": r[2],
             "support_rep": r[3]} for r in rows]


@app.get("/customers/{customer_id}/invoices")
def customer_invoices(customer_id: int):
    db = chinook()
    rep = db.execute(
        """SELECT e.FirstName || ' ' || e.LastName FROM customers c
           JOIN employees e ON e.EmployeeId = c.SupportRepId
           WHERE c.CustomerId = ?""", (customer_id,)).fetchone()
    if rep is None:
        raise HTTPException(404, f"No customer {customer_id}")
    rows = db.execute(
        """SELECT InvoiceId, substr(InvoiceDate, 1, 10), Total
           FROM invoices WHERE CustomerId = ?
           ORDER BY InvoiceDate""", (customer_id,)).fetchall()
    return {"customer_id": customer_id, "support_rep": rep[0],
            "count": len(rows),
            "total": round(sum(r[2] for r in rows), 2),
            "invoices": [{"invoice_id": r[0], "date": r[1],
                          "total": r[2]} for r in rows]}


@app.get("/invoices/{invoice_id}")
def invoice(invoice_id: int):
    if invoice_id in FIXTURE:
        return {"invoice_id": invoice_id, **FIXTURE[invoice_id],
                "source": "course fixture"}
    db = chinook()
    head = db.execute(
        """SELECT CustomerId, substr(InvoiceDate, 1, 10), Total
           FROM invoices WHERE InvoiceId = ?""",
        (invoice_id,)).fetchone()
    if head is None:
        raise HTTPException(404, f"No invoice {invoice_id}")
    lines = db.execute(
        """SELECT t.Name, a.Title, ii.UnitPrice, ii.Quantity
           FROM invoice_items ii
           JOIN tracks t ON t.TrackId = ii.TrackId
           JOIN albums a ON a.AlbumId = t.AlbumId
           WHERE ii.InvoiceId = ?""", (invoice_id,)).fetchall()
    return {"invoice_id": invoice_id, "customer_id": head[0],
            "date": head[1], "total": head[2],
            "lines": [{"track": l[0], "album": l[1],
                       "unit_price": l[2], "quantity": l[3]}
                      for l in lines],
            "source": "chinook.db"}


class RefundIn(BaseModel):
    invoice_id: int
    amount: float = Field(gt=0)
    reason: str
    rep_id: str


@app.post("/refund-requests", status_code=201)
def file_refund(body: RefundIn, response: Response,
                idempotency_key: str = Header()):
    db = ops()
    seen = db.execute(
        "SELECT * FROM refund_requests WHERE idempotency_key = ?",
        (idempotency_key,)).fetchone()
    if seen:                 # same key: return it, file nothing new
        response.status_code = 200
        return {**_row(seen), "replayed": True}
    total = invoice(body.invoice_id)["total"]   # 404 if unknown
    if body.amount > total:
        raise HTTPException(
            422, f"Amount {body.amount} exceeds invoice total {total}")
    status = ("needs_manager" if body.amount > ESCALATE_OVER
              else "pending_review")
    cur = db.execute(
        """INSERT INTO refund_requests (idempotency_key, invoice_id,
           amount, reason, rep_id, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (idempotency_key, body.invoice_id, body.amount, body.reason,
         body.rep_id, status,
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    db.commit()
    row = db.execute(
        "SELECT * FROM refund_requests WHERE request_id = ?",
        (cur.lastrowid,)).fetchone()
    return {**_row(row), "replayed": False}


@app.get("/refund-requests/{request_id}")
def get_refund(request_id: int):
    row = ops().execute(
        "SELECT * FROM refund_requests WHERE request_id = ?",
        (request_id,)).fetchone()
    if row is None:
        raise HTTPException(404, f"No refund request {request_id}")
    return _row(row)


def _row(r):
    keys = ["request_id", "idempotency_key", "invoice_id", "amount",
            "reason", "rep_id", "status", "created_at"]
    return dict(zip(keys, r))


def serve(port: int = 8765, fresh: bool = True):
    """Run the API in a background thread. fresh=True starts with no refund requests."""
    import uvicorn
    if fresh and OPS_DB.exists():
        OPS_DB.unlink()
    server = uvicorn.Server(uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        if not thread.is_alive():      # e.g. the port is already in use
            raise RuntimeError(f"Ops API did not start on port {port}")
        time.sleep(0.05)
    return server


def start_ops_api(port: int = 8765):
    """Start the API once per session and return its server.

    If a server already answers /health on this port (a cell run twice, or another notebook),
    reuse it and return None, so a second start never fails on a busy port.
    """
    url = f"http://127.0.0.1:{port}"
    try:
        if httpx.get(f"{url}/health", timeout=1.0).status_code == 200:
            print(f"Ops API already running at {url}: reusing it")
            return None
    except httpx.HTTPError:
        pass                                   # nothing answers yet: start one
    server = serve(port)
    print(f"Ops API started at {url}")
    return server
