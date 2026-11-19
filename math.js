// Math Hunt: the times-tables fact engine. Plain functions with no Phaser, so tools/test_math.js can run them in Node.
//
// Every fact (like 7 × 8) is tracked the way the typing game tracks every key: right or wrong, how fast, and when it
// was last seen. A fact and its turnaround (8 × 7) are one fact, stored under the smaller number first ("7x8").
// Each fact sits on one of five levels and comes back on a schedule that stretches as it moves up.
(function (root) {
  const FAST_MS = 3000;   // right within 3 seconds: Fluent, the bar researchers use for automatic recall
  const OK_MS = 6000;     // right within 6 seconds: Known, the bar used by the UK times-table check
  const LEVELS = [
    { name: 'New', color: 0x5b4f78 },
    { name: 'Learning', color: 0xff6b6b },
    { name: 'Known', color: 0x5ec8ff },
    { name: 'Fluent', color: 0x7be08f },
    { name: 'Mastered', color: 0xffcf5a },
  ];
  const REVIEW_DAYS = [0, 0, 1, 3, 7];   // days until a fact comes back after a right answer, by level
  const LONG_REVIEW = 21;                // a Mastered fact that stays Mastered waits 3 weeks
  const MASTER_DAYS = 3;                 // Fluent on this many different days makes a fact Mastered
  const GATE = 0.8;                      // a stage opens when 80% of the one before it is Known
  const DAILY_GOAL = 60;                 // facts answered right in a day
  const MAX_LEARNING = 4;                // no new facts while this many are still being learned
  const RULE_TABLES = [1, 10];           // taught as a rule ("any number times 1 is itself"), not fact by fact

  const key = (a, b) => (a <= b ? `${a}x${b}` : `${b}x${a}`);
  const parse = k => k.split('x').map(Number);
  const isRule = k => parse(k).some(n => RULE_TABLES.includes(n));

  // Stages follow the order schools use: easy anchors first, then each table that can be built from them.
  // Phase 1 has the first three. Each one is a setting with its own battle track and boss.
  const STAGES = [
    { id: 1, name: 'Graveyard', tables: [1, 10, 2], label: '×1, ×10 and ×2', scene: 'graveyard', track: 'battle-loop', tip: 'Doubles: 2 × 7 is 7 + 7.' },
    { id: 2, name: 'Garden', tables: [5], label: '×5', scene: 'garden', track: 'battle-moonlight-waltz', tip: 'Fives are half of tens: 5 × 8 is half of 80.' },
    { id: 3, name: 'Bat Cave', tables: [4], label: '×4', scene: 'cave', track: 'battle-bat-cave-bounce', tip: 'Fours are double the doubles: 4 × 7 is 14 + 14.' },
  ];
  // Which facts are new in each stage (a turnaround learned earlier doesn't count again), and the lessons that teach them.
  (function buildStages() {
    const seen = new Set();
    STAGES.forEach(s => {
      s.facts = []; s.lessons = [];
      s.tables.forEach(t => {
        const fresh = [];
        for (let b = 1; b <= 10; b++) {
          const k = key(t, b);
          if (!seen.has(k)) { seen.add(k); s.facts.push(k); fresh.push(k); }
        }
        if (!fresh.length) return;
        if (RULE_TABLES.includes(t)) {
          s.lessons.push({ table: t, rule: true, facts: fresh, example: t === 1 ? [1, 7] : [10, 3],
            text: t === 1 ? 'Any number times 1 is just that number.' : 'Times 10: put a 0 on the end.' });
        } else {
          for (let i = 0; i < fresh.length; i += 2) s.lessons.push({ table: t, facts: fresh.slice(i, i + 2) });
        }
      });
    });
  })();
  const STAGE_OF = {};
  STAGES.forEach(s => s.facts.forEach(k => { STAGE_OF[k] = s.id; }));
  const stage = id => STAGES.find(s => s.id === id) || STAGES[0];

  // Days are counted on the device's own calendar, so "tomorrow" means after midnight where the kid lives.
  function dayNum(d = new Date()) {
    return Math.round(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 864e5);
  }

  function ensure(p) {
    const m = p.math = p.math || {};
    m.facts = m.facts || {};
    m.days = m.days || {};
    m.open = Math.max(1, m.open || 1);
    m.placed = !!m.placed;
    m.mastered = m.mastered || {};
    return m;
  }
  function fact(p, k) {
    const F = ensure(p).facts;
    return F[k] || (F[k] = { lvl: 0, hit: 0, miss: 0, ms: 0, fast: 0, days: [], due: 0, int: 0, last: 0 });
  }
  const level = (p, k) => (ensure(p).facts[k] || { lvl: 0 }).lvl;

  // One answer. ok = right on the first try, ms = how long it took. Returns the level before and after.
  // scout = the placement round, where a quick right answer shows the fact is already Fluent.
  function record(f, ok, ms, today, scout = false) {
    const before = f.lvl;
    f.last = today;
    if (!ok) {
      f.miss++;
      f.lvl = scout ? f.lvl : 1;   // a miss in the placement round just leaves the fact to be taught later
      f.int = 0; f.due = today;
      return { before, after: f.lvl };
    }
    f.hit++; f.ms += Math.min(ms, 10000);
    const prevInt = f.int;
    if (ms <= FAST_MS) {
      f.fast++;
      if (!f.days.includes(today)) { f.days.push(today); if (f.days.length > 6) f.days.shift(); }
      f.lvl = scout ? 3 : f.lvl >= 4 ? 4 : Math.min(3, Math.max(2, f.lvl + 1));
      if (f.lvl === 3 && f.days.length >= MASTER_DAYS) f.lvl = 4;
    } else if (ms <= OK_MS) {
      f.lvl = f.lvl >= 4 ? 3 : 2;    // right but not automatic yet
    } else {
      f.lvl = 1;                      // right, but too slow to count as known
    }
    f.int = f.lvl === 4 && prevInt >= REVIEW_DAYS[4] && ms <= FAST_MS ? LONG_REVIEW : REVIEW_DAYS[f.lvl];
    f.due = today + f.int;
    return { before, after: f.lvl };
  }

  // Teach a lesson: its facts become Learning and are due right away.
  function introduce(p, lesson, today) {
    lesson.facts.forEach(k => { const f = fact(p, k); if (f.lvl === 0) { f.lvl = 1; f.due = today; f.last = today; } });
  }

  function progress(p, id) {
    const s = stage(id), n = [0, 0, 0, 0, 0];
    s.facts.forEach(k => n[level(p, k)]++);
    const known = n[2] + n[3] + n[4];
    return { total: s.facts.length, counts: n, met: s.facts.length - n[0], known, fluent: n[3] + n[4], mastered: n[4], pct: known / s.facts.length };
  }
  // Opens every stage whose stage before it is 80% Known. Stages never close again. Returns the newly opened ones.
  function updateOpen(p) {
    const m = ensure(p), opened = [];
    while (m.open < STAGES.length && progress(p, m.open).pct >= GATE) { m.open++; opened.push(stage(m.open)); }
    STAGES.forEach(s => { if (!m.mastered[s.id] && s.facts.every(k => level(p, k) === 4)) m.mastered[s.id] = true; });
    return opened;
  }
  const openStages = p => STAGES.filter(s => s.id <= ensure(p).open);
  const unlockedFacts = p => openStages(p).flatMap(s => s.facts);
  function learningLoad(p) {
    return unlockedFacts(p).filter(k => !isRule(k) && level(p, k) === 1).length;
  }
  function nextLesson(p, id) {
    const s = stage(id);
    for (const L of s.lessons) {
      const fresh = L.facts.filter(k => level(p, k) === 0);
      if (fresh.length) return Object.assign({}, L, { facts: L.facts, fresh });
    }
    return null;
  }
  // The lesson for a hunt in this stage: its own next lesson, or one left over in an earlier open stage
  // (a scouting round can open a stage while a few facts behind it are still untaught).
  const huntLesson = (p, id) => nextLesson(p, id) || openStages(p).map(s => nextLesson(p, s.id)).find(Boolean) || null;
  const canLearn = (p, lesson) => !!lesson && (lesson.rule || learningLoad(p) < MAX_LEARNING);

  // Smart Hunt: the first open stage still under 80% Known, else the newest open stage that has facts left to learn,
  // else the newest open stage.
  function smartStage(p) {
    const open = openStages(p);
    const behind = open.find(s => progress(p, s.id).pct < GATE);
    if (behind) return behind.id;
    const withNew = open.slice().reverse().find(s => nextLesson(p, s.id));
    return (withNew || open[open.length - 1]).id;
  }

  // How much a fact needs practice: misses and slow answers make it come up more often.
  function weakness(f) {
    if (!f) return 1.5;
    const missRate = f.miss / (f.hit + f.miss + 2);
    const avg = f.hit ? f.ms / f.hit : 4000;
    const slow = Math.min(1, Math.max(0, (avg - 1500) / 3000));
    return 1 + missRate * 4 + slow * 1.5;
  }
  function weighted(items, wf, rnd) {
    const ws = items.map(wf), total = ws.reduce((a, b) => a + b, 0);
    let r = rnd() * total;
    for (let i = 0; i < items.length; i++) { r -= ws[i]; if (r <= 0) return items[i]; }
    return items[items.length - 1];
  }

  // Picks the next fact for an enemy. ctx: { kind, stage, focus (lesson facts), avoid (on screen or just seen), today }.
  // Kinds: warmup (known facts), learn (lesson and Learning facts mixed with known ones), review (due facts first),
  // boss (this stage), bonus (everything met), rule (an easy ×1 or ×10 fact for the Bat Queen's bats).
  function pick(p, ctx, rnd = Math.random) {
    const F = ensure(p).facts, today = ctx.today, avoid = ctx.avoid || new Set();
    const all = unlockedFacts(p);
    const lv = k => (F[k] || { lvl: 0 }).lvl;
    const fresh = list => { const c = list.filter(k => !avoid.has(k)); return c.length ? c : list; };
    const inStage = k => STAGE_OF[k] === ctx.stage;
    const met = all.filter(k => lv(k) >= 1);
    const learning = met.filter(k => lv(k) === 1 && !isRule(k));
    const known = met.filter(k => lv(k) >= 2);
    const due = known.filter(k => (F[k].due || 0) <= today);
    // ×1 and ×10 facts are easy and there are 19 of them, so they come up less often than the rest
    const easy = k => (isRule(k) ? 0.35 : 1);
    const knownW = k => weakness(F[k]) * easy(k) * (inStage(k) ? 1.5 : 1) * (lv(k) === 4 ? 0.5 : 1);
    const from = (list, wf) => (list.length ? weighted(fresh(list), wf, rnd) : null);
    const focus = [...new Set([...(ctx.focus || []), ...learning.filter(inStage)])];
    let k = null;
    switch (ctx.kind) {
      case 'warmup':
        k = from(known, x => [0, 0, 2, 1.5, 0.7][lv(x)] * easy(x));
        break;
      case 'learn':
        if (focus.length && rnd() < 0.45) k = from(focus, x => ((ctx.focus || []).includes(x) ? 2 : 1) * weakness(F[x]));
        else k = from(known, knownW);
        if (!k) k = from(focus, x => weakness(F[x]));
        break;
      case 'review':
        if (learning.length && rnd() < 0.25) k = from(learning, x => weakness(F[x]));
        else if (due.length && rnd() < 0.65) k = from(due, x => 2 * weakness(F[x]) * easy(x));
        else k = from(known, knownW);
        break;
      case 'boss':
        k = from(met.filter(inStage), x => weakness(F[x]) * easy(x));
        break;
      case 'rule':
        k = from(met.filter(isRule), () => 1) || from(stage(1).facts.filter(isRule), () => 1);
        break;
      default:   // bonus
        k = from(met, x => weakness(F[x]) * easy(x) * (lv(x) === 1 ? 2 : 1));
    }
    if (!k) k = from(met, () => 1) || from(stage(ctx.stage).facts, () => 1);
    return k;
  }

  // The placement round: a couple of facts from every table, easy to hard. A quick right answer marks a fact as
  // already Fluent, so a kid never redoes facts they know.
  function scoutList(rnd = Math.random) {
    const out = [key(1, 2 + Math.floor(rnd() * 8)), key(10, 2 + Math.floor(rnd() * 8))];
    [2, 5, 4, 3, 9, 6, 7, 8].forEach(t => {
      const bs = [3, 4, 5, 6, 7, 8, 9, 2].filter(b => !out.includes(key(t, b)));
      for (let i = 0; i < 2 && bs.length; i++) out.push(key(t, bs.splice(Math.floor(rnd() * bs.length), 1)[0]));
    });
    return out;
  }
  // After the placement round: if both rule facts (×1 and ×10) were right, the whole rule is Known.
  function finishScout(p, results, today) {
    const m = ensure(p);
    m.placed = true;
    const ruleOk = results.filter(r => isRule(r.key));
    if (ruleOk.length >= 2 && ruleOk.every(r => r.ok && r.ms <= OK_MS)) {
      stage(1).facts.filter(isRule).forEach(k => { const f = fact(p, k); if (f.lvl < 2) { f.lvl = 2; f.int = 1; f.due = today + 1; f.last = today; } });
    }
    return updateOpen(p);
  }

  // The facts most worth practicing: met facts with the most misses and slowest answers.
  function weakFacts(p, n = 3) {
    const F = ensure(p).facts;
    return Object.keys(F).filter(k => F[k].lvl >= 1 && F[k].hit + F[k].miss >= 2 && weakness(F[k]) > 1.6)
      .sort((a, b) => weakness(F[b]) - weakness(F[a])).slice(0, n);
  }
  const label = k => { const [a, b] = parse(k); return `${b} × ${a}`; };

  // One day's log: answers, right answers, fluent answers and the time per table, for the parent page later.
  function logDay(p, dateKey, k, ok, ms) {
    const d = ensure(p).days[dateKey] || (ensure(p).days[dateKey] = { n: 0, right: 0, fast: 0, t: {} });
    d.n++;
    if (!ok) return d;
    d.right++; if (ms <= FAST_MS) d.fast++;
    new Set(parse(k)).forEach(t => { const s = d.t[t] || (d.t[t] = [0, 0]); s[0] += Math.min(ms, 10000); s[1]++; });
    return d;
  }

  root.VH_MATH = {
    FAST_MS, OK_MS, LEVELS, STAGES, GATE, DAILY_GOAL, MAX_LEARNING, STAGE_OF,
    key, parse, isRule, stage, dayNum, ensure, fact, level, record, introduce, progress, updateOpen, openStages,
    learningLoad, nextLesson, huntLesson, canLearn, smartStage, weakness, pick, scoutList, finishScout, weakFacts, label, logDay,
  };
})(typeof window !== 'undefined' ? window : globalThis);
