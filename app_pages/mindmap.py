# -*- coding: utf-8 -*-
import streamlit as st

from content.mindmaps import BRANCHES, FLOWS, OVERVIEW

st.title("마인드맵")
st.caption("전체 지도 → 가지별 상세 지도 → 실제 실행 흐름도 순서로 보면 연결 관계가 잡혀요.")

st.subheader("전체 지도")
with st.container(border=True):
    st.mermaid_chart(OVERVIEW)

st.subheader("가지별 상세 지도")
for tab, body in zip(st.tabs(list(BRANCHES)), BRANCHES.values()):
    with tab:
        with st.container(border=True):
            st.mermaid_chart(body)

st.subheader("실행 흐름도")
st.caption("마인드맵이 '무엇이 있는지'라면, 흐름도는 '어떤 순서로 이어지는지'예요.")
for tab, body in zip(st.tabs(list(FLOWS)), FLOWS.values()):
    with tab:
        with st.container(border=True):
            st.mermaid_chart(body)
