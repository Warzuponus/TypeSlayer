# Packs the Math Hunt art made by gen_math_art.py into mathart.js (data URIs), plus copies in art/math/.
# Usage: python3 tools/build_math_art.py <work folder> <out mathart.js> [art copy folder]
import glob, json, base64, io, os, sys
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
ART = sys.argv[3] if len(sys.argv) > 3 else None
if ART: os.makedirs(ART, exist_ok=True)
sheets, foes, scenes, icons = {}, {}, {}, {}
def b64(img):
    bio = io.BytesIO(); img.save(bio, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()
def feet(img):
    a = img.getchannel('A'); x0, y0, x1, y1 = a.getbbox(); px = a.load()
    fy = y1 - max(3, (y1 - y0) * 12 // 100)
    xs = [x for y in range(fy, y1) for x in range(x0, x1) if px[x, y] > 40]
    return (min(xs) + max(xs)) / 2, y1, y1 - y0
# bosses: one strip per animation, facing west (toward the hunter)
PICK = json.loads(os.environ.get('PICK', '{}'))   # {"beetle/walk": "walk-1234abcd"} when an animation was made twice
for k in ('beetle', 'weaver'):
    base = os.path.join(SRC, k)
    if not os.path.isdir(base): print('missing', k); continue
    foes[k] = {}
    for anim in ('walk', 'cast'):
        folder = PICK.get(f'{k}/{anim}', anim)
        fs = sorted(glob.glob(f'{base}/**/animations/{folder}*/west/*.png', recursive=True))
        if not fs: print('no frames', k, anim); continue
        fl = [Image.open(f).convert('RGBA') for f in fs]
        size = fl[0].width
        strip = Image.new('RGBA', (size * len(fl), size))
        for i, f in enumerate(fl): strip.paste(f.resize((size, size), Image.NEAREST) if f.size != (size, size) else f, (i * size, 0))
        key = f'{k}{anim.capitalize()}'
        sheets[key] = {'url': b64(strip), 'size': size}
        fx, fy, fh = feet(fl[0])
        foes[k][anim] = {'sheet': key, 'frames': len(fl), 'ox': round(fx / size, 4), 'oy': round(fy / size, 4), 'fh': fh}
        if ART: strip.save(os.path.join(ART, f'boss-{k}-{anim}.png'))
# settings: same layout rules as tools/build_scenes.py
FLOOR = {'tower': 119, 'castle': 106}   # image row where the walkable floor starts
SKY = {'tower': False, 'castle': False}
TARGET = 398
def hx(c): return int('%02x%02x%02x' % tuple(int(v) for v in c[:3]), 16)
def shade(c, f): return tuple(max(0, min(255, v * f)) for v in c[:3])
for k in FLOOR:
    f = os.path.join(SRC, f'scene-{k}.png')
    if not os.path.exists(f): print('missing scene', k); continue
    im = Image.open(f).convert('RGBA')
    sheets['scene-' + k] = {'url': b64(im), 'image': True}
    shift = max(0, -40 + 4 * FLOOR[k] - TARGET)
    r0 = min(im.height - 6, (432 + 40 + shift) // 4)
    row = sorted([im.getpixel((x, y)) for y in range(r0, r0 + 6) for x in range(0, im.width, 2)], key=lambda c: sum(c[:3]))
    mid = row[len(row) // 2]
    scenes[k] = {'img': 'scene-' + k, 'sky': SKY[k], 'shift': shift, 'ground': [hx(shade(mid, 0.8)), hx(shade(mid, 0.35))],
                 'tuft': [hx(shade(mid, 1.05)), hx(shade(mid, 0.9)), hx(shade(mid, 0.6))]}
    if ART: im.save(os.path.join(ART, f'scene-{k}.png'))
# the map and the small icons
m = os.path.join(SRC, 'map.png')
if os.path.exists(m):
    im = Image.open(m).convert('RGBA'); sheets['mathMap'] = {'url': b64(im), 'image': True}
    if ART: im.save(os.path.join(ART, 'map.png'))
for f in sorted(glob.glob(os.path.join(SRC, 'icon-*.png'))):
    k = os.path.basename(f)[5:-4]
    im = Image.open(f).convert('RGBA'); bb = im.getbbox()
    if bb: im = im.crop(bb)
    sheets['icon-' + k] = {'url': b64(im), 'image': True}; icons[k] = 'icon-' + k
    if ART: im.save(os.path.join(ART, f'icon-{k}.png'))
js = ('// Math Hunt art (Pixellab): the Beetle Baron and Countess Weaver, the Spider Tower and Castle settings, the map and icons.\n'
      '// Embedded as data URIs. Built by tools/build_math_art.py.\n'
      'Object.assign(window.VH_SHEETS = window.VH_SHEETS || {}, ' + json.dumps(sheets) + ');\n'
      'Object.assign(window.VH_FOES = window.VH_FOES || {}, ' + json.dumps(foes) + ');\n'
      'Object.assign(window.VH_SCENES = window.VH_SCENES || {}, ' + json.dumps(scenes) + ');\n'
      'window.VH_MATH_ICONS = ' + json.dumps(icons) + ';\n')
open(OUT, 'w').write(js)
print(json.dumps({'foes': foes, 'scenes': scenes, 'icons': icons}, indent=1)); print('bytes', len(js))
