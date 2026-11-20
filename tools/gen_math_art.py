# Makes the Math Hunt art with Pixellab: two bosses, two settings, the map, and small icons.
# Usage: python3 tools/gen_math_art.py <work folder>   (then tools/build_math_art.py packs it into mathart.js)
import sys, os, json, time, base64, io, zipfile, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pl
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
STYLE = ", cartoony kid-friendly, silly not scary, bright colors, chunky pixel art"
BOSSES = {
 'beetle': (128, "Beetle Baron boss, a big round vampire beetle standing upright on two of its six legs, shiny dark green and purple shell like a cape, "
                 "tiny top hat, monocle, small fangs, four other stubby legs waving, big friendly eyes",
            [('walk', 'scuttling forward proudly on its back legs, shell wobbling, little legs waving', 8),
             ('cast', 'lifts all six legs up and spins its shell with green sparkles', 8)]),
 'weaver': (128, "Countess Weaver boss, a tall spider vampire lady, purple spider body with eight thin striped legs, pale lavender face, "
                 "tall black hair bun, red high-collar cape, small fangs, sly smile",
            [('walk', 'creeping forward gracefully on eight legs, cape swaying', 8),
             ('cast', 'rears up and throws a glowing silver web from her hands', 8)]),
}
SCENE_TAIL = (", wide side-scrolling game background, cartoony kid-friendly spooky not scary, chunky pixel art, deep purple and blue night palette, "
              "flat ground strip along the bottom quarter, no characters, no text")
SCENES = {
 'tower':  "inside a tall spooky spider tower at night, stone walls, giant silver cobwebs in the corners, tall arched windows with a full moon, candles, wooden floor",
 'castle': "great hall of a vampire castle at night, tall red curtains, stained glass windows, golden candelabras, checkered stone floor, a big throne far away",
}
MAP = ("top-down fantasy treasure map of a spooky kid-friendly vampire land at night, dark blue and purple, small graveyard, garden, cave, forest, crypt, "
       "castle on a hill, little trees and hills, no text, no path, chunky pixel art")
ICONS = {   # name: (size, description)
 'bat':     (48, "cute small purple bat with wings spread, big eyes, front view, game icon"),
 'garlic':  (48, "cute white garlic bulb, game icon"),
 'pumpkin': (48, "cute small orange jack-o-lantern pumpkin with a friendly smile, game icon"),
 'coin':    (48, "shiny gold coin with a bat emblem, game icon"),
 'lock':    (48, "old iron padlock, game icon"),
 'stamp':   (64, "round gold mastery medal stamp with a star in the middle and a red ribbon, game icon"),
}
state_f = os.path.join(OUT, 'state.json')
state = json.load(open(state_f)) if os.path.exists(state_f) else {}
save = lambda: json.dump(state, open(state_f, 'w'), indent=1)

def image(path, desc, w, h, seed, nobg):
    if os.path.exists(path): return
    r = pl.req('POST', '/create-image-pixflux-background', {'description': desc, 'image_size': {'width': w, 'height': h}, 'view': 'side',
                                                            'seed': seed, 'no_background': nobg, 'outline': 'single color black outline'})
    s = pl.wait(r['background_job_id']); log('img', os.path.basename(path), s['status'])
    img = s['last_response']['image']; b = img['base64'] if isinstance(img, dict) else img
    if b.startswith('data:'): b = b.split(',', 1)[1]
    open(path, 'wb').write(base64.b64decode(b))

# 1. boss characters
jobs = []
for i, (k, (size, d, anims)) in enumerate(BOSSES.items()):
    if k in state: continue
    r = pl.req('POST', '/create-character-v3', {'description': d + STYLE, 'name': 'math-' + k, 'image_size': {'width': size, 'height': size}, 'view': 'side',
                                                'seed': 1200 + i, 'no_background': True, 'outline': 'single color black outline', 'detail': 'medium detail'})
    state[k] = {'id': r['character_id']}; jobs.append(r['background_job_id']); save(); log('character', k)
for j in jobs: log('char done', pl.wait(j).get('status'))
for k, (size, d, anims) in BOSSES.items():
    for name, act, n in anims:
        if state[k].get('sub_' + name): continue
        while True:
            try:
                r = pl.req('POST', '/characters/animations', {'character_id': state[k]['id'], 'animation_name': name, 'action_description': act,
                                                              'mode': 'v3', 'directions': ['west'], 'frame_count': n}); break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
                time.sleep(20)
        state[k]['sub_' + name] = r['background_job_ids']; save(); log('animation', k, name)

# 2. settings, map and icons while the animations run
for i, (k, d) in enumerate(SCENES.items()):
    image(os.path.join(OUT, f'scene-{k}.png'), d + SCENE_TAIL, 320, 140, 31 + i, False)
image(os.path.join(OUT, 'map.png'), MAP, 320, 140, 77, False)
for i, (k, (s, d)) in enumerate(ICONS.items()):
    image(os.path.join(OUT, f'icon-{k}.png'), d + ', cartoony kid-friendly, bright colors, chunky pixel art, black outline', s, s, 300 + i, True)

# 3. download the boss zips once every animation is done
for k in BOSSES:
    while True:
        rq = urllib.request.Request(f"{pl.BASE}/characters/{state[k]['id']}/zip", headers={'Authorization': 'Bearer dummy'})
        try:
            data = urllib.request.urlopen(rq).read(); break
        except urllib.error.HTTPError as e:
            if e.code != 423: raise
            time.sleep(15)
    zipfile.ZipFile(io.BytesIO(data)).extractall(os.path.join(OUT, k)); log('downloaded', k)
log('ALL DONE')
