# -*- coding: utf-8 -*-
import random

import streamlit as st

import db
from content.cards import BLANK, CARD_BY_ID, CARDS, GROUPS, blank_hints, build_ox, is_correct
from quiz_state import current_user

ss = st.session_state
user = current_user()
CARD_MODES = ["뒤집기", "단어 입력형", "빈칸 채우기"]

st.title("개념 카드")
st.caption(f"용어 정리의 용어 {len(CARDS)}개로 외우고 확인해요. 이름을 입력하면 틀린 카드가 따로 모여요.")

view = st.segmented_control("보기 방식", ["카드", "OX 퀴즈"], default="카드", key="cards_view")
counts = {g: sum(c["group"] == g for c in CARDS) for g in GROUPS}
groups = st.pills(
    "범위",
    GROUPS,
    selection_mode="multi",
    default=GROUPS,
    format_func=lambda g: f"{g} ({counts[g]})",
    key="cards_groups",
)
filtered = [c["id"] for c in CARDS if c["group"] in (groups or [])]
if not view:
    st.warning("보기 방식을 골라 주세요.", icon=":material/warning:")
    st.stop()
if not filtered:
    st.warning("범위를 하나 이상 골라 주세요.", icon=":material/warning:")
    st.stop()


def _record(kind, cid, correct):
    if user:
        db.mark_concept(user, kind, cid, correct)


# ── 카드 ─────────────────────────────────────────────────────────────
def _card_order():
    # 범위가 바뀌면 순서를 새로 잡고, 같은 범위면 섞어 둔 순서를 유지한다.
    if sorted(ss.get("card_order", [])) != sorted(filtered):
        ss.card_order = list(filtered)
        ss.card_idx = 0
        ss.card_flipped = False
    return ss.card_order


def _move(step):
    ss.card_idx += step
    ss.card_flipped = False


def _shuffle():
    random.shuffle(ss.card_order)
    ss.card_idx = 0
    ss.card_flipped = False


def _check(cid, mode, gave_up=False):
    answer = ss.get(f"card_in_{mode}_{cid}", "")
    ok = (not gave_up) and is_correct(CARD_BY_ID[cid], answer)
    ss.card_results[(mode, cid)] = ok
    _record("card", cid, ok)


def _render_cards():
    order = _card_order()
    ss.setdefault("card_results", {})
    ss.card_idx = min(ss.get("card_idx", 0), len(order) - 1)
    card = CARD_BY_ID[order[ss.card_idx]]
    cid = card["id"]

    with st.container(horizontal=True, vertical_alignment="bottom"):
        mode = st.segmented_control("확인 방식", CARD_MODES, default="뒤집기", key="card_mode")
        front = None
        if mode == "뒤집기":
            front = st.segmented_control("앞면", ["용어", "설명"], default="용어", key="card_front")
    if not mode:
        st.warning("확인 방식을 골라 주세요.", icon=":material/warning:")
        return

    st.progress((ss.card_idx + 1) / len(order), text=f"{ss.card_idx + 1} / {len(order)}")
    with st.container(border=True):
        st.badge(card["group"], color="violet")
        st.caption(card["section"])

        if mode == "뒤집기":
            if front == "설명":
                st.markdown(f"#### {card['masked']}")
                if ss.get("card_flipped"):
                    st.success(f"정답: **{card['term']}**", icon=":material/check_circle:")
            else:
                st.markdown(f"### {card['term']}")
                if ss.get("card_flipped"):
                    st.info(card["desc"], icon=":material/lightbulb:")
            if not ss.get("card_flipped"):
                st.caption("정답 보기를 누르면 뒷면이 나와요.")
        else:
            if mode == "단어 입력형":
                st.markdown(f"#### {card['masked']}")
                st.caption("이 설명에 해당하는 용어를 입력하세요.")
            else:
                st.markdown(f"#### {BLANK} — {card['masked']}")
                st.caption("힌트: " + " · ".join(blank_hints(card)))

            result = ss.card_results.get((mode, cid))
            if result is None:
                with st.form(f"card_form_{mode}_{cid}", border=False):
                    st.text_input(
                        "정답 입력",
                        key=f"card_in_{mode}_{cid}",
                        placeholder="정답을 입력하고 Enter",
                        label_visibility="collapsed",
                    )
                    with st.container(horizontal=True):
                        st.form_submit_button("확인", type="primary", icon=":material/check:", on_click=_check, args=(cid, mode))
                        st.form_submit_button("모르겠어요", icon=":material/help:", on_click=_check, args=(cid, mode, True))
            else:
                if result:
                    st.success(f"정답이에요! **{card['term']}**", icon=":material/check_circle:")
                else:
                    st.error(f"아쉬워요. 정답은 **{card['term']}**", icon=":material/cancel:")
                st.info(card["desc"], icon=":material/lightbulb:")
                st.button(
                    "다시 시도",
                    icon=":material/replay:",
                    key=f"card_retry_{mode}_{cid}",
                    on_click=lambda: ss.card_results.pop((mode, cid), None),
                )

    with st.container(horizontal=True):
        st.button("이전", icon=":material/arrow_back:", disabled=ss.card_idx == 0, on_click=_move, args=(-1,))
        if mode == "뒤집기":
            st.button(
                "다시 가리기" if ss.get("card_flipped") else "정답 보기",
                type="primary",
                icon=":material/flip:",
                on_click=lambda: ss.update(card_flipped=not ss.get("card_flipped")),
            )
        st.button(
            "다음", icon=":material/arrow_forward:", disabled=ss.card_idx >= len(order) - 1, on_click=_move, args=(1,)
        )
        st.button("순서 섞기", icon=":material/shuffle:", on_click=_shuffle)
        if mode != "뒤집기":
            st.button("푼 카드 초기화", icon=":material/restart_alt:", on_click=lambda: ss.card_results.clear())

    _render_wrong_cards()


