# AWS Mistake Tracker

A Streamlit-based tool for recording and reviewing practice-exam mistakes
while studying for AWS certifications (e.g. CLF-C02, SAA-C03).

---

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## Data location

Mistakes are stored in a SQLite database. The default path is
`mistakes.db` in the current working directory.  
You can change the path in the **Database path** field in the sidebar.

---

## Input format examples

Paste any of the following formats into the **Paste question block** area:

### Single correct answer
```
Which AWS service lets you run code without provisioning servers?
A. Amazon EC2
B. AWS Lambda
C. Amazon ECS
D. AWS Batch
Correct answer: B
Your answer: A
```

### Multi-answer – comma separated
```
Which TWO services are compute services? (Choose 2)
A. Amazon S3
B. AWS Lambda
C. Amazon RDS
D. Amazon EC2
E. AWS IAM
Correct answers: B, D
Your answers: B, C
```

### Multi-answer – no separator
```
Which services are serverless? (Choose 2)
A. Amazon EC2
B. AWS Lambda
C. AWS Fargate
D. Amazon RDS
Correct answers: BC
Your answers: AB
```

### Multi-answer – space separated
```
Select the TWO correct answers.
A. Answer one
B. Answer two
C. Answer three
Correct answers: A C
Your answers: A B
```

**Notes:**
- `Correct answer` / `Correct answers` both work (case-insensitive).  
- `Your answer` / `Your answers` are **optional** – omit them if you just want to record the question.  
- Options `A` through `F` are supported.

---

## Search tips

| Goal | How |
|---|---|
| Filter by exam | Type `CLF-C02` (or any exam code) in the **Exam** field |
| Filter by domain | Use the **Domain** dropdown |
| Find by keyword | Enter a word from the question, topic, or reason |
| Filter by tag | Type a partial tag name |
| Show only wrong answers | Enable **Only incorrect** toggle |
| Show only right answers | Enable **Only correct** toggle |
| Drill into a question | Click the expandable row, then **Load full detail** |

---

## Windows EXE

[![Build Windows EXE](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml/badge.svg?branch=main)](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml)

The EXE is built automatically on every push to `main` (and can also be
triggered manually via **Actions → Build Windows EXE → Run workflow**).

**To download:**
1. Go to [Actions → Build Windows EXE](../../actions/workflows/build-windows.yml).
2. Click the latest successful run (green ✓).
3. Scroll to the **Artifacts** section at the bottom.
4. Click **aws-mistake-tool-windows** to download the ZIP, then unzip to get `aws-mistake-tool.exe`.

Double-click the EXE – it starts Streamlit and opens your browser
automatically.  
The `mistakes.db` file is created in the same folder as the EXE.

---

### Troubleshooting – "server.port does not work when global.developmentMode is true"

<img src="docs/images/error-development-mode.png" alt="Screenshot: RuntimeError server.port does not work when global.developmentMode is true" />

**What the screenshot shows**

A Windows terminal (PowerShell/CMD) displaying a Python traceback that ends
with two critical lines:

```
RuntimeError: server.port does not work when global.developmentMode is true.
[PYI-XXXXX:ERROR] Failed to execute script 'launcher' due to unhandled exception!
```

**Root cause**

When PyInstaller packages a Python application, the frozen binary cannot place
Streamlit's own entry-point script on `sys.argv[0]`.  Streamlit's bootstrap
code interprets this absence as a sign that it is running in a development
environment and automatically sets `global.developmentMode = True`.

Once `developmentMode` is `True`, Streamlit's configuration validator raises a
`RuntimeError` if `server.port` is provided – either via `--server.port` on
the command line or via the `STREAMLIT_SERVER_PORT` env-var *if the validator
has already locked the config*.  The old `launcher.py` passed `--server.port=8501`
as a CLI argument, which always triggers this check in frozen bundles.

**How the fix works**

The updated `launcher.py` sets four environment variables **before** Streamlit
is imported or its config bootstrap runs:

| Variable | Value | Effect |
|---|---|---|
| `STREAMLIT_GLOBAL_DEVELOPMENT_MODE` | `false` | Disables development mode; removes the port restriction |
| `STREAMLIT_SERVER_HEADLESS` | `1` | Suppresses the "running locally" browser prompt |
| `STREAMLIT_SERVER_PORT` | `8501` | Binds to a fixed port (read before the validator runs) |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | `false` | Disables telemetry |

Environment variables are read during Streamlit's very first config load, before
the validator that checks `developmentMode`.  This means the port is set
correctly and the `RuntimeError` is never reached.  The `--server.port` CLI
argument (which re-triggers the validator) is no longer passed.