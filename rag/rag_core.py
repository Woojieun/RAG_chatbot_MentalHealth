# rag/rag_core.py
import os
import json
import numpy as np
import faiss
from openai import OpenAI

# =========================
# Paths / Models
# =========================
INDEX_PATH = "data/index.faiss"
META_PATH = "data/meta.json"

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# =========================
# RAG Safety / Policy
# =========================
NO_INFO_MSG = "현재 제공된 자료에는 해당 주제가 포함되어 있지 않습니다."

# FAISS가 "항상 뭔가"를 내놓는 문제를 막기 위한 점수 컷
# - 너무 높으면 정상 질문도 막힐 수 있음 → 0.15~0.30 사이에서 로그 보고 조정 추천
MIN_SCORE = 0.08

# "정신건강 범주"가 아닌 질문은(사과/날씨/프로그래밍 등) 그냥 차단
MH_KEYWORDS = [
    # 한국어
    "정신건강", "멘탈", "마음", "심리", "상담", "치료", "증상", "장애", "질환",
    "스트레스", "불안", "우울", "공황", "강박", "조현", "양극", "조울",
    "adhd", "자폐", "ptsd", "트라우마", "섭식", "거식", "폭식",
    "수면", "불면", "번아웃", "자해", "자살", "공포", "긴장",

    # 영어 (혹시)
    "mental health", "stress", "anxiety", "depression", "panic", "ocd",
    "schizophrenia", "bipolar", "adhd", "autism", "ptsd", "trauma",
    "eating disorder", "insomnia", "burnout", "self-harm", "suicide",
]

def is_mental_health_query(q: str) -> bool:
    t = (q or "").lower()
    return any(k in t for k in MH_KEYWORDS)

# =========================
# Load index/meta once
# =========================
_index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    # build_index(string->int64 IDMap) 결과:
    # {"<int_id>": {"int_id":..., "id":"who_mh_001", "source":..., "title":..., "url":..., "text":...}, ...}
    _meta_by_intid = json.load(f)

# =========================
# Query expansion (optional)
# =========================
ALIASES = {
    "우울": "depression major depressive disorder clinical depression",
    "불안": "anxiety disorders generalized anxiety disorder panic disorder",
    "조현": "schizophrenia psychosis",
    "강박": "obsessive-compulsive disorder OCD",
    "양극": "bipolar disorder manic depressive",
    "adhd": "attention deficit hyperactivity disorder ADHD",
    "자폐": "autism spectrum disorder ASD",
    "ptsd": "post-traumatic stress disorder PTSD trauma",
    "섭식": "eating disorders anorexia bulimia binge eating",
    "경계성": "borderline personality disorder BPD",
}

def expand_query(query: str) -> str:
    q = (query or "").lower()
    extras = []
    for k, v in ALIASES.items():
        if k in q:
            extras.append(v)
    return query + (" " + " ".join(extras) if extras else "")

# =========================
# Embedding / Retrieval
# =========================
def embed(text: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=[text])
    v = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(v)
    return v

def retrieve(query: str, k: int = 6):
    # expand for search only (alias expansion)
    q2 = expand_query(query)
    qv = embed(q2)

    # ✅ IndexIDMap: "ids" are int64 chunk ids (not positional indices)
    scores, ids = _index.search(qv, k)

    hits = []
    for score, cid in zip(scores[0], ids[0]):
        if cid == -1:
            continue
        hits.append((float(score), int(cid)))
    return hits

# =========================
# Answer
# =========================
def answer(query: str, k: int = 4):
    """
    - 정신건강 범주 밖 질문: 즉시 NO_INFO_MSG
    - retrieval: top-k보다 조금 더 크게 뽑고(기본 6), 점수 컷(MIN_SCORE) 적용 후 상위 k개 사용
    - hits 없으면 GPT 호출 금지
    - GPT가 NO_INFO_MSG를 말하면 출처 링크 절대 붙이지 않음
    """
    q = (query or "").strip()
    if not q:
        return {"answer": NO_INFO_MSG, "citations": []}

    # 1) 정신건강 범주 아닌 질문은 차단 (사과 같은 케이스 방지)
    if not is_mental_health_query(q):
        return {"answer": NO_INFO_MSG, "citations": []}

    # 2) 검색 (조금 넉넉히 뽑고 필터링)
    hits = retrieve(q, k=max(k * 2, 6))
    hits = [(s, cid) for s, cid in hits if s >= MIN_SCORE]
    hits = hits[:k]

    # ✅ hits 없으면 GPT 호출 자체를 안 함
    if not hits:
        return {"answer": NO_INFO_MSG, "citations": []}

    # 3) 컨텍스트 구성
    contexts = []
    citations = []

    # debug
    print("QUERY:", q)
    print("HITS (after threshold):")

    for score, cid in hits:
        m = _meta_by_intid.get(str(cid))
        if not m:
            continue

        print("HIT:", score, m.get("title"))

        citations.append({**m, "score": score})

        chunk_text = (m.get("text") or "").strip()
        contexts.append(
            f"[{m.get('source','')} | {m.get('title','')}]\n"
            f"URL: {m.get('url','')}\n"
            f"CONTENT:\n{chunk_text}"
        )

    # 혹시 meta 누락 등으로 컨텍스트가 비면 종료
    if not contexts:
        return {"answer": NO_INFO_MSG, "citations": []}

    context_block = "\n\n".join(contexts)
    print("CONTEXT_SAMPLE:\n", context_block[:500])

    # 4) System prompt
    # - "자료 없으면 딱 한 문장" 강제
    # - 일반 지식 금지(단, 소스 기반 요약/재진술은 허용)
    system = (
        "You are an information support assistant for mental health topics. "
        "Use ONLY the provided sources to answer the question. "
        "If the sources are insufficient, say you do not have enough information. "
        "Do NOT mention sources, links, or references in the answer text. "
        "Do not provide medical diagnosis or personalized treatment advice."
    )   


    user = (
        f"Question:\n{q}\n\n"
        f"Sources:\n{context_block}\n\n"
        "Write a concise, helpful answer in Korean."
    )

    # 5) Generate
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    bot_answer = (resp.choices[0].message.content or "").strip()

    # ✅ 자료 없음 응답이면 출처 링크/시테이션 둘 다 제거
    if bot_answer == NO_INFO_MSG:
        return {"answer": bot_answer, "citations": []}

    # 6) 출처 링크 붙이기 (정신건강 질문에서만, 그리고 NO_INFO가 아닐 때만)
    #    - top1만 붙임 (원하면 top3로 확장 가능)
    if citations:
        top = citations[0]
        title = top.get("title", "")
        url = top.get("url", "")
        source = top.get("source", "")
        if title and url:
            bot_answer += f"\n\n더 자세한 정보는 [{source}의 {title}]({url})를 참고하세요."

    return {"answer": bot_answer, "citations": citations}