def _retry_wrong(cid):
    ok = is_correct(CARD_BY_ID[cid], ss.get(f"cw_in_{cid}", ""))
    db.mark_concept(user, "card", cid, ok)
    if not ok:
        ss[f"cw_fail_{cid}"] = True


def _render_wrong_cards():
    st.divider()
    if not user:
        st.caption("사이드바에 이름을 입력하면 단어 입력형 · 빈칸 채우기에서 틀린 카드가 '카드 오답'에 모여요.")
        return
    wrong = [cid for cid in db.concept_wrongs(user, "card") if cid in CARD_BY_ID]
    with st.expander(f"카드 오답 ({len(wrong)})", icon=":material/style:"):
        if not wrong:
            st.caption("아직 단어 입력형 · 빈칸 채우기에서 틀린 카드가 없어요.")
        else:
            st.caption("바로 정답을 입력해 다시 풀어 보세요. 맞히면 목록에서 빠져요.")
        for cid in wrong:
            card = CARD_BY_ID[cid]
            with st.container(border=True):
                st.markdown(f"**{card['masked']}**")
                if ss.get(f"cw_fail_{cid}"):
                    st.error(f"오답이에요. 정답: **{card['term']}**", icon=":material/cancel:")
                    st.button("다시 시도", key=f"cw_again_{cid}", on_click=lambda c=cid: ss.pop(f"cw_fail_{c}", None))
                    continue
                with st.form(f"cw_form_{cid}", border=False):
                    st.text_input("정답 입력", key=f"cw_in_{cid}", label_visibility="collapsed", placeholder="정답 입력")
                    with st.container(horizontal=True):
                        st.form_submit_button("확인", on_click=_retry_wrong, args=(cid,))
                        st.form_submit_button(
                            "목록에서 지우기", type="tertiary", on_click=db.mark_concept, args=(user, "card", cid, True)
                        )


# ── OX 퀴즈 ──────────────────────────────────────────────────────────
def _ox_start(cids):
    ss.ox = {"pool": build_ox(cids_to_cards(cids)), "pos": 0, "correct": 0, "picked": None}


def cids_to_cards(cids):
    return [CARD_BY_ID[c] for c in cids]


