"""
app.py – Streamlit UI for the AWS practice-exam mistake tracker.

Two modes (sidebar):
  1. Input mistake  – paste question block, auto-parse, preview, save.
  2. Filter/Search  – filter by exam/domain/tag/keyword, paginate, expand details.
"""

import math

import streamlit as st

from db import (
    count_mistakes,
    distinct_exams,
    get_conn,
    get_mistake,
    init_db,
    insert_mistake,
    list_mistakes,
)
from parser import parse_mistake_block

st.set_page_config(page_title="AWS Mistake Tracker", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar – common settings
# ---------------------------------------------------------------------------
st.sidebar.title("AWS Mistake Tracker")

DB_PATH = st.sidebar.text_input("Database path", value="mistakes.db")
conn = get_conn(DB_PATH)
init_db(conn)

mode = st.sidebar.radio("Mode", ["Input mistake", "Filter / Search"], index=0)

DOMAIN_CODES = ["CC", "SEC", "TECH", "BILL"]
DOMAIN_LABELS = {
    "CC": "CC – Cloud Concepts",
    "SEC": "SEC – Security & Compliance",
    "TECH": "TECH – Cloud Technology & Services",
    "BILL": "BILL – Billing, Pricing & Support",
}

# ---------------------------------------------------------------------------
# Mode 1: Input mistake
# ---------------------------------------------------------------------------
if mode == "Input mistake":
    st.title("📝 Input Mistake")
    st.caption(
        "Paste the full question block below, fill in the metadata, "
        "then **Preview** to check parsing before saving."
    )

    col_meta, col_block = st.columns([1, 2])

    with col_meta:
        exam = st.text_input("Exam", value="CLF-C02")
        domain = st.selectbox(
            "Domain",
            DOMAIN_CODES,
            format_func=lambda c: DOMAIN_LABELS[c],
            index=2,
        )
        topic = st.text_input("Topic / knowledge point", value="")
        tags = st.text_input("Tags (comma-separated)", value="")
        reason = st.text_area("Why did you get it wrong?", value="", height=100)

    with col_block:
        st.markdown("**Question block** – paste here:")
        sample = (
            "Which AWS service lets you run code without provisioning servers?\n"
            "A. Amazon EC2\n"
            "B. AWS Lambda\n"
            "C. Amazon ECS\n"
            "D. AWS Batch\n"
            "Correct answer: B\n"
            "Your answer: A"
        )
        raw_text = st.text_area(
            "Paste question block",
            value=sample,
            height=260,
            label_visibility="collapsed",
        )

        st.markdown(
            "<small>Supported formats: "
            "`Correct answer: D` · `Correct answers: A,C` · "
            "`Correct answers: AC` · `Your answer: B` · `Your answers: A C`"
            "</small>",
            unsafe_allow_html=True,
        )

    c1, c2, _ = st.columns([1, 1, 4])
    preview_clicked = c1.button("🔍 Preview parse")
    save_clicked = c2.button("💾 Save")

    if preview_clicked or save_clicked:
        try:
            parsed = parse_mistake_block(raw_text)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        if preview_clicked:
            st.subheader("Parsed result")
            with st.expander("Parsed fields", expanded=True):
                st.write("**Question:**", parsed["question"])
                for letter in "ABCDEF":
                    val = parsed.get(f"option_{letter.lower()}")
                    if val:
                        st.write(f"**{letter}.**", val)
                st.write("**Correct letters:**", parsed["correct_letters"])
                if parsed["your_letters"] is not None:
                    verdict = "✅ Correct" if parsed["your_correct"] else "❌ Wrong"
                    st.write(
                        "**Your letters:**",
                        parsed["your_letters"],
                        "→",
                        verdict,
                    )

        if save_clicked:
            row = {
                "exam": exam.strip() or "CLF-C02",
                "domain": domain,
                "topic": topic.strip(),
                "tags": tags.strip(),
                "reason": reason.strip(),
                **parsed,
            }
            new_id = insert_mistake(conn, row)
            st.success(f"✅ Saved – mistake id = {new_id}")

# ---------------------------------------------------------------------------
# Mode 2: Filter / Search
# ---------------------------------------------------------------------------
else:
    st.title("🔎 Filter / Search")

    # --- Filter controls ---------------------------------------------------
    all_exams = distinct_exams(conn)
    exam_options = ["(all)"] + all_exams
    exam_filter = st.selectbox("Exam", exam_options, index=0)
    exam_val = None if exam_filter == "(all)" else exam_filter

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        domain_filter = st.selectbox(
            "Domain",
            ["ALL"] + DOMAIN_CODES,
            format_func=lambda c: "ALL – show all" if c == "ALL" else DOMAIN_LABELS[c],
            index=0,
        )
    with fcol2:
        tag_filter = st.text_input("Tag contains", value="")
    with fcol3:
        keyword_filter = st.text_input("Keyword (question / topic / reason)", value="")

    tcol1, tcol2 = st.columns(2)
    with tcol1:
        only_incorrect = st.toggle(
            "Only incorrect (your answer ≠ correct)",
            value=False,
        )
    with tcol2:
        only_correct = st.toggle(
            "Only correct (your answer = correct)",
            value=False,
        )

    # Mutual-exclusive guard
    if only_incorrect and only_correct:
        st.warning("Cannot filter for both correct and incorrect simultaneously. Showing all.")
        only_incorrect = False
        only_correct = False

    page_size = st.selectbox("Per page", [5, 10, 20, 50], index=1)

    # --- Query & pagination ------------------------------------------------
    filter_kwargs = dict(
        exam=exam_val,
        domain=domain_filter,
        tag=tag_filter.strip() or None,
        keyword=keyword_filter.strip() or None,
        only_incorrect=only_incorrect,
        only_correct=only_correct,
    )
    total = count_mistakes(conn, **filter_kwargs)
    total_pages = max(1, math.ceil(total / page_size))

    st.caption(f"**{total}** result(s) · **{total_pages}** page(s)")

    # Pagination via session state so Prev/Next buttons work reliably
    if "page" not in st.session_state:
        st.session_state.page = 1
    # Clamp to valid range whenever total_pages changes
    st.session_state.page = max(1, min(st.session_state.page, total_pages))

    page = st.session_state.page
    offset = (page - 1) * page_size

    rows = list_mistakes(conn, limit=page_size, offset=offset, **filter_kwargs)

    if total == 0:
        st.info("No results – try different filters.")
    else:
        for r in rows:
            # Build expander header
            verdict = ""
            if r["your_correct"] is not None:
                verdict = " ✅" if r["your_correct"] else " ❌"
            header = (
                f"#{r['id']} | {r['created_at']} | "
                f"{r['exam']} | {r['domain'] or '—'} | "
                f"{r['topic'] or '—'} | "
                f"Correct: {r['correct_letters']}{verdict}"
            )

            with st.expander(header):
                st.write("**Question:**", r["question"])

                # Render options from the summary row
                # (full options only in detail view)
                st.write("**Correct answer(s):**", r["correct_letters"])
                if r["your_letters"]:
                    st.write("**Your answer(s):**", r["your_letters"])

                st.write("**Tags:**", r["tags"] or "—")
                st.write("**Reason:**", r["reason"] or "—")

                if st.button(f"Load full detail", key=f"detail-{r['id']}"):
                    detail = get_mistake(conn, r["id"])
                    if detail:
                        st.divider()
                        for letter in "ABCDEF":
                            val = detail[f"option_{letter.lower()}"]
                            if val:
                                mark = ""
                                if letter in (detail["correct_letters"] or "").split(","):
                                    mark = " ✅"
                                if detail["your_letters"] and letter in (detail["your_letters"] or "").split(","):
                                    mark += " ← your answer"
                                st.write(f"**{letter}.** {val}{mark}")
                        st.divider()
                        st.markdown("**Raw block:**")
                        st.code(detail["raw_text"])

        # Navigation buttons
        st.divider()
        nav1, nav2, nav3 = st.columns([1, 1, 4])
        with nav1:
            if st.button("⬅ Prev") and page > 1:
                st.session_state.page = page - 1
                st.rerun()
        with nav2:
            if st.button("Next ➡") and page < total_pages:
                st.session_state.page = page + 1
                st.rerun()
