# -*- coding: utf-8 -*-
import streamlit as st

import db
from content.questions import BY_ID, CATEGORIES
from quiz_state import MODES, QUIZ_PAGE, require_user, start_quiz

st.title("오답노트")
user = require_user()
st.caption(
    f"{user} 님이 틀린 문제가 자동으로 모여요. "
    f"오답노트에 있는 문제를 {db.CLEAR_STREAK}번 연속으로 맞히면 자동으로 빠져요."
)

notes = [n for n in db.wrong_notes(user) if n["qid"] in BY_ID]
marks = [qid for qid in db.bookmarks(user) if qid in BY_ID]


def _go(qids, mode, source):
    start_quiz(qids, mode, True, source)
    st.switch_page(QUIZ_PAGE)


def _retry_bar(qids, label, key):
    with st.container(horizontal=True, vertical_alignment="bottom"):
        mode = st.segmented_control(
            "풀이 방식", list(MODES), format_func=MODES.get, default="one", key=f"{key}_mode"
        )
        if st.button(
            f"{label} {len(qids)}문제 다시 풀기",
            type="primary",
            icon=":material/replay:",
            key=f"{key}_go",
            disabled=not qids or not mode,
        ):
            _go(qids, mode, f"내 {label}")


def _choices(q):
    st.markdown("\n".join(f"- {'**' + c + '** (정답)' if i == 0 else c}" for i, c in enumerate(q["choices"])))
    st.info(q["exp"], icon=":material/lightbulb:")


wrong_tab, mark_tab = st.tabs([f"오답노트 ({len(notes)})", f"북마크 ({len(marks)})"])

with wrong_tab:
    if not notes:
        st.success("오답노트가 비어 있어요. 퀴즈를 풀다가 틀린 문제가 여기에 모여요.", icon=":material/task_alt:")
    else:
        counts = {c: sum(BY_ID[n["qid"]]["cat"] == c for n in notes) for c in CATEGORIES}
        cats = st.pills(
            "범위",
            [c for c in CATEGORIES if counts[c]],
            selection_mode="multi",
            default=[c for c in CATEGORIES if counts[c]],
            format_func=lambda c: f"{c} ({counts[c]})",
            key="note_cats",
        )
        shown = [n for n in notes if BY_ID[n["qid"]]["cat"] in (cats or [])]
        _retry_bar([n["qid"] for n in shown], "오답", "note")
        st.caption("많이 틀린 문제부터 보여 줘요.")

        for n in shown:
            q = BY_ID[n["qid"]]
            title = f"{q['q']}  ·  틀린 횟수 {n['wrong_count']}  ·  연속 정답 {n['streak']}/{db.CLEAR_STREAK}"
            with st.expander(title, icon=":material/edit_note:" if n["memo"] else ":material/close:"):
                st.badge(q["cat"], color="violet")
                _choices(q)
                with st.form(f"memo_{n['qid']}", border=False):
                    memo = st.text_area("나만의 메모", value=n["memo"], placeholder="헷갈린 이유, 외울 포인트 등")
                    if st.form_submit_button("메모 저장", icon=":material/save:"):
                        db.save_memo(user, n["qid"], memo.strip())
                        st.toast("메모를 저장했어요.", icon=":material/check:")
                        st.rerun()
                st.button(
                    "오답노트에서 빼기",
                    icon=":material/delete:",
                    type="tertiary",
                    key=f"rm_{n['qid']}",
                    on_click=db.remove_wrong,
                    args=(user, n["qid"]),
                )

with mark_tab:
    if not marks:
        st.info("북마크한 문제가 없어요. 퀴즈 화면에서 북마크 버튼을 눌러 보세요.", icon=":material/bookmark:")
    else:
        _retry_bar(marks, "북마크", "mark")
        for qid in marks:
            q = BY_ID[qid]
            with st.expander(q["q"], icon=":material/bookmark:"):
                st.badge(q["cat"], color="violet")
                _choices(q)
                st.button(
                    "북마크 해제",
                    icon=":material/bookmark_remove:",
                    type="tertiary",
                    key=f"unmark_{qid}",
                    on_click=db.toggle_bookmark,
                    args=(user, qid),
                )
