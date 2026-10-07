# -*- coding: utf-8 -*-
"""여러 페이지에서 함께 쓰는 사용자 이름 · 퀴즈 시작 도우미."""
import random

import streamlit as st

QUIZ_PAGE = "app_pages/quiz.py"
MODES = {"one": "한 문제씩", "all": "한 번에 풀기"}


def current_user():
    return (st.session_state.get("user_name") or "").strip()


def require_user():
    """이름이 없으면 안내를 띄우고 페이지 실행을 멈춘다."""
    user = current_user()
    if not user:
        st.info("왼쪽 사이드바에 이름을 입력하면 내 기록을 볼 수 있어요.", icon=":material/person:")
        st.stop()
    return user


def start_quiz(qids, mode, shuffle=True, source="전체 문제"):
    qids = list(qids)
    if shuffle:
        random.shuffle(qids)
    # 문제은행은 첫 보기가 정답이라 보기 순서는 항상 섞는다.
    st.session_state.quiz = {
        "ids": qids,
        "perms": [random.sample(range(4), 4) for _ in qids],
        "mode": mode,
        "source": source,
        "pos": 0,
        "picked": {},
        "submitted": False,
        "graded": False,
        "recorded": False,
        "run": random.getrandbits(32),
    }
    st.session_state.pop("quiz_error", None)


def reset_quiz():
    st.session_state.pop("quiz", None)
    st.session_state.pop("quiz_error", None)
