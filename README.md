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
- **Daily hunt** with a reward: 10 minutes of typing and 10 minutes of Math Hunt.
- **Lots of enemies.** Fledglings, armored vampires, ghouls and bats, plus wolf pups (fast), little mummies (slow), see-through ghosts that drift in bursts, shield guards (type the shield word, then theirs) and giant bats that split into two letter bats.
- **A boss for each setting**, each with a queue of words and its own trick (Math Hunt adds three more, below):
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

Press **M** on the hunt menu. Each enemy carries a times-table problem like `7 × 8 = ?`. Typing the answer fires the crossbow as soon as the number matches, with no Enter needed. The crossbow always aims at the enemy closest to the hunter. Math Hunt uses the same hunters, coins and shop. It has its own 10-minute timer: a full daily hunt is 10 minutes of typing plus 10 minutes of Math Hunt.

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
- **New facts come 2 at a time** on a card that shows them as rows of little pictures (bats, pumpkins, garlic or coins). The hunter types each answer once. The ×1 and ×10 tables are taught as rules. No new facts are added while 4 or more are still being learned.
- **Mistakes are re-taught.** A wrong answer shows the right one on the enemy for a second, then it is typed again. The same fact comes back 2 enemies later. SPACE means "I don't know" and shows the answer. 3 wrong answers in a row jam the crossbow.
- **Every enemy has a math job:**
  - Slow mummies carry facts being learned, and fast wolf pups carry fluent ones.
  - Armored vampires carry the harder facts of the place you are in.
  - Shield guards need two answers: the fact breaks the shield, then its turnaround (7 × 8, then 8 × 7). Only the first one counts.
  - Ghosts hide a number: `? × 6 = 42`. They only carry fluent facts, and get a little more time.
  - The Bat Queen's bats carry quick ×1 and ×10 facts.
- **Hint pictures.** A fact missed twice in a hunt shows its rows of dots and a strategy ("Double 7, then one more 7: 14 + 7") the next time it comes. Grown-ups can turn this off.
- **The Mega Mutant** comes at the end of a wave with 8 wrong answers, carrying exactly the facts that were missed.
- **Nine places on a map:**

  | # | Place | New facts | Boss |
  | --- | --- | --- | --- |
  | 1 | Graveyard | ×1, ×10 and ×2 (27) | Count Moonfang |
  | 2 | Garden | ×5 (7) | Count Moonfang |
  | 3 | Bat Cave | ×4 (6) | Queen Vespera |
  | 4 | Dark Forest | ×3 (5) | Grizzlefang |
  | 5 | Crypt | ×9 (4) | Pharaoh Mumbles |
  | 6 | Courtyard | ×6 (3) | The Beetle Baron, who spins in his shell and bounces back |
  | 7 | Rooftops | ×7 (2) | The Ghost Knight |
  | 8 | Spider Tower | ×8 (1) | Countess Weaver, who drops into another lane |
  | 9 | Castle | All 55 mixed | Count Moonfang returns, bigger and glowing, with 10 facts |

  Every table finished makes the next one smaller, so the ×8 place only adds 8 × 8. Each place opens when 80% of the one before it is Known. Its ring on the map fills as facts become Known, and it gets a **gold stamp** when every fact in it is Mastered. Smart Hunt (SPACE on the math menu) picks the place to work on, and 1 to 9 pick one.
- **Its own music:** the math menu plays Times Table Tick-Tock, the Spider Tower and the Castle have their own battle loops, Count Moonfang returns with his own boss song, and a gold stamp plays the Table Mastered fanfare.
- **Mixed Review** (R) is endless waves of every fact met so far, a little faster each wave, with a boss every other wave. It opens after the first hunt.
- **Math practice** (P) is blue like typing practice: every enemy shows its hint picture, nobody bites, and nothing counts.
- **A daily math goal** of 60 facts answered right (grown-ups can change it) is worth 50 coins.

## Grown-ups page

Press **G** on the hunter screen. The first time, it asks for a 4-digit PIN, which is the same for every hunter on the device. (If it is forgotten, "Forgot the PIN?" asks a grown-up question, 14 × 16, and then lets you set a new one.) For each hunter it shows:

- How many of the 55 facts are Known, Fluent and Mastered, the day streak, and how many of the last 14 days hit the math goal.
- A 10 × 10 grid of every fact colored by level. Tap a square for its accuracy, average time, when it was last seen, when it comes back and a strategy.
- The 5 facts to watch, each with a tip, and which places are open, Mastered and have had their boss beaten.
- Getting faster: the average answer time per table for each of the last 4 weeks, with the 3-second line marked.
- A practice log of typing and math minutes for the last 14 days, with the daily hunt and math goal days marked.
- The typing key heat map, best speed and accuracy, and the best wave in each typing mode.
- Settings: the daily math goal, a cap on math minutes per day, how fast math enemies walk, hint pictures on or off, and changing the PIN.
- **Copy report** puts a short text summary on the clipboard to paste into a message to a teacher.

Everything stays in the browser on that device.

The fact engine is in `math.js` with no game code in it, so it can be checked with `node tools/test_math.js`. Math progress is saved in each profile under `math`.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The whole game (Phaser 3.80.1 from cdnjs) |
| `assets.js` | Enemy, boss, original hunter and graveyard sprite sheets, embedded as data URIs |
| `enemies.js` | The newer enemies and bosses (wolf pup, mummy, shield guard, ghost, the four setting bosses and the Mega Mutant) |
| `skins.js` | Hunter and outfit sheets, bolt images and their crossbow and feet offsets |
| `scenes.js` | The six newer settings and their ground colors |
| `math.js` | The Math Hunt fact engine: levels, review schedule, places, lessons, fact picking and hints |
| `mathart.js` | Math Hunt art: the Beetle Baron, Countess Weaver, the Spider Tower and Castle settings, the map and icons (copies in `art/math/`, made with `tools/gen_math_art.py` and `tools/build_math_art.py`) |
| `music/` | The game's music (Suno), 128 kbps MP3, loops trimmed on the beat. `tracks.json` has the exact lengths |
| `art/` | Source PNGs from Pixellab, plus `pixellab-character-ids.json` for regenerating or adding animations |
| `tools/` | The Python scripts used to call the Pixellab API and pack the art into the `.js` files, `find_loop.py` and `cut_loop.py` for turning a Suno song into a seamless loop, plus `test_math.js` for the fact engine |

Saves live in `localStorage` under `vh-save-v1`.

See [ROADMAP.md](ROADMAP.md) for what's next.
