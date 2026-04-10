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

### What triggers the build?

The **Build Windows EXE** workflow runs automatically every time code is
pushed (or a PR is merged) to `main`.  This means **you always get a
fresh, downloadable EXE right after any merge** – no manual step needed.

You can also trigger it on demand:
**Actions → Build Windows EXE → Run workflow → Run workflow** (select `main`).

### How to download the EXE

1. Go to [Actions → Build Windows EXE](../../actions/workflows/build-windows.yml).
2. Click the latest successful run (green ✓).
3. Scroll to the **Artifacts** section at the bottom of the run page.
4. Click **aws-mistake-tool-windows** to download the ZIP.
5. Unzip to get `aws-mistake-tool.exe`.

Double-click the EXE – it starts Streamlit and opens your browser
automatically.  
The `mistakes.db` file is created in the same folder as the EXE.

---

## GitHub Actions workflows explained

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| **Build Windows EXE** | `build-windows.yml` | Push / merge to `main`, or manual | **Builds the app into a Windows `.exe`** using PyInstaller and uploads it as a downloadable Artifact. This is the workflow that produces the exe you download. |

> **Is "Build Windows EXE" just a CI check?**  
> No – it is a **build-and-package** workflow. When it finishes (green ✓),
> a ready-to-run `aws-mistake-tool.exe` is available in the **Artifacts**
> section of that run. CI/check workflows only validate code; this one
> actually produces something you download and use.