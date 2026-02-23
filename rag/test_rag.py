from rag_core import answer

res = answer("우울증이 뭐야?", k=4)

print("\n=== ANSWER ===")
print(res["answer"])

print("\n=== CONTEXTS USED ===")
for i, c in enumerate(res["contexts"], 1):
    print(f"\n--- chunk {i} ---")
    print(c[:400])
