import pl, json, time, zipfile, io, urllib.request, base64, os, sys
STYLE = ", holding a crossbow pointed forward, cartoony kid-friendly, bright colors, chunky pixel art"
SKINS = {
 'ivy':      "young girl vampire hunter with a long red braid, green hooded cloak, leather vest, brown boots, freckles, confident grin",
 'grimsby':  "old grandpa vampire hunter with a huge white mustache, bald head, round spectacles, patched brown trench coat, tall boots, cheerful",
 'clank':    "small friendly robot vampire hunter, round copper body, glowing blue eyes, little antenna, rivets, stubby legs",
 'knight':   "young vampire hunter wearing a full shining steel suit of armor with a plumed helmet, red tabard with a gold cross emblem",
 'nightbat': "young vampire hunter in a glowing teal and violet bat-wing costume, big round teal goggles, pointed bat-wing hood with no mask, scalloped violet wing cape with teal glowing edges, silver gloves, playful, original character",
 'ninja':    "young ninja vampire hunter in a dark purple ninja outfit, red headband with long trailing tails, face mask, wrapped wrists",
 'ranger':   "young moonlight ranger vampire hunter in a silver hooded cloak, glowing blue goggles, navy tunic, crescent moon pin",
 'pirate':   "young pirate vampire hunter with a red bandana, eye patch, striped shirt, blue captain coat with gold buttons, big boots",
 'sunfire':  "legendary young champion vampire hunter in radiant golden and orange armor with a glowing sun emblem on the chest, flowing orange cape, golden aura, epic",
}
ANIMS = [('idle', 'standing ready holding crossbow, gentle breathing, slight sway', 4),
         ('shoot', 'raises crossbow, fires a bolt forward with a small recoil, then lowers it', 6),
         ('hurt', 'flinches backward after being hit, then recovers', 4)]
out = 'skins'; os.makedirs(out, exist_ok=True)
state = json.load(open('skins/state.json')) if os.path.exists('skins/state.json') else {}
def save(): json.dump(state, open('skins/state.json', 'w'), indent=1)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
# 1. characters
jobs = []
for i, (k, d) in enumerate(SKINS.items()):
    if k in state: continue
    r = pl.req('POST', '/create-character-v3', {'description': d + STYLE, 'name': 'skin-' + k, 'image_size': {'width': 96, 'height': 96}, 'view': 'side', 'seed': 520 + i, 'no_background': True, 'outline': 'single color black outline', 'detail': 'medium detail'})
    state[k] = {'id': r['character_id']}; jobs.append((k, r['background_job_id'])); save()
for k, j in jobs:
    s = pl.wait(j); log('char', k, s['status'], s.get('usage'))
# 2. animations
for k in SKINS:
    st = state[k]
    if st.get('anims'): continue
    js = []
    for name, act, n in ANIMS:
        r = pl.req('POST', '/characters/animations', {'character_id': st['id'], 'animation_name': name, 'action_description': act, 'mode': 'v3', 'directions': ['east'], 'frame_count': n})
        js += r['background_job_ids']
    for j in js:
        s = pl.wait(j); log('anim', k, s['status'], s.get('usage'))
    st['anims'] = True; save()
# 3. download
for k in SKINS:
    r = urllib.request.Request(f"https://api.pixellab.ai/v2/characters/{state[k]['id']}/zip", headers={'Authorization': 'Bearer dummy'})
    zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(r).read())).extractall(f'skins/{k}')
    log('downloaded', k)
# 4. bolts
BOLTS = {
 'silver': 'a sleek silver crossbow bolt with a glinting steel tip, flying to the right, side view',
 'fire':   'a flaming crossbow bolt wrapped in bright orange fire, flying to the right, side view',
 'ice':    'an icy blue crystal crossbow bolt trailing frost sparkles, flying to the right, side view',
 'garlic': 'a spinning white garlic bulb projectile with a little motion trail, flying to the right, side view',
 'holy':   'a glowing blue holy water splash orb projectile with droplets, flying to the right, side view',
 'sun':    'a short beam of golden sunlight shaped like an arrow, glowing, flying to the right, side view',
}
for i, (k, d) in enumerate(BOLTS.items()):
    f = f'skins/bolt-{k}.png'
    if os.path.exists(f): continue
    r = pl.req('POST', '/create-image-pixflux-background', {'description': d + ', game projectile, chunky pixel art, black outline', 'image_size': {'width': 64, 'height': 32}, 'view': 'side', 'seed': 700 + i, 'no_background': True, 'outline': 'single color black outline'})
    s = pl.wait(r['background_job_id']); log('bolt', k, s['status'], s.get('usage'))
    img = s['last_response']['image']; b = img['base64'] if isinstance(img, dict) else img
    if b.startswith('data:'): b = b.split(',', 1)[1]
    open(f, 'wb').write(base64.b64decode(b))
log('ALL DONE')
