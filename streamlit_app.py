# -*- coding: utf-8 -*-
"""LangChain · RAG · LangGraph 흐름 중심 학습 페이지 (용어 정리 + 마인드맵 + 4지선다 퀴즈 + 오답노트)."""
import streamlit as st

st.set_page_config(
    page_title="LangChain · RAG · LangGraph 정리",
    page_icon=":material/account_tree:",
    layout="wide",
    initial_sidebar_state="expanded",
)

page = st.navigation(
    {
        "공부하기": [
            st.Page("app_pages/concepts.py", title="용어 정리", icon=":material/menu_book:", default=True),
            st.Page("app_pages/mindmap.py", title="마인드맵", icon=":material/hub:"),
        ],
        "문제 풀기": [
            st.Page("app_pages/quiz.py", title="4지선다 퀴즈", icon=":material/quiz:"),
            st.Page("app_pages/notebook.py", title="오답노트", icon=":material/edit_note:"),
        ],
    },
    position="top",
)

# 진입 파일에서 매번 그리는 위젯이라 페이지를 옮겨도 이름이 유지된다.
with st.sidebar:
    st.text_input(
        "이름",
        key="user_name",
        placeholder="예: 홍길동",
        icon=":material/person:",
        help="이름별로 풀이 기록 · 오답노트 · 북마크가 따로 저장돼요. 같은 이름을 쓰면 기록을 함께 써요.",
    )
    st.caption("이름을 입력하면 틀린 문제가 오답노트에 자동으로 모여요.")

page.run()
