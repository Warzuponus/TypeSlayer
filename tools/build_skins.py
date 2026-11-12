import glob, json, base64, io, os, sys
from PIL import Image
IDS = ['ivy','grimsby','clank','knight','nightbat','ninja','ranger','pirate','sunfire']
sheets, looks, report = {}, {}, {}
def b64(img):
    bio = io.BytesIO(); img.save(bio, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()
for k in IDS:
    base = f'pl/skins/{k}'
    if not os.path.isdir(base): print('missing', k); continue
    frames = {}
    for anim in ['idle','shoot','hurt']:
        fs = sorted(glob.glob(f'{base}/**/animations/{anim}*/east/*.png', recursive=True))
        if not fs: fs = sorted(glob.glob(f'{base}/**/animations/*{anim}*/east/*.png', recursive=True))
        frames[anim] = [Image.open(f).convert('RGBA') for f in fs]
    if not all(frames.values()): print('incomplete', k, {a: len(v) for a, v in frames.items()}); continue
    size = frames['idle'][0].width
    for anim, fl in frames.items():
        strip = Image.new('RGBA', (size * len(fl), size))
        for i, f in enumerate(fl):
            if f.size != (size, size): f = f.resize((size, size), Image.NEAREST)
            strip.paste(f, (i * size, 0))
        sheets[f'{k}{anim.capitalize()}'] = {'url': b64(strip), 'size': size}
    f0 = frames['idle'][0]; a = f0.getchannel('A'); bb = a.getbbox()
    x0, y0, x1, y1 = bb; px = a.load()
    # feet: center of opaque pixels in the bottom 12% of the figure
    fy = y1 - max(3, (y1 - y0) * 12 // 100)
    xs = [x for y in range(fy, y1) for x in range(x0, x1) if px[x, y] > 40]
    fx = (min(xs) + max(xs)) / 2
    # crossbow tip: rightmost opaque pixel in the upper-middle band
    by0, by1 = y0 + (y1 - y0) * 25 // 100, y0 + (y1 - y0) * 70 // 100
    best = None
    for y in range(by0, by1):
        for x in range(x1 - 1, x0 - 1, -1):
            if px[x, y] > 40:
                if best is None or x > best[0]: best = (x, y)
                break
    ox, oy = fx / size, y1 / size
    looks[k] = {'idle': f'{k}Idle', 'shoot': f'{k}Shoot', 'hurt': f'{k}Hurt', 'ox': round(ox, 4), 'oy': round(oy, 4),
                'tipX': round((best[0] - fx) * 2), 'tipY': round((best[1] - y1) * 2), 'shootStart': 2}
    report[k] = dict(size=size, n={a: len(v) for a, v in frames.items()}, bbox=bb, **looks[k])
for b in ['silver','fire','ice','garlic','holy','sun']:
    f = f'pl/skins/bolt-{b}.png'
    if os.path.exists(f):
        im = Image.open(f).convert('RGBA'); bb = im.getbbox()
        if bb: im = im.crop(bb)
        sheets[f'bolt-{b}'] = {'url': b64(im), 'image': True}
        report['bolt-' + b] = im.size
js = 'Object.assign(window.VH_SHEETS = window.VH_SHEETS || {}, ' + json.dumps(sheets) + ');\nwindow.VH_LOOKS = ' + json.dumps(looks, indent=1) + ';\n'
open('vh2/skins.js', 'w').write(js)
print(json.dumps(report, indent=1, default=str)); print('bytes', len(js))
