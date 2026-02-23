# debug_rag_check.py
import os, json
import numpy as np
import faiss
from openai import OpenAI

INDEX_PATH  = "data/index.faiss"
META_PATH   = "data/meta.json"
CHUNKS_PATH = "data/chunks.jsonl"

EMBED_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def load_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def embed(text: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=[text])
    v = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(v)
    return v


def preview_text(t: str, n: int = 220) -> str:
    t = (t or "").replace("\n", " ").strip()
    return t[:n] + ("..." if len(t) > n else "")


def main():
    # --- load ---
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    chunks = load_jsonl(CHUNKS_PATH)

    print("=== FILE CHECK ===")
    print(f"- index:  {INDEX_PATH}")
    print(f"- meta:   {META_PATH} (items={len(meta)})")
    print(f"- chunks: {CHUNKS_PATH} (items={len(chunks)})")

    # --- sanity: counts ---
    if len(meta) != len(chunks):
        print("\n[WARN] meta와 chunks 길이가 다릅니다!")
        print(" - idx 기반 매칭이면 출처/본문이 엇갈릴 수 있어요.")
    else:
        print("\n[OK] meta와 chunks 길이 동일 (idx 기반 매칭 가능)")

    # --- meta text existence ---
    meta_has_text = sum(1 for m in meta if isinstance(m, dict) and "text" in m and (m["text"] or "").strip())
    print("\n=== META TEXT FIELD ===")
    print(f"- meta에 'text'가 (비어있지 않게) 들어있는 항목 수: {meta_has_text} / {len(meta)}")

    # --- vector count check (IndexFlatIP) ---
    try:
        ntotal = index.ntotal
        print("\n=== INDEX CHECK ===")
        print(f"- index.ntotal = {ntotal}")
        if ntotal != len(meta):
            print("[WARN] index 벡터 개수(ntotal)와 meta 길이가 다릅니다! (매칭 깨질 가능성)")
    except Exception as e:
        print("\n[WARN] index.ntotal 확인 실패:", e)

    # --- query test ---
    q = input("\n테스트 질문을 입력하세요: ").strip()
    if not q:
        print("질문이 비어있어서 종료합니다.")
        return

    k = 4
    qv = embed(q)
    scores, idxs = index.search(qv, k)

    print("\n=== TOP HITS ===")
    for rank, (score, idx) in enumerate(zip(scores[0], idxs[0]), start=1):
        if idx == -1:
            continue

        m = meta[idx]
        title = (m.get("title") if isinstance(m, dict) else None) or ""
        src   = (m.get("source") if isinstance(m, dict) else None) or ""
        url   = (m.get("url") if isinstance(m, dict) else None) or ""

        # rag_core 방식 (meta에서 text 찾기)
        meta_text = ""
        if isinstance(m, dict):
            meta_text = m.get("text", "") or ""

        # chunks.jsonl에서 text 찾기
        chunk_text = ""
        try:
            chunk_text = chunks[idx].get("text", "") or ""
        except Exception:
            chunk_text = ""

        print(f"\n[{rank}] idx={idx} score={float(score):.4f}")
        print(f" - source/title: {src} | {title}")
        print(f" - url: {url}")

        print(" - meta_text preview:  ", preview_text(meta_text))
        print(" - chunks_text preview:", preview_text(chunk_text))

        if not meta_text.strip() and chunk_text.strip():
            print("   ✅ 결론: meta에는 text가 없고, chunks에서만 text가 존재합니다.")
        elif meta_text.strip():
            print("   ✅ 결론: meta에도 text가 들어있습니다. (현재 rag_core도 컨텍스트가 채워질 수 있음)")
        else:
            print("   ❌ 결론: meta에도 없고 chunks에도 text가 비었습니다. 데이터 파이프라인 점검 필요.")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
