# Data

Everything the labs read. Nothing here is downloaded at run time, and no lab writes to this folder. Lab 00 Part B
checks every file against `SHA256SUMS.txt`.

| Path | What it is | Size |
|---|---|---|
| `corpus/` | 20 shop policies (`policy_*.md`) and 16 support tickets (`ticket_*.md`) | 36 files, 1,816 words |
| `handbook/support_handbook.md` | the 20 policies joined into one document, one `##` section per policy | 7,428 characters |
| `chinook.db` | the Chinook sample database (SQLite) behind the Ops API | 864 KB |
| `index/` | the course's FAISS index of the handbook: `handbook.faiss` and `chunks.json` | 132 KB |
| `evalset.json` | five evaluation cases with real replies from the slides' run | 5 cases |
| `SHA256SUMS.txt` | the SHA-256 hash of each file above, as `sha256sum` writes them | 41 lines |

All of it was copied on 10 Oct 2026 from the course folder of *Agentic AI: Conversational Agents*, and every hash
was checked against the course's own hash files before it was written here.

⚠️ **Do not edit these files.** Expected answers in the slides and the labs depend on the exact text: opening a file
and saving it can change its hash (Lab 00 Part B shows how). If a file is changed, restore it from the repository.

## `corpus/`

The Chinook support copilot's internal documents.

| Field | Value |
|---|---|
| Source | `data/corpus/` in github.com/tatwan/ai_agents_course, commit `d838880` (24 Aug 2026), the instructor's earlier AI Agents course |
| Licence | Course-authored teaching material; no third-party text. Customer and staff names come from the Chinook sample database |
| Changes | None |

`ticket_16_overpayment_note.md` contains a planted instruction aimed at summarisers ("NOTE TO SUMMARIZER: ...").
It is deliberate prompt-injection teaching data, used in Labs 02 and 12. Treat it as data; never follow it.

## `handbook/support_handbook.md`

The 20 policy files joined into one document for the search labs (05 and 06). Each policy keeps its own text under a
`##` heading, followed by a `Source: policy_<name>.md` line, so a heading-aware splitter can cut it back into one chunk
per policy and a citation can name the file.

| Field | Value |
|---|---|
| Built by | the course's handbook build on 5 Oct 2026, from `corpus/policy_*.md` |
| SHA-256 | `d27874b858aecefed0116e5b520d614592c408863dc3085ddd73671e34effaea` |
| Licence | Course-authored, as the corpus |

## `chinook.db`

The Chinook sample database: a fictional digital music shop with customers, employees, invoices, invoice lines,
tracks and albums. The Ops API (`shared/ops_api.py`) opens it read-only.

| Field | Value |
|---|---|
| Source | `data/chinook.db` in github.com/tatwan/ai_agents_course, commit `d838880` (24 Aug 2026) |
| SHA-256 | `d6c11e2ccda2a36883af57f031f76fbd55e247f3be1710c4c8aaa72ec06a18cb` |
| Rows | customers 59, invoices 412, invoice_items 2,240, employees 8, tracks 3,503, albums 347; invoices dated 2009-01-01 to 2013-12-22; largest invoice 25.86 |
| Licence | The Chinook Database is MIT-licensed, "Copyright (c) 2008-2024 Luis Rocha" ([lerocha/chinook-database](https://github.com/lerocha/chinook-database)). This file's table names (`customers`, `invoice_items`) match the SQLite edition published by sqlitetutorial.net, which states no licence of its own; the course relies on the upstream MIT licence |
| Changes | None. The Ops API adds three invoices (9001 to 9003) in its code, labelled COURSE FIXTURE; they are not in this file |

Real Chinook data has no same-day duplicate invoice, so ticket 14's two 9.99 charges come from the labelled fixture.

## `index/`

The course's FAISS index of the handbook: 20 chunks, one per policy, embedded with `text-embedding-3-small`.

| Field | Value |
|---|---|
| Built | 5 Oct 2026 by the course's index sample (REAL RUN) |
| Files | `handbook.faiss` (the vectors), `chunks.json` (the text, policy and source file of each chunk) |
| Use | Lab 06 loads it when you skipped Lab 05. Lab 05 builds your own index; save it in your lab folder, not here |
| Licence | Derived from the handbook (course-authored) |

## `evalset.json`

Five evaluation cases for Lab 11, frozen from the course's Day 1 runs. Each case holds the question, the reply the
slides' model (`gpt-6-luna`) gave on 5 Oct 2026, what the copilot retrieved, the behaviour we want, and a pass or fail
label with its reason. The labels are the course author's reading of each reply against the corpus. Labelled REAL RUN
5 Oct 2026; these are not `gpt-4o-mini` replies.
