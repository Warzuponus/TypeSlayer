import pl, base64, sys, time
TAIL = ", wide side-scrolling game background, cartoony kid-friendly spooky not scary, chunky pixel art, deep purple and blue night palette, flat ground strip along the bottom quarter, no characters, no text"
SC = {
 'forest':    "haunted forest at night, tall twisted dark trees, glowing blue mushrooms, fireflies, full moon peeking through branches, mossy grass",
 'crypt':     "underground stone crypt hall, round stone arches, wall torches with warm orange flames, cobwebs, old coffins along the wall, stone floor",
 'garden':    "moonlit castle garden terrace, stone balustrade, trimmed hedges, rose bushes, glowing lanterns, huge full moon, starry sky",
 'courtyard': "castle courtyard at night, tall stone walls with red banners, burning torches, big iron gate, cobblestone ground, starry sky",
 'cave':      "spooky cave with glowing purple and teal crystals, hanging stalactites, small bat silhouettes, rocky cave floor",
 'rooftops':  "old village rooftops at night, tiled roofs, crooked chimneys, houses with warm lit windows, huge full moon, starry sky",
}
seeds = [int(a) for a in sys.argv[1:]] or [31]
for seed in seeds:
  for k, d in SC.items():
    f = f'scenes/{k}-{seed}.png'
    r = pl.req('POST', '/create-image-pixflux-background', {'description': d + TAIL, 'image_size': {'width': 320, 'height': 140}, 'view': 'side', 'seed': seed, 'no_background': False, 'outline': 'single color black outline'})
    s = pl.wait(r['background_job_id']); print(time.strftime('%H:%M:%S'), k, seed, s['status'], flush=True)
    img = s['last_response']['image']; b = img['base64'] if isinstance(img, dict) else img
    if b.startswith('data:'): b = b.split(',', 1)[1]
    open(f, 'wb').write(base64.b64decode(b))
print('SCENES DONE')
