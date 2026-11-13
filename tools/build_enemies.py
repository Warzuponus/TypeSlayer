# Packs the newer enemies and bosses (Pixellab character zips) into enemies.js.
# Usage: python3 build_enemies.py <folder with one sub-folder per foe, plus ghost.png> <out enemies.js> [art copy folder]
import glob, json, base64, io, os, sys, shutil
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
ART = sys.argv[3] if len(sys.argv) > 3 else None
ANIMS = {'wolf': ['run'], 'mummy': ['walk'], 'shield': ['walk'], 'batqueen': ['walk', 'cast'], 'werewolf': ['walk', 'cast'],
         'pharaoh': ['walk', 'cast'], 'ghostknight': ['walk', 'cast'], 'mutant': ['walk', 'cast']}
# Some animations were generated twice; these are the takes picked for the game (folder names in the zip).
PICK = {('batqueen', 'walk'): 'walk-e2e42a18', ('ghostknight', 'walk'): 'walk-ff02cb9f', ('mummy', 'walk'): 'walk-fe613b61',
        ('pharaoh', 'walk'): 'walk-dfa8fc35'}
sheets, foes, report = {}, {}, {}
def b64(img):
    bio = io.BytesIO(); img.save(bio, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()
def feet(img):
    a = img.getchannel('A'); x0, y0, x1, y1 = a.getbbox(); px = a.load()
    fy = y1 - max(3, (y1 - y0) * 12 // 100)
    xs = [x for y in range(fy, y1) for x in range(x0, x1) if px[x, y] > 40]
    return (min(xs) + max(xs)) / 2, y1, y1 - y0
for k, anims in ANIMS.items():
    base = os.path.join(SRC, k)
    if not os.path.isdir(base): print('missing', k); continue
    foes[k] = {}
    for anim in anims:
        fs = sorted(glob.glob(f'{base}/**/animations/{PICK.get((k, anim), anim)}/west/*.png', recursive=True))
        if not fs: print('no frames', k, anim); continue
        fl = [Image.open(f).convert('RGBA') for f in fs]
        size = fl[0].width
        strip = Image.new('RGBA', (size * len(fl), size))
        for i, f in enumerate(fl):
            if f.size != (size, size): f = f.resize((size, size), Image.NEAREST)
            strip.paste(f, (i * size, 0))
        key = f'{k}{anim.capitalize()}'
        sheets[key] = {'url': b64(strip), 'size': size}
        fx, fy, fh = feet(fl[0])
        foes[k][anim] = {'sheet': key, 'frames': len(fl), 'ox': round(fx / size, 4), 'oy': round(fy / size, 4), 'fh': fh}
        report[key] = dict(size=size, **foes[k][anim])
        if ART:
            os.makedirs(ART, exist_ok=True); strip.save(os.path.join(ART, f'{"boss" if anim == "cast" or k in ("batqueen","werewolf","pharaoh","ghostknight","mutant") else "enemy"}-{k}-{anim}.png'))
g = os.path.join(SRC, 'ghost.png')
if os.path.exists(g):
    im = Image.open(g).convert('RGBA'); bb = im.getbbox()
    if bb: im = im.crop(bb)
    sheets['ghostImg'] = {'url': b64(im), 'image': True}
    foes['ghost'] = {'img': 'ghostImg'}
    report['ghostImg'] = im.size
    if ART: im.save(os.path.join(ART, 'enemy-ghost.png'))
js = ('// Newer enemies and bosses (Pixellab), embedded as data URIs. Built by tools/build_enemies.py.\n'
      'Object.assign(window.VH_SHEETS = window.VH_SHEETS || {}, ' + json.dumps(sheets) + ');\nwindow.VH_FOES = ' + json.dumps(foes, indent=1) + ';\n')
open(OUT, 'w').write(js)
print(json.dumps(report, indent=1, default=str)); print('bytes', len(js))
