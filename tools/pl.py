import json, sys, time, urllib.request, base64, os
BASE='https://api.pixellab.ai/v2'
def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE+path, data=data, method=method, headers={'Content-Type':'application/json','Authorization':'Bearer dummy'})
    try:
        with urllib.request.urlopen(r, timeout=120) as resp: return json.loads(resp.read() or b'{}')
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, e.read()[:800].decode(errors='replace')); raise
def wait(job):
    for i in range(120):
        s = req('GET', f'/background-jobs/{job}')
        st = s.get('status')
        if st in ('completed','failed','error','cancelled'): return s
        time.sleep(5)
    return s
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'create':
        name, desc, size, seed = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        r = req('POST','/create-character-v3', {'description':desc,'name':name,'image_size':{'width':size,'height':size},'view':'side','seed':seed,'no_background':True,'outline':'single color black outline','detail':'medium detail'})
        print(json.dumps(r)[:600])
