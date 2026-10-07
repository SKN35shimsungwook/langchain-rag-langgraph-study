# -*- coding: utf-8 -*-
import random

import streamlit as st

import db
from content.questions import BY_ID, CATEGORIES, QUESTIONS
from quiz_state import MODES, current_user, reset_quiz, start_quiz

CIRCLE = ["①", "②", "③", "④"]
SOURCES = {"all": "전체 문제", "wrong": "내 오답노트", "bookmark": "내 북마크"}

user = current_user()


def _labels(quiz, pos):
    q = BY_ID[quiz["ids"][pos]]
    return [f"{CIRCLE[i]} {q['choices'][orig]}" for i, orig in enumerate(quiz["perms"][pos])]


def _is_correct(quiz, pos):
    # perms[pos][화면 보기 번호] = 원래 보기 번호, 원래 0번이 정답
    picked = quiz["picked"].get(pos)
    return picked is not None and quiz["perms"][pos][picked] == 0


def _record(quiz, pos):
    if user:
        db.record_answer(user, quiz["ids"][pos], _is_correct(quiz, pos))


def _submit_one(choice_label):
    quiz = st.session_state.quiz
    if choice_label is None:
        st.session_state.quiz_error = "보기를 하나 고른 뒤 제출해 주세요."
        return
    pos = quiz["pos"]
    quiz["picked"][pos] = CIRCLE.index(choice_label[0])
    quiz["submitted"] = True
    st.session_state.pop("quiz_error", None)
    _record(quiz, pos)


def _next():
    quiz = st.session_state.quiz
    quiz["pos"] += 1
    quiz["submitted"] = False


def _grade_all():
    quiz = st.session_state.quiz
    keys = [f"all_{quiz['run']}_{pos}" for pos in range(len(quiz["ids"]))]
    missing = [str(pos + 1) for pos, key in enumerate(keys) if st.session_state.get(key) is None]
    if missing:
        st.session_state.quiz_error = f"아직 고르지 않은 문제가 있어요: {', '.join(missing)}번"
        return
    for pos, key in enumerate(keys):
        quiz["picked"][pos] = CIRCLE.index(st.session_state[key][0])
        _record(quiz, pos)
    quiz["graded"] = True
    st.session_state.pop("quiz_error", None)


def _bookmark_button(qid, marks, key):
    if not user:
        return
    marked = qid in marks
    st.button(
        "북마크 해제" if marked else "북마크",
        icon=":material/bookmark_remove:" if marked else ":material/bookmark_add:",
        key=key,
        type="tertiary",
        on_click=db.toggle_bookmark,
        args=(user, qid),
    )


def _render_results(quiz, marks):
    ids = quiz["ids"]
    total = len(ids)
    correct = sum(_is_correct(quiz, p) for p in range(total))

    with st.container(horizontal=True):
        st.metric("점수", f"{round(correct / total * 100)}점", border=True)
        st.metric("맞힌 문제", f"{correct} / {total}", border=True)
        st.metric("틀린 문제", total - correct, border=True)

    if user:
        st.caption(f"{user} 님의 풀이 기록과 오답노트에 저장됐어요.")
    else:
        st.caption("사이드바에 이름을 입력하면 다음부터 풀이 기록이 오답노트에 저장돼요.")

    by_cat = {}
    for p, qid in enumerate(ids):
        ok, n = by_cat.get(BY_ID[qid]["cat"], (0, 0))
        by_cat[BY_ID[qid]["cat"]] = (ok + _is_correct(quiz, p), n + 1)
    st.subheader("범위별 정답률")
    st.dataframe(
        {
            "범위": list(by_cat),
            "정답": [f"{ok} / {n}" for ok, n in by_cat.values()],
            "정답률": [ok / n * 100 for ok, n in by_cat.values()],
        },
        column_config={
            "정답률": st.column_config.ProgressColumn("정답률", format="%.0f%%", min_value=0, max_value=100)
        },
        hide_index=True,
    )

    wrong = [p for p in range(total) if not _is_correct(quiz, p)]
    with st.container(horizontal=True):
        st.button("처음부터 다시", icon=":material/restart_alt:", on_click=reset_quiz)
        if wrong:
            st.button(
                f"틀린 {len(wrong)}문제만 다시 풀기",
                type="primary",
                icon=":material/replay:",
                on_click=start_quiz,
                args=([ids[p] for p in wrong], quiz["mode"], True, "방금 틀린 문제"),
            )
    if not wrong:
        st.balloons()
        st.success("전부 맞혔어요!", icon=":material/celebration:")

    # 한 번에 풀기는 전체 문제를 다시 보여 주고, 한 문제씩은 이미 해설을 봤으니 틀린 문제만 모아 준다.
    review = range(total) if quiz["mode"] == "all" else wrong
    if review:
        st.subheader("전체 문제 해설" if quiz["mode"] == "all" else "이번 회차 오답")
    for p in review:
        q = BY_ID[ids[p]]
        ok = _is_correct(quiz, p)
        picked = q["choices"][quiz["perms"][p][quiz["picked"][p]]]
        with st.expander(f"Q{p + 1}. {q['q']}", icon=":material/check:" if ok else ":material/close:", expanded=not ok):
            if ok:
                st.markdown(f"내 답: **{picked}**")
            else:
                st.markdown(f"내 답: ~~{picked}~~")
                st.markdown(f"정답: **{q['choices'][0]}**")
            st.info(q["exp"], icon=":material/lightbulb:")
            _bookmark_button(q["id"], marks, key=f"bm_review_{quiz['run']}_{p}")


