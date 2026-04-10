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

[![Build Windows EXE (manual)](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml/badge.svg)](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml)

The EXE is built **on demand** (manual trigger only – it does **not** run
automatically on every push or PR merge).

**How to build and download the EXE:**
1. Go to [Actions → Build Windows EXE (manual)](https://github.com/DaoC-del/aws-mistake-tool/actions/workflows/build-windows.yml).
2. Click **Run workflow** (top-right of the workflow list), select the `main` branch, then click the green **Run workflow** button.
3. Wait for the run to finish (green ✓ appears next to it).
4. Click on that run to open its details page.
5. Scroll to the **Artifacts** section at the bottom.
6. Click **aws-mistake-tool-windows** to download the ZIP, then unzip to get `aws-mistake-tool.exe`.

**How to run:**
1. Place `aws-mistake-tool.exe` in any folder of your choice.
2. Double-click `aws-mistake-tool.exe`.
3. A browser window opens automatically at **http://localhost:8501**.

> **Note:** The `mistakes.db` database file is created in the same folder as the EXE.
> Keep the EXE and `mistakes.db` together so your data is preserved between sessions.

> **Firewall / antivirus:** Windows may show a SmartScreen warning the first time
> you run the EXE because it is unsigned. Click **More info → Run anyway** to proceed.