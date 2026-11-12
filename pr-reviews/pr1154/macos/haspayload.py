# python3 -I haspayload.py <files...>: report whether each file carries a ReShiki drawing payload.
import sys, re, base64, struct, zlib, hashlib, json
def png(b):
    if not b.startswith(b'\x89PNG\r\n\x1a\n'): return None
    i = 8
    while i + 8 <= len(b):
        n, t = struct.unpack('>I4s', b[i:i+8]); d = b[i+8:i+8+n]
        if t == b'iTXt' and d.startswith(b'dev.reshiki.drawing\0'):
            parts = d.split(b'\0', 4)
            return parts[4] if len(parts) == 5 else d
        if t == b'IEND': break
        i += 12 + n
    return b''
def text(b):
    m = re.search(rb'<reshiki:drawing[^>]*>([A-Za-z0-9+/=\s]+)</reshiki:drawing>', b)
    return m.group(1) if m else b''
def check(b64):
    env = base64.b64decode(b64)
    if env[:4] != b'RSKD': return 'bad magic'
    ver = env[4]; n = struct.unpack('<I', env[5:9])[0]; h = env[9:41]
    try: js = zlib.decompress(env[41:], -15)
    except Exception:
        js = zlib.decompress(env[41:])
    ok = len(js) == n and hashlib.sha256(js).digest() == h
    d = json.loads(js)
    return f"v{ver} json={n}B env={len(env)}B hash={'ok' if ok else 'BAD'} atoms={len(d.get('atoms',[]))} bonds={len(d.get('bonds',[]))}"
for f in sys.argv[1:]:
    b = open(f, 'rb').read()
    p = png(b)
    if p is None: p = text(b)
    print(f"{f}: {len(b)}B payload={'none' if not p else check(p)}")