st.title("4지선다 퀴즈")
st.caption(f"전체 {len(QUESTIONS)}문항 · 보기 순서는 풀 때마다 섞여요.")

quiz = st.session_state.get("quiz")
marks = set(db.bookmarks(user)) if user else set()

# ── 설정 화면 ─────────────────────────────────────────────────────────
if quiz is None:
    with st.container(border=True):
        mode = st.segmented_control(
            "풀이 방식", list(MODES), format_func=MODES.get, default="one", key="setup_mode"
        )
        st.caption(
            "한 문제씩: 제출할 때마다 바로 채점하고 해설을 보여 줘요. "
            "한 번에 풀기: 모든 문제를 한 페이지에서 푼 뒤 한꺼번에 채점해요."
        )

        source_options = list(SOURCES) if user else ["all"]
        source = st.segmented_control(
            "출제 대상", source_options, format_func=SOURCES.get, default="all", key="setup_source"
        )
        if not user:
            st.caption("사이드바에 이름을 입력하면 풀이 기록이 저장되고, 오답노트·북마크에서도 출제할 수 있어요.")

        if source == "wrong":
            base = [n["qid"] for n in db.wrong_notes(user) if n["qid"] in BY_ID]
        elif source == "bookmark":
            base = [qid for qid in marks if qid in BY_ID]
        else:
            base = [q["id"] for q in QUESTIONS]

        counts = {c: sum(BY_ID[qid]["cat"] == c for qid in base) for c in CATEGORIES}
        cats = st.pills(
            "출제 범위",
            CATEGORIES,
            selection_mode="multi",
            default=CATEGORIES,
            format_func=lambda c: f"{c} ({counts[c]})",
            key=f"setup_cats_{source}",
        )
        pool = [qid for qid in base if BY_ID[qid]["cat"] in (cats or [])]

        if not mode or not source:
            st.warning("풀이 방식과 출제 대상을 골라 주세요.", icon=":material/warning:")
        elif not pool:
            st.warning("조건에 맞는 문제가 없어요. 출제 대상이나 범위를 바꿔 보세요.", icon=":material/warning:")
        else:
            n = st.slider("문항 수", 1, len(pool), len(pool)) if len(pool) > 1 else 1
            shuffle = st.toggle("문제 순서 섞기", value=True)

            def _go():
                picked = random.sample(pool, n) if n < len(pool) else pool
                start_quiz(picked, mode, shuffle, SOURCES[source])

            st.button(f"{n}문항 풀기 시작", type="primary", icon=":material/play_arrow:", on_click=_go)
    st.stop()

ids = quiz["ids"]
total = len(ids)
st.caption(f"{quiz['source']} · {MODES[quiz['mode']]}")

# ── 한 번에 풀기 ─────────────────────────────────────────────────────
if quiz["mode"] == "all":
    if quiz["graded"]:
        _render_results(quiz, marks)
        st.stop()

    with st.form(f"all_form_{quiz['run']}", border=False):
        for pos, qid in enumerate(ids):
            q = BY_ID[qid]
            with st.container(border=True):
                st.badge(q["cat"], color="violet")
                st.markdown(f"**Q{pos + 1}. {q['q']}**")
                st.radio(
                    f"Q{pos + 1} 보기",
                    _labels(quiz, pos),
                    index=None,
                    key=f"all_{quiz['run']}_{pos}",
                    label_visibility="collapsed",
                )
        if st.session_state.get("quiz_error"):
            st.error(st.session_state.quiz_error, icon=":material/error:")
        st.form_submit_button(f"{total}문항 채점하기", type="primary", icon=":material/done_all:", on_click=_grade_all)
    st.button("그만두고 설정으로", icon=":material/close:", on_click=reset_quiz, type="tertiary")
    st.stop()

# ── 한 문제씩 ─────────────────────────────────────────────────────────
pos = quiz["pos"]
if pos >= total:
    _render_results(quiz, marks)
    st.stop()

q = BY_ID[ids[pos]]
labels = _labels(quiz, pos)

st.progress(pos / total, text=f"{pos + 1} / {total}")
with st.container(border=True):
    with st.container(horizontal=True, vertical_alignment="center"):
        st.badge(q["cat"], color="violet")
        st.space("stretch")
        _bookmark_button(q["id"], marks, key=f"bm_one_{quiz['run']}_{pos}")
    st.markdown(f"#### Q{pos + 1}. {q['q']}")
    choice = st.radio(
        "보기",
        labels,
        index=None,
        key=f"radio_{quiz['run']}_{pos}",
        disabled=quiz["submitted"],
        on_change=lambda: st.session_state.pop("quiz_error", None),
        label_visibility="collapsed",
    )

    if not quiz["submitted"]:
        if st.session_state.get("quiz_error"):
            st.error(st.session_state.quiz_error, icon=":material/error:")
        st.button("제출", type="primary", icon=":material/check:", on_click=_submit_one, args=(choice,))
    else:
        answer_label = labels[quiz["perms"][pos].index(0)]
        if _is_correct(quiz, pos):
            st.success(f"정답이에요! {answer_label}", icon=":material/check_circle:")
        else:
            st.error(f"오답이에요. 정답은 {answer_label}", icon=":material/cancel:")
        st.info(q["exp"], icon=":material/lightbulb:")
        last = pos + 1 >= total
        st.button(
            "결과 보기" if last else "다음 문제",
            type="primary",
            icon=":material/flag:" if last else ":material/arrow_forward:",
            on_click=_next,
        )

st.button("그만두고 설정으로", icon=":material/close:", on_click=reset_quiz, type="tertiary")
