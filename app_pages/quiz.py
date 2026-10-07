# -*- coding: utf-8 -*-
import random

import streamlit as st

from content.questions import CATEGORIES, QUESTIONS

CIRCLE = ["①", "②", "③", "④"]


def _start(question_ids, shuffle_questions):
    ids = list(question_ids)
    if shuffle_questions:
        random.shuffle(ids)
    # 문제은행은 첫 보기가 정답이라 보기 순서는 항상 섞는다.
    st.session_state.quiz = {
        "ids": ids,
        "perms": [random.sample(range(4), 4) for _ in ids],
        "pos": 0,
        "picked": {},
        "submitted": False,
        "run": random.getrandbits(32),
    }


def _submit(choice_label):
    quiz = st.session_state.quiz
    pos = quiz["pos"]
    if choice_label is None:
        st.session_state.quiz_error = "보기를 하나 고른 뒤 제출해 주세요."
        return
    quiz["picked"][pos] = CIRCLE.index(choice_label[0])
    quiz["submitted"] = True
    st.session_state.pop("quiz_error", None)


def _next():
    quiz = st.session_state.quiz
    quiz["pos"] += 1
    quiz["submitted"] = False


def _reset():
    st.session_state.pop("quiz", None)


def _is_correct(quiz, pos):
    # perm[display_idx] = 원래 보기 인덱스, 원래 인덱스 0이 정답
    return quiz["perms"][pos][quiz["picked"][pos]] == 0


st.title("4지선다 퀴즈")
st.caption(f"전체 {len(QUESTIONS)}문항 · 보기 순서는 풀 때마다 섞여요.")

quiz = st.session_state.get("quiz")

# ── 설정 화면 ─────────────────────────────────────────────────────────
if quiz is None:
    counts = {c: sum(q["cat"] == c for q in QUESTIONS) for c in CATEGORIES}
    with st.container(border=True):
        cats = st.pills(
            "출제 범위",
            CATEGORIES,
            selection_mode="multi",
            default=CATEGORIES,
            format_func=lambda c: f"{c} ({counts[c]})",
        )
        pool = [i for i, q in enumerate(QUESTIONS) if q["cat"] in (cats or [])]
        if pool:
            n = st.slider("문항 수", 1, len(pool), len(pool))
            shuffle_questions = st.toggle("문제 순서 섞기", value=True)
            st.button(
                f"{n}문항 풀기 시작",
                type="primary",
                icon=":material/play_arrow:",
                on_click=lambda: _start(
                    random.sample(pool, n) if n < len(pool) else pool, shuffle_questions
                ),
            )
        else:
            st.warning("출제 범위를 하나 이상 골라 주세요.", icon=":material/warning:")
    st.stop()

ids, pos = quiz["ids"], quiz["pos"]
total = len(ids)

# ── 결과 화면 ─────────────────────────────────────────────────────────
if pos >= total:
    correct = sum(_is_correct(quiz, p) for p in range(total))
    score = round(correct / total * 100)

    with st.container(horizontal=True):
        st.metric("점수", f"{score}점", border=True)
        st.metric("맞힌 문제", f"{correct} / {total}", border=True)
        st.metric("틀린 문제", total - correct, border=True)

    by_cat = {}
    for p, qid in enumerate(ids):
        cat = QUESTIONS[qid]["cat"]
        ok, n = by_cat.get(cat, (0, 0))
        by_cat[cat] = (ok + _is_correct(quiz, p), n + 1)
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
        st.button("처음부터 다시", icon=":material/restart_alt:", on_click=_reset)
        if wrong:
            st.button(
                f"틀린 {len(wrong)}문제만 다시 풀기",
                type="primary",
                icon=":material/replay:",
                on_click=lambda: _start([ids[p] for p in wrong], True),
            )

    if wrong:
        st.subheader("오답 노트")
        for p in wrong:
            q = QUESTIONS[ids[p]]
            picked = q["choices"][quiz["perms"][p][quiz["picked"][p]]]
            with st.expander(f"{q['q']}", icon=":material/close:"):
                st.markdown(f"내가 고른 답: ~~{picked}~~")
                st.markdown(f"정답: **{q['choices'][0]}**")
                st.info(q["exp"], icon=":material/lightbulb:")
    else:
        st.balloons()
        st.success("전부 맞혔어요!", icon=":material/celebration:")
    st.stop()

# ── 문제 풀이 화면 ────────────────────────────────────────────────────
q = QUESTIONS[ids[pos]]
perm = quiz["perms"][pos]
labels = [f"{CIRCLE[i]} {q['choices'][orig]}" for i, orig in enumerate(perm)]

st.progress(pos / total, text=f"{pos + 1} / {total}")
with st.container(border=True):
    st.badge(q["cat"], color="violet")
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
        st.button("제출", type="primary", icon=":material/check:", on_click=_submit, args=(choice,))
    else:
        answer_label = labels[perm.index(0)]
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

st.button("그만두고 설정으로", icon=":material/close:", on_click=_reset, type="tertiary")
