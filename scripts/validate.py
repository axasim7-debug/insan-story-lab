from pathlib import Path
import re,csv,hashlib
root=Path(__file__).resolve().parents[1]
errors=[]
for p in root.rglob('*.md'):
    if '.git' in p.parts: continue
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'): continue
        if not (p.parent/target.split('#')[0]).exists():errors.append(f'{p.relative_to(root)}: missing {target}')
with (root/'research/SOURCES.csv').open() as f: sources=list(csv.DictReader(f))
ids={x['source_id'] for x in sources}
if len(ids)!=len(sources):errors.append('Duplicate source IDs')
for p in root.rglob('*.md'):
    for ref in set(re.findall(r'\bS\d{3}\b',p.read_text())):
        if ref not in ids:errors.append(f'{p.relative_to(root)}: unknown {ref}')
for p in root.rglob('*.csv'):
    with p.open() as f: rows=list(csv.reader(f))
    if not rows:errors.append(f'{p.name}: empty CSV');continue
    if any(len(x)!=len(rows[0]) for x in rows[1:]):errors.append(f'{p.name}: inconsistent CSV')
    with p.open() as f:
        for x in csv.DictReader(f):
            refs=x.get('source_ids',x.get('source_id',''))
            for ref in refs.split(';'):
                if ref and ref!='USER' and ref not in ids:errors.append(f'{p.name}: unknown {ref}')
manifest=root/'episodes/EP001/ASSET_MANIFEST.csv'
checked=0;not_local=0
if manifest.exists():
    for row in csv.DictReader(manifest.open()):
        p=root/row['local_path']
        if not p.exists():not_local+=1;continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Hash mismatch: '+row['local_path'])
        checked+=1
if errors:raise SystemExit('\n'.join(errors))
print(f'OK: {len(list(root.rglob("*.md")))} Markdown files; local links, unique source IDs and CSV shapes valid. {checked} local asset hashes verified; {not_local} assets not in this checkout.')
