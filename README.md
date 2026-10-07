# LangChain · RAG · LangGraph 흐름 중심 정리

LangChain, RAG, LangGraph를 "용어 암기"가 아니라 "왜 생겼고, 시스템 안에서 어디에 쓰이며, 어떻게 연결되는지" 중심으로 정리한 Streamlit 학습 페이지예요.

## 페이지 구성

| 페이지 | 내용 |
|---|---|
| 용어 정리 | 14개 섹션, 93개 용어를 풀어서 설명 · 용어 검색 · 코드 예시와 흐름도 · 비유표 · 헷갈리는 짝 |
| 마인드맵 | 전체 마인드맵 1개 + 가지별 상세 마인드맵 5개 + 실행 흐름도 5개 (Mermaid) |
| 4지선다 퀴즈 | 60문항 (LangChain·LCEL 11 / RAG 15 / LangGraph 기본 14 / LangGraph 심화 10 / Agent·응용 10) · 범위·문항 수 선택 · 보기 순서 섞기 · 즉시 채점과 해설 · 범위별 정답률 · 오답 노트 · 틀린 문제만 다시 풀기 |

## 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 파일 구조

```
langgraph_study/
├── streamlit_app.py        # 진입점 (st.navigation으로 3개 페이지 연결)
├── app_pages/
│   ├── concepts.py         # 용어 정리
│   ├── mindmap.py          # 마인드맵 · 흐름도
│   └── quiz.py             # 4지선다 퀴즈
├── content/
│   ├── terms.py            # 섹션별 용어 데이터
│   ├── mindmaps.py         # Mermaid 마인드맵 · 흐름도 정의
│   └── questions.py        # 문제은행 (첫 번째 보기가 정답, 앱에서 섞음)
├── .streamlit/config.toml  # 테마 색
└── requirements.txt
```

## 문제 추가하기

`content/questions.py`의 `QUESTIONS`에 `_q(범위, 질문, [정답, 오답1, 오답2, 오답3], 해설)`을 추가하면 돼요.
보기 순서는 퀴즈를 시작할 때마다 섞이므로 정답은 항상 첫 번째에 적어요.

## Streamlit Community Cloud 배포

1. 이 폴더를 GitHub 저장소에 올려요 (폴더 내용을 저장소 루트에 두는 것을 권장).
2. [share.streamlit.io](https://share.streamlit.io)에서 **Create app** → 저장소와 브랜치 선택.
3. Main file path에 `streamlit_app.py`를 입력하고 Deploy.

비밀 키나 외부 API를 쓰지 않아서 Secrets 설정은 필요 없어요.
