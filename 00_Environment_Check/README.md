# Lab 00: How to set up the lab environment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/00_Environment_Check/00_environment_check.ipynb)

**CPU | API key: `OPENAI_API_KEY` for Part D**

## Goal

Get a working environment for every lab in this repository, on Colab or on your own machine, and prove it in one run.
This README is the setup guide; the notebook is the check at the end. When its last cell shows ✅ on every line, you
are ready for Lab 01.

Do this before the first class if you can. A local install can take 10 to 20 minutes the first time, most of it
downloading packages.

## What you will learn

- How to set up the labs on Colab, or on your own machine with `uv` or with `pip`.
- Where your OpenAI key goes, and how the labs find it without printing it.
- How to open a lab notebook on the right kernel in JupyterLab or VS Code.
- How to check in one run that your packages, the data files, the shop's Ops API and your key all work.
- How to find what a failed check means and fix it.

## Choose a route

| Route | Use it when | You need |
|---|---|---|
| **A. Colab** | you cannot install software, or you want to start in five minutes | a Google account and an OpenAI key |
| **B. Local with `uv`** (recommended for local) | you can install a command-line tool | a terminal, Git (or a ZIP download) and an OpenAI key |
| **C. Local with `pip`** | your laptop does not allow `uv`, or you already use Python 3.13 | Python 3.13, a terminal, Git (or a ZIP) and an OpenAI key |

Routes B and C install the same pinned package versions. The saved outputs in every lab come from these versions, so a
run on your machine should match ours.

---

## Route A: Colab

1. Open the notebook with the **Open in Colab** badge above. Each lab's README has the same badge.
2. Add your key: click the key icon (**Secrets**) in Colab's left bar, add a secret named `OPENAI_API_KEY` with your key
   as its value, and switch on **Notebook access**.
3. Run the notebook from the top (**Runtime → Run all**). Its first cell copies this repository into the Colab session
   and installs the packages, which takes a minute or two.

Each Colab session starts empty: every lab's first cell copies the repository and installs the packages again. Your
key stays in Secrets.

---

## Route B: Local with `uv`

