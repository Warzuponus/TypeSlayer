import pl, json, time, zipfile, io, urllib.request, base64, os
STYLE = ", cartoony kid-friendly, silly not scary, bright colors, chunky pixel art"
FOES = {
 # name: (size, description, [(anim, action, frame_count)])
 'wolf':   (96, "little werewolf pup standing on two legs, shaggy grey-brown fur, big pointy ears, oversized paws, torn purple vest, glowing yellow eyes, goofy toothy grin",
            [('run', 'running forward fast on two legs, arms pumping, ears flapping', 8)]),
 'mummy':  (96, "little mummy wrapped in loose cream bandages with trailing ends, one big glowing green eye peeking out, stubby arms stretched forward, clumsy",
            [('walk', 'shambling forward slowly with arms stretched out in front, stiff wobbly steps', 8)]),
 'shield': (96, "vampire guard carrying a big round wooden shield with a silver bat emblem held in front, pale lavender skin, red hooded cape, small fangs, determined frown",
            [('walk', 'walking forward steadily holding the round shield up in front', 8)]),
 'batqueen': (128, "giant bat queen boss, tall purple bat lady with huge leathery wings folded like a cape, small golden crown, big pointed ears, glowing pink eyes, small fangs, regal and theatrical",
            [('walk', 'walking forward regally, wings swaying like a cape', 8), ('cast', 'spreads her huge wings wide and screeches to call bats', 8)]),
 'werewolf': (128, "big werewolf boss named Grizzlefang standing on two legs, huge shaggy dark grey fur, broad chest, torn red flannel shirt, big claws, glowing yellow eyes, toothy grin",
            [('walk', 'stomping forward on two legs, shoulders rolling', 8), ('cast', 'throws head back and howls at the moon with arms spread wide', 8)]),
 'pharaoh': (128, "mummy pharaoh boss, tall, wrapped in cream bandages, golden striped pharaoh headdress, wide golden collar, one glowing green eye, holding a golden staff",
            [('walk', 'shuffling forward slowly holding the golden staff', 8), ('cast', 'raises the golden staff high over the head with glowing green magic', 8)]),
 'ghostknight': (128, "ghost knight boss, glowing pale blue see-through armored knight, tall plumed helmet, dark visor with two glowing white eyes, ghostly sword, tattered blue cape",
            [('walk', 'marching forward with the sword held ready', 8), ('cast', 'raises the sword high and swirls into ghostly mist', 8)]),
 'mutant': (128, "giant mutant vampire boss, huge hulking muscular body, bright toxic green skin with purple spots, tiny bat wings, tattered purple cape, oversized fangs, three glowing red eyes, goofy grumpy frown, dripping green goo",
            [('walk', 'lumbering forward with heavy stomping steps, big arms swinging', 8), ('cast', 'pounds its chest with both fists and roars', 8)]),
}
os.makedirs('foes', exist_ok=True)
state = json.load(open('foes/state.json')) if os.path.exists('foes/state.json') else {}
def save(): json.dump(state, open('foes/state.json', 'w'), indent=1)
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)
jobs = []
for i, (k, (size, d, anims)) in enumerate(FOES.items()):
    if k in state: continue
    r = pl.req('POST', '/create-character-v3', {'description': d + STYLE, 'name': 'foe-' + k, 'image_size': {'width': size, 'height': size}, 'view': 'side', 'seed': 900 + i, 'no_background': True, 'outline': 'single color black outline', 'detail': 'medium detail'})
    state[k] = {'id': r['character_id']}; jobs.append((k, r['background_job_id'])); save()
for k, j in jobs:
    s = pl.wait(j); log('char', k, s['status'])
import urllib.error
for k, (size, d, anims) in FOES.items():
    st = state[k]
    for name, act, n in anims:
        if st.get('sub_' + name): continue
        while True:
            try:
                r = pl.req('POST', '/characters/animations', {'character_id': st['id'], 'animation_name': name, 'action_description': act, 'mode': 'v3', 'directions': ['west'], 'frame_count': n})
                break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
                time.sleep(20)
        st['sub_' + name] = r['background_job_ids']; save(); log('submitted', k, name)
# wait until every character's zip is ready
for k in FOES:
    while True:
        rq = urllib.request.Request(f"https://api.pixellab.ai/v2/characters/{state[k]['id']}/zip", headers={'Authorization': 'Bearer dummy'})
        try:
            data = urllib.request.urlopen(rq).read(); break
        except urllib.error.HTTPError as e:
            if e.code != 423: raise
            time.sleep(15)
    zipfile.ZipFile(io.BytesIO(data)).extractall(f'foes/{k}')
    log('downloaded', k)
# ghost and big bat: single images, animated with tweens in game
IMGS = {
 'ghost': ("small floating ghost with a little vampire cape and high collar, pale blue glowing body with a wispy tail instead of legs, big round eyes, tiny fangs, cheeky smile, facing left, side view", 80, 80),
}
for i, (k, (d, w, h)) in enumerate(IMGS.items()):
    f = f'foes/{k}.png'
    if os.path.exists(f): continue
    r = pl.req('POST', '/create-image-pixflux-background', {'description': d + ', game character sprite, cartoony kid-friendly, bright colors, chunky pixel art, black outline', 'image_size': {'width': w, 'height': h}, 'view': 'side', 'seed': 950 + i, 'no_background': True, 'outline': 'single color black outline'})
    s = pl.wait(r['background_job_id']); log('img', k, s['status'])
    img = s['last_response']['image']; b = img['base64'] if isinstance(img, dict) else img
    if b.startswith('data:'): b = b.split(',', 1)[1]
    open(f, 'wb').write(base64.b64decode(b))
log('ALL DONE')
