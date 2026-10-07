# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

import db
from content.questions import BY_ID, CATEGORIES, QUESTIONS
from quiz_state import QUIZ_PAGE, require_user, start_quiz

st.title("약점 통계")
user = require_user()

rows = [a for a in db.attempts(user) if a["qid"] in BY_ID]
if not rows:
    st.info("아직 푼 문제가 없어요. 퀴즈를 풀면 여기에 통계가 쌓여요.", icon=":material/insights:")
    st.stop()

df = pd.DataFrame(rows)
df["cat"] = df["qid"].map(lambda qid: BY_ID[qid]["cat"])
df["date"] = pd.to_datetime(df["ts"]).dt.date

solved = df["qid"].nunique()
with st.container(horizontal=True):
    st.metric("총 풀이 수", len(df), border=True)
    st.metric("전체 정답률", f"{df['correct'].mean() * 100:.0f}%", border=True)
    st.metric("푼 문제", f"{solved} / {len(QUESTIONS)}", border=True)
    st.metric("오답노트", len(db.wrong_notes(user)), border=True)

st.subheader("범위별 정답률")
by_cat = (
    df.groupby("cat")["correct"]
    .agg(정답률=lambda s: s.mean() * 100, 풀이수="count")
    .reindex(CATEGORIES)
    .dropna()
)
weakest = by_cat["정답률"].idxmin()
st.bar_chart(by_cat, y="정답률", horizontal=True, x_label="정답률 (%)", y_label="", sort="정답률")
st.caption(f"가장 약한 범위는 **{weakest}** ({by_cat.loc[weakest, '정답률']:.0f}%)예요.")


def _drill(cat):
    start_quiz([q["id"] for q in QUESTIONS if q["cat"] == cat], "one", True, f"약점 집중: {cat}")
    st.switch_page(QUIZ_PAGE)


if st.button(f"{weakest} 문제 집중 풀기", icon=":material/target:", type="primary"):
    _drill(weakest)

st.subheader("자주 틀리는 문제")
wrong = df[df["correct"] == 0]
if wrong.empty:
    st.success("아직 틀린 문제가 없어요.", icon=":material/celebration:")
else:
    top = (
        df.groupby("qid")["correct"]
        .agg(틀린횟수=lambda s: int((s == 0).sum()), 풀이수="count")
        .query("틀린횟수 > 0")
        .sort_values(["틀린횟수", "풀이수"], ascending=[False, True])
        .head(10)
        .reset_index()
    )
    top["범위"] = top["qid"].map(lambda qid: BY_ID[qid]["cat"])
    top["문제"] = top["qid"].map(lambda qid: BY_ID[qid]["q"])
    top["정답"] = top["qid"].map(lambda qid: BY_ID[qid]["choices"][0])
    st.dataframe(top[["범위", "문제", "정답", "틀린횟수", "풀이수"]], hide_index=True)

st.subheader("날짜별 풀이")
daily = df.groupby("date")["correct"].agg(풀이수="count", 정답률=lambda s: s.mean() * 100)
st.line_chart(daily, y="정답률", y_label="정답률 (%)", x_label="")
st.bar_chart(daily, y="풀이수", y_label="풀이 수", x_label="")
