import json

def pretty_print_hits(hits, title: str):
    print(f"\n========\n{title}")

    if not hits or not hits.points:
        print("No results")
        return

    formatted = []
    for p in hits.points:
        formatted.append({
            "id": p.id,
            "score": p.score,
            "payload": p.payload
        })

    print(json.dumps(formatted, indent=4, ensure_ascii=False))