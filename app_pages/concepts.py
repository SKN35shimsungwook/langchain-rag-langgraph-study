# -*- coding: utf-8 -*-
import streamlit as st

from content.terms import ANALOGIES, CONFUSING_PAIRS, SECTIONS

st.title("LangChain · RAG · LangGraph 용어 정리")
st.caption("'이 용어가 뭐지?'가 아니라 '왜 생겼고, 어디에 쓰이며, 어떻게 연결되는지'를 이해하는 자료")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.markdown("**LangChain**  \n부품 조립")
    c2.markdown("**RAG**  \n검색해서 답하는 방법")
    c3.markdown("**LangGraph**  \n전체 실행 흐름 제어")

query = st.text_input(
    "용어 검색",
    placeholder="예: Reducer, 청킹, compile",
    icon=":material/search:",
).strip().lower()


def _matches(term, desc):
    return not query or query in term.lower() or query in desc.lower()


total_shown = 0
for section in SECTIONS:
    terms = [(t, d) for t, d in section["terms"] if _matches(t, d)]
    if query and not terms:
        continue
    total_shown += len(terms)

    st.subheader(section["title"], anchor=section["id"])
    st.markdown(f"{section['icon']} {section['intro']}")
    st.markdown("\n".join(f"- **{t}** — {d}" for t, d in terms))

    if not query:
        if section.get("flow"):
            st.code(section["flow"], language=None)
        if section.get("code"):
            st.code(section["code"], language="python")
    st.divider()

if query and total_shown == 0:
    st.info(f"'{query}'에 해당하는 용어가 없어요.", icon=":material/search_off:")

if not query:
    st.subheader("비유로 다시 보기")
    st.table(
        {
            "개념": [a[0] for a in ANALOGIES],
            "역할": [a[1] for a in ANALOGIES],
            "비유": [a[2] for a in ANALOGIES],
        }
    )

    st.subheader("시험에서 헷갈리기 쉬운 짝")
    for left, left_desc, right, right_desc in CONFUSING_PAIRS:
        with st.container(border=True, horizontal=True, gap="large"):
            st.markdown(f"**{left}**  \n{left_desc}")
            st.markdown("vs")
            st.markdown(f"**{right}**  \n{right_desc}")

    st.subheader("최종 한 줄")
    st.success(
        "RAG는 '무엇을 검색해서 답할지', LangGraph는 '검색을 언제 하고, 실패하면 어떻게 다시 할지, "
        "조건에 따라 어디로 갈지'를 제어한다.",
        icon=":material/lightbulb:",
    )
