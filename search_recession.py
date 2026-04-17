import os, sys

root = '.'
matches = []
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(dirpath, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    for i, line in enumerate(fh, 1):
                        if any(k in line for k in ['Recession Risk', 'recession_risk', 'compute_recession', 'recession']):
                            out = line.strip().encode('ascii', 'replace').decode()
                            matches.append(f"{path}:{i}: {out[:100]}")
            except Exception as e:
                pass

for m in matches[:50]:
    print(m)
print(f"\nTotal matches: {len(matches)}")
