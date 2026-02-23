# build_index.py (IDMap + string id support)
import os, json, hashlib
import numpy as np
import faiss
from openai import OpenAI

DATA_PATH  = "data/chunks.jsonl"
INDEX_PATH = "data/index.faiss"
META_PATH  = "data/meta.json"

EMBED_MODEL = "text-embedding-3-small"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def load_jsonl(path: str):
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def str_id_to_int64(s: str) -> np.int64:
    """
    Stable 64-bit ID from string.
    - Same string -> same int64
    - Very low collision risk for small/medium corpora
    """
    s = str(s)
    digest = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()  # 8 bytes = 64 bits
    u = int.from_bytes(digest, byteorder="big", signed=False)            # 0..2^64-1
    # FAISS는 int64를 쓰므로 signed로 맞춰줌(음수도 가능하지만 괜찮음)
    if u >= 2**63:
        u -= 2**64
    return np.int64(u)


def main():
    docs = load_jsonl(DATA_PATH)
    if not docs:
        raise ValueError("chunks.jsonl이 비어있습니다.")

    # --- make ids (int64) ---
    raw_ids = []
    ids = []
    for d in docs:
        if "id" not in d:
            raise ValueError("chunks.jsonl에 id가 없는 항목이 있습니다.")
        rid = d["id"]
        raw_ids.append(str(rid))
        ids.append(str_id_to_int64(rid))

    # 중복 검사(충돌/중복 감지)
    if len(set(raw_ids)) != len(raw_ids):
        raise ValueError("chunks.jsonl에 중복 문자열 id가 있습니다. id는 반드시 고유해야 합니다.")
    if len(set(map(int, ids))) != len(ids):
        raise ValueError(
            "문자열 id -> int64 변환 과정에서 충돌(중복)이 발생했습니다. "
            "digest_size를 늘리거나 다른 방식으로 id를 생성해야 합니다."
        )

    texts = [d["text"] for d in docs]

    # --- embeddings (batch) ---
    vectors = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vectors.extend([x.embedding for x in resp.data])

    embeddings = np.array(vectors, dtype="float32")
    faiss.normalize_L2(embeddings)

    # --- FAISS index with IDs ---
    dim = embeddings.shape[1]
    base = faiss.IndexFlatIP(dim)
    index = faiss.IndexIDMap2(base)

    ids_np = np.array(ids, dtype=np.int64)
    index.add_with_ids(embeddings, ids_np)

    faiss.write_index(index, INDEX_PATH)

    # --- meta: int_id(str) -> metadata (원본 string id도 보존) ---
    meta_by_intid = {}
    for d, rid, iid in zip(docs, raw_ids, ids):
        meta_by_intid[str(int(iid))] = {
            "int_id": int(iid),     # FAISS용
            "id": rid,              # 원본 문자열 id (who_mh_001)
            "source": d.get("source"),
            "title": d.get("title"),
            "url": d.get("url"),
            "text": d.get("text"),
        }

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta_by_intid, f, ensure_ascii=False, indent=2)

    print(f"✅ indexed {len(docs)} chunks (IDMap string->int64)")
    print(f"- saved: {INDEX_PATH}")
    print(f"- saved: {META_PATH}")


if __name__ == "__main__":
    main()