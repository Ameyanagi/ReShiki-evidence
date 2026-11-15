import json, sys, copy
src = json.load(open(sys.argv[1]))
xs = [a['position']['x'] for a in src['atoms']] + [a['position']['x'] for a in src['annotations']]
ys = [a['position']['y'] for a in src['atoms']] + [a['position']['y'] for a in src['annotations']]
w, h = max(xs) - min(xs) + 400, max(ys) - min(ys) + 400
out = copy.deepcopy(src)
for k in ['atoms', 'bonds', 'annotations', 'arrows', 'abbreviations']:
    out[k] = []
def mv(p, dx, dy): return {'x': p['x'] + dx, 'y': p['y'] + dy}
for n in range(64):
    dx, dy, o = (n % 8) * w, (n // 8) * h, n * 1000
    for a in src['atoms']:
        a = copy.deepcopy(a); a['id'] += o; a['position'] = mv(a['position'], dx, dy)
        if a.get('centroid'): a['centroid'] = [i + o for i in a['centroid']]
        out['atoms'].append(a)
    for b in src['bonds']:
        b = copy.deepcopy(b); b['a'] += o; b['b'] += o; out['bonds'].append(b)
    for t in src['annotations']:
        t = copy.deepcopy(t); t['id'] += o; t['position'] = mv(t['position'], dx, dy); out['annotations'].append(t)
    for r in src['arrows']:
        r = copy.deepcopy(r); r['id'] += o; r['start'] = mv(r['start'], dx, dy); r['end'] = mv(r['end'], dx, dy); out['arrows'].append(r)
    for ab in src['abbreviations']:
        ab = copy.deepcopy(ab); ab['anchor'] += o; ab['members'] = [i + o for i in ab['members']]; out['abbreviations'].append(ab)
json.dump(out, open(sys.argv[2], 'w'))
print(len(out['atoms']), len(out['bonds']), len(out['annotations']))
