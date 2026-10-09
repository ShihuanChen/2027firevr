import csv, os
base = os.path.dirname(os.path.abspath(__file__))
secs = {
    '2.1 Immersive Journalism (沉浸式新闻)': 'related work文献 - 2.1 immersive journalism.csv',
    '2.2 VR Storytelling & Embodiment (VR叙事与具身)': 'related work文献 - 2.2 VR storytelling.csv',
    '2.3 VR Simulation of Vulnerable Groups (弱势群体VR模拟)': 'related work文献 - 2.3 VR simulation vulnerable groups.csv',
}
cols = ['section', 'link', 'ref', 'title', 'venue', 'year', 'cite', 'abstract', 'content', 'pics', 'inspiration', '创新点']
rows = []
for sec, fn in secs.items():
    with open(os.path.join(base, fn), encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            r['section'] = sec
            rows.append(r)
out = os.path.join(base, 'related work文献_合并总表.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, '') for c in cols})
print('合并', len(rows), '篇 ->', os.path.basename(out))
