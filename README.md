# TypeSlayer the Vampire Hunter

A browser typing game for kids aged 8 to 11. Cartoon vampires walk toward the hunter carrying letters or words, and typing them fires the crossbow. The goal is fast touch typing without looking at the keys.

It plays in any modern browser on a desktop, or on an iPad with a hardware keyboard.

## Play

Open `index.html` through any static web server, for example:

```
python3 -m http.server 8000
```

Then visit http://localhost:8000. Opening the file directly with `file://` blocks the music from loading. The game still plays, but without music.

GitHub Pages works as is: serve the repository root from the default branch.

## What's in it

- **Five modes:** home row, top row, bottom row, numbers and symbols, and all keys. Each one goes from single letters to full words.
- **Adaptive pace.** It speeds up when vampires are stopped far away and slows down after a bite.
- **Extra practice on weak keys.** It tracks a miss rate and speed for every key and serves the weak ones more often.
- **No peeking.** The on-screen keyboard is covered in the real game, so kids learn where the keys are by feel.
- **Practice mode** (press P on the hunt menu) shows the keyboard with finger colors and the next key lit up. It is always blue and earns nothing: no points, coins, unlocks, daily hunt time or best scores, and it doesn't change the weak-key stats.
- **Capitals toggle.** Shift is required and coins pay 1.5x.
- **Profiles** for each kid, saved in the browser on that device.
- **Daily 20-minute hunt** with a reward.
- **Count Moonfang**, a boss with a queue of words.
- **Shop** with 4 hunters, 6 outfits and 7 bolts, bought with coins earned in play.
  - Some items unlock through achievements.
  - The ultimate Sunfire Champion outfit is for beating every mode with Capitals on.
- **Seven settings, each with its own battle track.** The screen fades between waves into a new one.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The whole game (Phaser 3.80.1 from cdnjs) |
| `assets.js` | Enemy, boss, original hunter and graveyard sprite sheets, embedded as data URIs |
| `skins.js` | Hunter and outfit sheets, bolt images and their crossbow and feet offsets |
| `scenes.js` | The six newer settings and their ground colors |
| `music/` | The game's music (Suno), 128 kbps MP3, loops trimmed on the beat. `tracks.json` has the exact lengths |
| `art/` | Source PNGs from Pixellab, plus `pixellab-character-ids.json` for regenerating or adding animations |
| `tools/` | The Python scripts used to call the Pixellab API and pack the art into the `.js` files |

Saves live in `localStorage` under `vh-save-v1`.

See [ROADMAP.md](ROADMAP.md) for what's next.
