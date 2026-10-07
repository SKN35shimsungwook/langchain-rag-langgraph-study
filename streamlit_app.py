# -*- coding: utf-8 -*-
"""LangChain · RAG · LangGraph 흐름 중심 학습 페이지 (용어 정리 + 마인드맵 + 4지선다 퀴즈)."""
import streamlit as st

st.set_page_config(
    page_title="LangChain · RAG · LangGraph 정리",
    page_icon=":material/account_tree:",
    layout="wide",
)

page = st.navigation(
    [
        st.Page("app_pages/concepts.py", title="용어 정리", icon=":material/menu_book:", default=True),
        st.Page("app_pages/mindmap.py", title="마인드맵", icon=":material/hub:"),
        st.Page("app_pages/quiz.py", title="4지선다 퀴즈", icon=":material/quiz:"),
    ],
    position="top",
)

page.run()
