import json, base64, io, sys, colorsys
from PIL import Image
# id -> (file, outdoor sky?)
PICK = json.loads(sys.argv[1])
SKY = {'forest': True, 'crypt': False, 'garden': True, 'courtyard': True, 'cave': False, 'rooftops': True}
sheets, scenes = {}, {}
FLOOR = {'forest': 125, 'crypt': 107, 'garden': 120, 'courtyard': 122, 'cave': 120, 'rooftops': 124}   # image row where the walkable floor starts
TARGET = 398   # screen y the floor should start at, just above the top lane
def hx(c): return int('%02x%02x%02x' % tuple(int(v) for v in c[:3]), 16)
def shade(c, f): return tuple(max(0, min(255, v * f)) for v in c[:3])
for k, f in PICK.items():
    im = Image.open(f).convert('RGBA')
    bio = io.BytesIO(); im.save(bio, 'PNG', optimize=True)
    sheets['scene-' + k] = {'url': 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode(), 'image': True}
    # the drawn ground band starts at image row (432+40)/4 = 118; continue the picture's own floor color there
    shift = max(0, -40 + 4 * FLOOR[k] - TARGET)
    r0 = min(im.height - 6, (432 + 40 + shift) // 4)   # image row that meets the drawn ground band
    row = [im.getpixel((x, y)) for y in range(r0, r0 + 6) for x in range(0, im.width, 2)]
    row.sort(key=lambda c: sum(c[:3])); mid = row[len(row) // 2]
    top = shade(mid, 0.8); bot = shade(mid, 0.35)
    scenes[k] = {'img': 'scene-' + k, 'sky': SKY[k], 'shift': shift, 'ground': [hx(top), hx(bot)],
                 'tuft': [hx(shade(mid, 1.05)), hx(shade(mid, 0.9)), hx(shade(mid, 0.6))]}
js = 'Object.assign(window.VH_SHEETS = window.VH_SHEETS || {}, ' + json.dumps(sheets) + ');\nwindow.VH_SCENES = ' + json.dumps(scenes) + ';\n'
open('vh2/scenes.js', 'w').write(js); print(json.dumps(scenes), len(js))
