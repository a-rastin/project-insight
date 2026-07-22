import json
from pathlib import Path
from datetime import datetime, timezone

# Read assembled graph, layers, tour
with open(r'E:\diagnosis\.understand-anything\intermediate\assembled-graph.json') as f:
    ag = json.load(f)
with open(r'E:\diagnosis\.understand-anything\intermediate\layers.json') as f:
    layers = json.load(f)
with open(r'E:\diagnosis\.understand-anything\intermediate\tour.json') as f:
    tour = json.load(f)

graph = {
    'version': '1.0.0',
    'project': {
        'name': 'diagnosis',
        'languages': ['python', 'html', 'markdown', 'txt'],
        'frameworks': ['FastAPI', 'uvicorn', 'sqlite3', 'stdlib unittest', 'httpx'],
        'description': 'DSM-5-TR schizophrenia criteria checklist (Insight diagnosis module). A FastAPI router exposing a minimalist REST seam over a pure-function DSM-5-TR evaluation, backed by a SQLite repository adapter. Clinician-authoritative -- the model never auto-decides.',
        'analyzedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'gitCommitHash': '2ad29b87e9f0c13940f7c3809ee28929547bf49f'
    },
    'nodes': ag['nodes'],
    'edges': ag['edges'],
    'layers': layers,
    'tour': tour
}

out = r'E:\diagnosis\.understand-anything\intermediate\full-graph.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(graph, f, indent=2)
print(f'Written {Path(out).stat().st_size} bytes')

# Verify structure
with open(out) as f:
    g2 = json.load(f)
print(f'verified: nodes={len(g2["nodes"])} edges={len(g2["edges"])} layers={len(g2["layers"])} tour={len(g2["tour"])}')
print(f'layers[0].id={g2["layers"][0]["id"]}')
print(f'tour[0][order]={g2["tour"][0]["order"]}')