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

### How to download the EXE

1. Open [Actions → Build Windows EXE](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml).
2. Click the latest successful run that shows a green ✓ checkmark.
3. Scroll down to the **Artifacts** section at the bottom of the run page.
4. Click **aws-mistake-tool-windows** to download a ZIP file.
5. Unzip the file to get `aws-mistake-tool.exe`.

### How to run

1. Place `aws-mistake-tool.exe` in any folder of your choice.
2. Double-click `aws-mistake-tool.exe`.
3. A browser window opens automatically at **http://localhost:8501**.

> **Note:** The `mistakes.db` database file is created in the same folder as the EXE.  
> Keep the EXE and `mistakes.db` in the same folder so your data is preserved between sessions.

> **Firewall / antivirus:** Windows may show a SmartScreen warning the first time you run the EXE because it is unsigned. Click **More info → Run anyway** to proceed.

### Troubleshooting – "server.port does not work when global.developmentMode is true"

If you see this error when launching the EXE:

```
RuntimeError: server.port does not work when global.developmentMode is true.
Failed to execute script 'launcher' due to unhandled exception!
```

**Root cause:** When PyInstaller packages a Python application, Streamlit cannot
find its own script on `sys.argv[0]` inside the bundle and automatically sets
`global.developmentMode = True`. Once in development mode, Streamlit's validator
raises a `RuntimeError` if `server.port` is provided as a CLI argument.

**Fix (already applied in this repo):** `launcher.py` now sets the env-var
`STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false` (plus `STREAMLIT_SERVER_PORT` and
others) **before** Streamlit is imported, bypassing the validator entirely.
If you are on an older build, re-download the EXE after the latest
`main`-branch build completes.