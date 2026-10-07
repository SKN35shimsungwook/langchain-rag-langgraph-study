# -*- coding: utf-8 -*-
"""마인드맵과 흐름도의 Mermaid 정의.

mindmap 문법에서는 괄호, 대괄호, 파이프 같은 기호가 노드 모양으로 해석되므로 라벨에 넣지 않는다.
중심 노드도 모양 지정 없이 둔다. 원·사각형 모양을 주면 라벨이 가운데가 아니라 중심점에서 시작해 절반이 잘린다.
"""

OVERVIEW = """
mindmap
  LLM 애플리케이션
    LangChain
      부품 조립
      Prompt · Model · Parser
      Retriever · Runnable
      LCEL 파이프 연결
    RAG
      검색 후 생성
      사전 준비
        Loader → Chunking
        Embedding → Vector DB
      질문 처리
        Retriever → Reranking
        Context → Generation
    LangGraph
      흐름 제어
      State · Node · Edge
      분기 · 반복 · 병렬
      Reducer · Checkpoint
    Agent
      LLM이 다음 행동 판단
      Tool 호출
      Multi-agent
    LangGraph + RAG
      검색 필요 판단
      Query Rewrite
      Faithfulness 검사
"""

BRANCHES = {
    "LangChain · LCEL": """
mindmap
  LangChain
    역할
      LLM 부품 연결 프레임워크
      비유 레고 부품과 연결 방식
    대표 부품
      Prompt
        지시 형식
      Model
        실제 LLM
      Parser
        출력 변환
      Retriever
        문서 가져오기
      Runnable
        공통 실행 규격
    LCEL
      파이프 연산자로 연결
      Chain
        순서 고정 실행 묶음
      흐름
        dict 입력
        PromptTemplate
        ChatModel
        AIMessage
        StrOutputParser
        str 출력
    Runnable 도구
      RunnableLambda
        함수를 Runnable로
      RunnablePassthrough
        입력 그대로 유지
      invoke
        한 번 실행
""",
    "RAG": """
mindmap
  RAG
    정의
      검색 증강 생성
      비유 책 찾아보고 답하기
    사전 준비
      Document
        page_content
        metadata
      Loader
        파일을 Document로
      Text Cleaning
      Chunking
        RecursiveCharacterTextSplitter
        chunk_size 1000
        chunk_overlap 150
      Embedding
        텍스트를 벡터로
      Vector DB
        FAISS · Chroma · Pinecone
    질문 처리
      질문 Embedding
      유사도 검색
      Retriever
        비유 도서관 사서
      Reranking
        관련도 재정렬
      Context
        프롬프트에 근거 삽입
      Generation
        LLM 답변 생성
    디버깅
      검색 오류
        청킹 · 임베딩 · 검색 설정
      생성 오류
        프롬프트 · 모델
""",
    "LangGraph 기본": """
mindmap
  LangGraph
    필요한 이유
      조건 분기
      반복 루프
      재시도
      병렬 실행
    핵심 3요소
      State
        공유 데이터
        비유 가방
        TypedDict로 구조 정의
      Node
        실제 작업 함수
        비유 작업실
        바뀐 키만 dict로 반환
      Edge
        다음 Node로 가는 길
        add_edge 고정 길
        add_conditional_edges 갈림길
        route_fn 라우팅 함수
    조립과 실행
      StateGraph 빌더
      add_node
      START · END
      compile
      invoke
""",
    "LangGraph 심화": """
mindmap
  LangGraph 심화
    병렬 실행
      Fan-out
        하나에서 여러 개
      Fan-in
        여러 개에서 하나
      Crossfade는 오답
    Reducer
      병렬 결과 병합 규칙
      Annotated
      operator.add
        리스트 이어 붙이기
      기본은 덮어쓰기
    반복 · 검증
      답변 검증 Node
      부족하면 되돌아가기
      좋으면 END
      재시도 횟수 상한
    상태 보존
      Checkpoint
        State 저장 · 복구
        checkpointer
        thread_id
      Memory
        대화 맥락 유지
      Human-in-the-loop
        사람 승인 후 진행
""",
    "Agent · 응용": """
mindmap
  Agent · 응용
    Agent
      LLM이 다음 행동 판단
      Tool
        검색 · 계산기 · DB
      누가 결정하나
        고정 Chain 개발자 순서
        Workflow 개발자 조건
        Agent LLM 판단
      Multi-agent
        Manager Agent
        Research · Coding · Review
    LangGraph + RAG
      질문 분석
      검색 필요 판단
      문서 충분성 판단
      Query Rewrite
      재검색
      Faithfulness 검사
      재생성
    실전 예시
      고객 상담 챗봇
        문의 유형 라우팅
      문서 분석 시스템
        근거 부족시 추가 검색
      코드 리뷰 Agent
        테스트 실패시 재수정
      강화학습 보조
        Reward 분석
        Exploration 분석
""",
}

FLOWS = {
    "RAG 파이프라인": """
flowchart LR
    subgraph prep["사전 준비"]
        direction TB
        A["PDF / 문서"] --> B["Loader"] --> C["Text Cleaning"] --> D["Chunking"] --> E["Embedding"] --> F[("Vector DB")]
    end
    subgraph ask["질문 처리"]
        direction TB
        Q["사용자 질문"] --> QE["질문 Embedding"] --> R["Retriever"] --> RR["Reranking"] --> CTX["Prompt의 Context에 삽입"] --> L["LLM"] --> ANS["Answer"]
    end
    F -. "유사도 검색" .-> R
""",
    "LangGraph로 만든 RAG": """
flowchart TD
    S(["START"]) --> A["질문 분석"]
    A --> B{"검색 필요?"}
    B -- "NO" --> G["답변 생성"]
    B -- "YES" --> R["Retriever"]
    R --> C{"문서 충분?"}
    C -- "YES" --> G
    C -- "NO" --> W["Query Rewrite"] --> R
    G --> F{"Faithfulness 통과?"}
    F -- "YES" --> E(["END"])
    F -- "NO" --> G
""",
    "그래프 조립 순서": """
flowchart LR
    A["State 정의<br/>TypedDict"] --> B["StateGraph 생성"] --> C["add_node"] --> D["add_edge<br/>add_conditional_edges"] --> E["compile()"] --> F["invoke()"]
""",
    "Fan-out · Fan-in": """
flowchart LR
    A["질문 분석 Node"] --> B["웹 검색"]
    A --> C["Vector DB 검색"]
    B --> D["합치기 Node"]
    C --> D
    D --> E["results = A + B<br/>Reducer: operator.add"]
""",
    "Human-in-the-loop": """
flowchart LR
    A["AI 초안 생성"] --> B{"사용자 승인?"}
    B -- "YES" --> C["다음 단계"]
    B -- "NO" --> D["수정 Node"] --> A
    A -. "State 저장" .-> CP[("Checkpoint")]
""",
}