def _ox_answer(choice):
    ox = ss.ox
    item = ox["pool"][ox["pos"]]
    ox["picked"] = choice
    ok = choice == item["truth"]
    ox["correct"] += ok
    _record("ox", item["cid"], ok)


def _ox_next():
    ss.ox["pos"] += 1
    ss.ox["picked"] = None


def _render_ox():
    ox = ss.get("ox")
    if ox is None:
        with st.container(border=True):
            st.caption("용어와 설명이 제대로 짝지어졌는지 O / X로 빠르게 판단하는 암기 확인 퀴즈예요.")
            n = st.slider("문항 수", 1, len(filtered), min(20, len(filtered))) if len(filtered) > 1 else 1
            st.button(
                f"OX 퀴즈 {n}문항 시작",
                type="primary",
                icon=":material/play_arrow:",
                on_click=lambda: _ox_start(random.sample(filtered, n)),
            )
        _render_wrong_ox()
        return

    total = len(ox["pool"])
    if ox["pos"] >= total:
        with st.container(horizontal=True):
            st.metric("점수", f"{round(ox['correct'] / total * 100)}점", border=True)
            st.metric("맞힌 문제", f"{ox['correct']} / {total}", border=True)
        st.button("새 OX 퀴즈", type="primary", icon=":material/restart_alt:", on_click=lambda: ss.pop("ox", None))
        _render_wrong_ox()
        return

    item = ox["pool"][ox["pos"]]
    card = CARD_BY_ID[item["cid"]]
    st.progress(ox["pos"] / total, text=f"{ox['pos'] + 1} / {total} · 맞힘 {ox['correct']}")
    with st.container(border=True):
        st.badge(card["group"], color="violet")
        st.markdown(f"### {card['term']}")
        st.markdown(f"#### {item['statement']}")
        st.caption("이 설명이 위 용어의 설명이 맞나요?")
        if ox["picked"] is None:
            with st.container(horizontal=True):
                st.button("O 맞아요", type="primary", icon=":material/radio_button_unchecked:", on_click=_ox_answer, args=(True,))
                st.button("X 아니에요", icon=":material/close:", on_click=_ox_answer, args=(False,))
        else:
            ok = ox["picked"] == item["truth"]
            answer = "O" if item["truth"] else "X"
            if ok:
                st.success(f"정답이에요! ({answer})", icon=":material/check_circle:")
            else:
                st.error(f"오답이에요. 정답은 {answer}", icon=":material/cancel:")
            if not item["truth"]:
                st.markdown(f"이 설명은 **{item['real']}**의 설명이에요.")
            st.info(f"{card['term']} — {card['desc']}", icon=":material/lightbulb:")
            st.button(
                "결과 보기" if ox["pos"] + 1 >= total else "다음 문제",
                type="primary",
                icon=":material/arrow_forward:",
                on_click=_ox_next,
            )
    st.button("그만두기", icon=":material/close:", type="tertiary", on_click=lambda: ss.pop("ox", None))


def _render_wrong_ox():
    if not user:
        st.caption("사이드바에 이름을 입력하면 OX 퀴즈에서 틀린 용어가 'OX 오답'에 모여요.")
        return
    wrong = [cid for cid in db.concept_wrongs(user, "ox") if cid in CARD_BY_ID]
    with st.expander(f"OX 오답 ({len(wrong)})", icon=":material/rule:"):
        if not wrong:
            st.caption("아직 OX 퀴즈에서 틀린 용어가 없어요.")
            return
        st.caption("OX 퀴즈에서 다시 맞히면 자동으로 빠져요.")
        st.button(
            f"OX 오답 {len(wrong)}개로 퀴즈 풀기",
            icon=":material/replay:",
            on_click=_ox_start,
            args=(wrong,),
        )
        for cid in wrong:
            card = CARD_BY_ID[cid]
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**{card['term']}** — {card['desc']}")
                st.button(
                    "외웠어요",
                    key=f"ox_clear_{cid}",
                    type="tertiary",
                    icon=":material/done:",
                    on_click=db.mark_concept,
                    args=(user, "ox", cid, True),
                )


if view == "카드":
    _render_cards()
else:
    _render_ox()
