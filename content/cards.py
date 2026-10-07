# -*- coding: utf-8 -*-
"""용어 정리(terms.py)의 용어 93개로 암기 카드 · 빈칸 채우기 · OX 퀴즈 데이터를 만든다."""
import random
import re

from content.terms import SECTIONS

GROUPS = ["큰 그림", "LangChain · LCEL", "RAG", "LangGraph 기본", "LangGraph 심화", "Agent · 응용"]

_SECTION_GROUP = {
    "overview": "큰 그림",
    "langchain": "LangChain · LCEL",
    "lcel": "LangChain · LCEL",
    "rag_index": "RAG",
    "rag_query": "RAG",
    "why_graph": "LangGraph 기본",
    "graph_core": "LangGraph 기본",
    "graph_build": "LangGraph 기본",
    "parallel": "LangGraph 심화",
    "loop": "LangGraph 심화",
    "checkpoint": "LangGraph 심화",
    "agent": "Agent · 응용",
    "graph_rag": "Agent · 응용",
    "examples": "Agent · 응용",
}

# 괄호 안이 같은 뜻의 다른 이름이 아니라 구분용 설명인 용어는 정답으로 인정할 표기를 직접 정한다.
_ANSWER_OVERRIDES = {
    "invoke() (그래프)": ["invoke()"],
    "Crossfade (함정)": ["Crossfade"],
    "Workflow (LangGraph)": ["Workflow"],
}

BLANK = "〔　　　〕"


def _answers(term):
    """채점할 때 정답으로 인정할 표기 목록. '표기 (다른 이름)'은 둘 다, 'A / B'는 각각도 인정한다."""
    if term in _ANSWER_OVERRIDES:
        return list(_ANSWER_OVERRIDES[term])
    out = [term]
    m = re.match(r"^(.*?)\s*\(([^)]*)\)$", term)
    if m and m.group(1):
        out += [m.group(1), m.group(2)]
    for item in list(out):
        if " / " in item:
            out += item.split(" / ")
    return [a.strip() for a in out if a.strip()]


def _mask(text, answers):
    """설명 안에 정답 표기가 그대로 들어 있으면 빈칸으로 가려서 답이 새지 않게 한다."""
    for a in sorted(answers, key=len, reverse=True):
        if len(a) >= 2:
            text = re.sub(re.escape(a), BLANK, text, flags=re.IGNORECASE)
    return text


def _build():
    cards = []
    for section in SECTIONS:
        for term, desc in section["terms"]:
            answers = _answers(term)
            cards.append(
                {
                    "id": f"{section['id']}:{term}",
                    "group": _SECTION_GROUP[section["id"]],
                    "section": section["title"],
                    "term": term,
                    "desc": desc,
                    "answers": answers,
                    "masked": _mask(desc, answers),
                }
            )
    return cards


CARDS = _build()
CARD_BY_ID = {c["id"]: c for c in CARDS}


def _normalize(s):
    s = re.sub(r"\(\)", "", s.strip().lower())
    return re.sub(r"[\s·\-_]+", "", s)


def is_correct(card, user_input):
    """띄어쓰기 · 대소문자 · 가운뎃점 · 하이픈 · 밑줄 · 함수 괄호()는 무시하고 비교한다."""
    if not user_input or not user_input.strip():
        return False
    u = _normalize(user_input)
    return any(u == _normalize(a) for a in card["answers"])


def blank_hints(card):
    """빈칸 채우기 힌트: 정답과 같은 범위의 다른 용어 3개를 섞어 보여 준다(카드마다 순서 고정)."""
    rng = random.Random(card["id"])
    same = [c["term"] for c in CARDS if c["group"] == card["group"] and c["id"] != card["id"]]
    hints = rng.sample(same, min(3, len(same))) + [card["term"]]
    rng.shuffle(hints)
    return hints


def build_ox(cards):
    """반은 맞는 설명, 반은 같은 범위의 다른 용어 설명을 붙여 OX 문제를 만든다."""
    pool = []
    for c in cards:
        if random.random() < 0.5:
            pool.append({"cid": c["id"], "statement": c["masked"], "truth": True, "real": c["term"]})
            continue
        others = [o for o in CARDS if o["group"] == c["group"] and o["id"] != c["id"]] or [
            o for o in CARDS if o["id"] != c["id"]
        ]
        other = random.choice(others)
        # 다른 용어의 설명에는 그 용어 이름이 들어 있을 수 있어서 가린 설명을 쓴다.
        pool.append({"cid": c["id"], "statement": other["masked"], "truth": False, "real": other["term"]})
    random.shuffle(pool)
    return pool