[`uv`](https://docs.astral.sh/uv/) installs the right Python (3.13) and the pinned packages into a folder called
`.venv` inside the repository, so nothing else on your machine changes.

**1. Install `uv`** (once per machine). macOS or Linux, in a terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows, in PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close the terminal and open a new one, then check that `uv --version` prints a version.

**2. Get the repository.** With Git:

```bash
git clone https://github.com/tatwan/agentic_ai_conversational_agents.git
cd agentic_ai_conversational_agents
```

Without Git, download the
[ZIP](https://github.com/tatwan/agentic_ai_conversational_agents/archive/refs/heads/main.zip), unzip it and open a
terminal in the unzipped folder (it is called `agentic_ai_conversational_agents-main`). Git makes later updates
easier: `git pull` fetches them.

**3. Install Python and the packages:**

```bash
uv sync
```

This reads `.python-version` and `uv.lock`, downloads Python 3.13 if you do not have it, and installs every pinned
package plus JupyterLab into `.venv`. Run it again whenever the repository's `uv.lock` changes.

**4. Add your key.** Copy the example file, then open `.env` in any text editor and paste your key after
`OPENAI_API_KEY=` (no quotes, no spaces):

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

`.env` stays on your machine: `.gitignore` keeps it out of Git. Never paste a key into a notebook cell.

**5. Open the notebook.** Either start JupyterLab from the repository folder:

```bash
uv run jupyter lab
```

and open `00_Environment_Check/00_environment_check.ipynb`, or open the repository folder in VS Code (with its Python
and Jupyter extensions), open the notebook, click the kernel picker at the top right (**Select Kernel**) and choose the
`.venv` environment.

**6. Run the notebook** from the top, then read the last cell.

---

## Route C: Local with `pip`

Use this route when you cannot install `uv`. You manage the Python version yourself.

**1. Install Python 3.13** from [python.org](https://www.python.org/downloads/) if you do not have it. Check with
`python3.13 --version` (macOS or Linux) or `py -3.13 --version` (Windows).

**2. Get the repository**, as in route B, step 2.

**3. Create a virtual environment and install the packages.** A virtual environment is a folder that holds this
repository's packages apart from any other Python project. From the repository folder, macOS or Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt jupyterlab==4.6.4 ipykernel==7.4.0
```

Windows (PowerShell):

```powershell
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt jupyterlab==4.6.4 ipykernel==7.4.0
```

`requirements.txt` holds the same pins as `uv.lock` for the packages the labs import; JupyterLab and the kernel package
are named on the command line because Colab must not install them. Your prompt shows `(.venv)` while the environment
is active. Activate it again in every new terminal.

**4. Add your key**, as in route B, step 4.

**5. Open the notebook:** with the environment active, run `jupyter lab` from the repository folder, or use VS Code as
in route B and choose the `.venv` kernel.

**6. Run the notebook** from the top, then read the last cell.

---

## What the notebook checks

**Setup and config.** The two cells every lab opens with: on Colab they copy the repository and install the packages;
then they read the model names from `models.env` and find your key without printing it.
**Part A: Check the packages.** Python 3.13 and each installed package against its pin in `requirements.txt`.
**Part B: Check the data files.** Every file in `data/` against its hash in `data/SHA256SUMS.txt`.
**Part C: Check the Ops API.** Starts the shop's small web service in the notebook, asks `/health` and stops it.
**Part D: Check that the model answers.** One short question to the chat model with your key.
**Check that you are ready.** One ✅ or ❌ per part.

## Checkpoints

| After | You should see |
|---|---|
| Config | `OPENAI_API_KEY` found in `.env`, the environment or Colab Secrets |
| Part A | Python 3.13.x; 20 pinned packages, 0 different |
| Part B | 41 of 41 files match; changed: none |
| Part C | `200 {'status': 'ok'}` |
| Part D | a reply in any wording, and the model that answered (ours: `gpt-4o-mini-2024-07-18`) |
| The last cell | ✅ on all four lines |

Part D's wording changes from run to run, and from model to model.

## The model every lab uses

No notebook names a model in its code. `models.env`, in the repository folder, sets the model for every lab
(`CHAT_MODEL=gpt-4o-mini` by default). To switch every lab to another model, change that line. To try another model
on your machine only, put a `CHAT_MODEL=...` line in your `.env`: it wins over `models.env`. Another model words its
replies differently, so in each lab check the facts a checkpoint names, not the wording.

## Troubleshooting the setup

The notebook ends with a table for failed checks. These are the problems that come before it:

| Symptom | Likely cause | Fix |
|---|---|---|
| `uv: command not found` (or "not recognized" on Windows) | the terminal was open before `uv` was installed | open a new terminal; if it still fails, rerun the install command and read its last lines for the folder to add to your PATH |
| The `uv` or Python installer is blocked | a managed laptop that does not allow installs | use route C if Python 3.13 is already installed, otherwise route A (Colab) |
| `uv sync` or `pip install` stops with a network or certificate error | a company proxy or firewall | try another network, or ask IT for the proxy settings; route A works from a browser |
| `pip` reports that no version matches a pin | the environment runs a Python other than 3.13 | delete `.venv`, create it again with Python 3.13 (route C, step 3) |
| Windows refuses to run `.venv\Scripts\activate` | PowerShell's script policy | run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt and `.venv\Scripts\activate.bat` |
| The notebook's Part A shows another Python, or packages `missing` | the notebook runs on another kernel | choose the `.venv` kernel (VS Code: the kernel picker; JupyterLab: start it with `uv run jupyter lab` or from the active environment) |
| The config cell says the key is `not found` | `.env` is missing, misnamed (`.env.txt`) or outside the repository folder | `.env` sits next to `models.env`; on Windows, turn on file name extensions to see the real name |

## Resources

- [uv: installation](https://docs.astral.sh/uv/getting-started/installation/) and
  [working on projects](https://docs.astral.sh/uv/guides/projects/): `uv sync`, `.python-version` and the lock file
- [Python: virtual environments](https://docs.python.org/3/library/venv.html): `python -m venv` and activation on each
  system
- [VS Code: Jupyter notebooks](https://code.visualstudio.com/docs/datascience/jupyter-notebooks): opening a notebook
  and choosing a kernel
- [OpenAI: API keys](https://platform.openai.com/api-keys): where to create a key

Next: [Lab 01: How to build a tool-calling agent](../01_First_Chain_And_Tool/README.md). Back to [the lab list](../README.md).
