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
- **Skips the warm-up once it's mastered.** In the four row modes, waves 1 to 4 teach the keys a pair at a time and wave 5 uses the whole row. Clearing wave 5 with 90% accuracy or better in two real hunts masters the warm-up, and from then on that hunter's hunts in that mode start at wave 5. A rough round there (under 75%) takes one clean clear back, so a rusty hunter goes back to wave 1. Practice never counts, always starts at wave 1, and grown-ups can still use ← → on the first wave screen to pick any wave. Saves that already got past wave 5 count as mastered.
- **Extra practice on weak keys.** It tracks a miss rate and speed for every key and serves the weak ones more often.
- **No peeking.** The on-screen keyboard is covered in the real game, so kids learn where the keys are by feel.
- **Practice mode** (press P on the hunt menu) shows the keyboard with finger colors and the next key lit up. It is always blue and earns nothing: no points, coins, unlocks, daily hunt time or best scores, and it doesn't change the weak-key stats.
- **Capitals toggle.** Shift is required and coins pay 1.5x.
- **Profiles** for each kid, saved in the browser on that device.
- **Daily 20-minute hunt** with a reward.
- **Lots of enemies.** Fledglings, armored vampires, ghouls and bats, plus wolf pups (fast), little mummies (slow), see-through ghosts that drift in bursts, shield guards (type the shield word, then theirs) and giant bats that split into two letter bats.
- **A boss for each setting**, each with a queue of words and its own trick:
  - Count Moonfang (graveyard, garden, rooftops) pauses to cast and gets knocked back.
  - Queen Vespera the Bat Queen (cave) calls in bats carrying single letters.
  - Grizzlefang the werewolf (forest) howls and charges every few seconds.
  - Pharaoh Mumbles (crypt) has extra words and calls in little mummies.
  - The Ghost Knight (courtyard) vanishes and pops up in another lane.
- **Wrong keys count.** Each wrong key costs 5 points, and the HUD shows two meters:
  - 4 wrong keys in a row jam the crossbow for 3 seconds. Keys do nothing until it's fixed.
  - 15 wrong keys in one wave bring the **Mega Mutant** at the end of the wave. It needs 2 whole sentences (or 3 phrases made only of that wave's keys) and gives no points or coins.
  - Practice mode never jams and never brings the Mutant. It shows a reminder instead.
- **Shop** with 4 hunters, 6 outfits and 7 bolts, bought with coins earned in play.
  - Some items unlock through achievements.
  - The ultimate Sunfire Champion outfit is for beating every mode with Capitals on.
- **Seven settings, each with its own battle track.** The screen fades between waves into a new one.

## Math Hunt

Press **M** on the hunt menu. Each enemy carries a times-table problem like `7 × 8 = ?`. Typing the answer fires the crossbow as soon as the number matches, with no Enter needed. The crossbow always aims at the enemy closest to the hunter. Math Hunt uses the same hunters, coins, shop and daily 20-minute hunt.

- **Every fact is tracked.** A fact and its turnaround (7 × 8 and 8 × 7) count as one. Each fact sits on one of five levels:

  | Level | How a fact gets there | Comes back |
  | --- | --- | --- |
  | New | Not taught yet | |
  | Learning | Just taught, missed, or right but slower than 6 seconds | The same hunt |
  | Known | Right within 6 seconds | Next day |
  | Fluent | Right within 3 seconds | In 3 days |
  | Mastered | Fluent on 3 different days | In a week, then 3 weeks |

- **A scouting round the first time.** It asks 18 facts from every table, easy to hard. Scouts never bite. A quick right answer marks a fact as already Fluent, and getting both the ×1 and ×10 facts right marks those whole tables as Known. Four misses in a row end it early.
- **One hunt** is a warm-up of known facts, two learning waves and a review wave of facts due from other days, with the place's boss at the end. Then there are bonus waves for as long as the hunter lasts.
- **New facts come 2 at a time** on a card that shows them as rows of dots. The hunter types each answer once. The ×1 and ×10 tables are taught as rules. No new facts are added while 4 or more are still being learned.
- **Mistakes are re-taught.** A wrong answer shows the right one on the enemy for a second, then it is typed again. The same fact comes back 2 enemies later. SPACE means "I don't know" and shows the answer. 3 wrong answers in a row jam the crossbow.
- **Slow mummies carry facts being learned, and fast wolf pups carry fluent ones.**
- **Three places so far:** the Graveyard (×1, ×10 and ×2), the Garden (×5) and the Bat Cave (×4). Each place opens when 80% of the one before it is Known. Smart Hunt (SPACE on the math menu) picks the place to work on.
- **A daily math goal** of 60 facts answered right is worth 50 coins.

The fact engine is in `math.js` with no game code in it, so it can be checked with `node tools/test_math.js`. Math progress is saved in each profile under `math`.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The whole game (Phaser 3.80.1 from cdnjs) |
| `assets.js` | Enemy, boss, original hunter and graveyard sprite sheets, embedded as data URIs |
| `enemies.js` | The newer enemies and bosses (wolf pup, mummy, shield guard, ghost, the four setting bosses and the Mega Mutant) |
| `skins.js` | Hunter and outfit sheets, bolt images and their crossbow and feet offsets |
| `scenes.js` | The six newer settings and their ground colors |
| `math.js` | The Math Hunt fact engine: levels, review schedule, places, lessons and fact picking |
| `music/` | The game's music (Suno), 128 kbps MP3, loops trimmed on the beat. `tracks.json` has the exact lengths |
| `art/` | Source PNGs from Pixellab, plus `pixellab-character-ids.json` for regenerating or adding animations |
| `tools/` | The Python scripts used to call the Pixellab API and pack the art into the `.js` files, plus `test_math.js` for the fact engine |

Saves live in `localStorage` under `vh-save-v1`.

See [ROADMAP.md](ROADMAP.md) for what's next.
