// Checks for the Math Hunt fact engine in math.js. Run with: node tools/test_math.js
const assert = require('assert');
require('../math.js');
const M = globalThis.VH_MATH;

let n = 0;
const test = (name, fn) => { fn(); n++; console.log('ok', name); };
const fresh = () => ({ name: 'T' });
const T0 = 20000;

test('stages hold 27, 7 and 6 new facts', () => {
  assert.deepStrictEqual(M.STAGES.map(s => s.facts.length), [27, 7, 6]);
  assert.strictEqual(new Set(M.STAGES.flatMap(s => s.facts)).size, 40);
  assert.strictEqual(M.key(8, 7), '7x8');
  assert.deepStrictEqual(M.STAGES[0].lessons.map(l => l.facts.length), [10, 9, 2, 2, 2, 2]);
  assert.ok(M.STAGES[0].lessons[0].rule && M.STAGES[0].lessons[1].rule);
});

test('levels move up with fast answers and drop on a miss', () => {
  const f = M.fact(fresh(), '2x7'); f.lvl = 1;
  M.record(f, true, 2000, T0); assert.strictEqual(f.lvl, 2); assert.strictEqual(f.due, T0 + 1);
  M.record(f, true, 2000, T0 + 1); assert.strictEqual(f.lvl, 3); assert.strictEqual(f.due, T0 + 4);
  M.record(f, true, 2000, T0 + 4); assert.strictEqual(f.lvl, 4, 'fluent on 3 different days is mastered');
  assert.strictEqual(f.due, T0 + 11);
  M.record(f, true, 2000, T0 + 11); assert.strictEqual(f.due, T0 + 32, 'mastered again waits three weeks');
  M.record(f, true, 4500, T0 + 32); assert.strictEqual(f.lvl, 3, 'a slow answer on a mastered fact drops it to fluent');
  M.record(f, false, 0, T0 + 33); assert.strictEqual(f.lvl, 1); assert.strictEqual(f.due, T0 + 33);
  M.record(f, true, 8000, T0 + 33); assert.strictEqual(f.lvl, 1, 'right but over 6 seconds stays learning');
  M.record(f, true, 5000, T0 + 33); assert.strictEqual(f.lvl, 2, '3 to 6 seconds is known');
});

test('placement marks quick facts fluent and leaves misses for later', () => {
  const p = fresh();
  const a = M.fact(p, '7x8'); M.record(a, true, 2500, T0, true); assert.strictEqual(a.lvl, 3);
  const b = M.fact(p, '6x7'); M.record(b, false, 0, T0, true); assert.strictEqual(b.lvl, 0);
  const c = M.fact(p, '3x4'); M.record(c, true, 5000, T0, true); assert.strictEqual(c.lvl, 2);
});

test('placement with both rule facts right makes the whole rule known', () => {
  const p = fresh();
  M.finishScout(p, [{ key: '1x7', ok: true, ms: 2000 }, { key: '3x10', ok: true, ms: 2500 }], T0);
  assert.ok(M.ensure(p).placed);
  M.STAGES[0].facts.filter(M.isRule).forEach(k => assert.ok(M.level(p, k) >= 2, k));
  assert.strictEqual(M.level(p, '2x7'), 0);
  assert.strictEqual(M.nextLesson(p, 1).table, 2);
});

test('a stage opens at 80% known and never closes', () => {
  const p = fresh();
  const s1 = M.STAGES[0].facts;
  s1.slice(0, 21).forEach(k => { M.fact(p, k).lvl = 2; });
  assert.deepStrictEqual(M.updateOpen(p), []);
  M.fact(p, s1[21]).lvl = 2;   // 22 of 27 is 81%
  assert.deepStrictEqual(M.updateOpen(p).map(s => s.id), [2]);
  s1.forEach(k => { M.fact(p, k).lvl = 1; });
  M.updateOpen(p);
  assert.strictEqual(M.ensure(p).open, 2);
});

test('new facts wait while too many are still being learned', () => {
  const p = fresh();
  ['2x2', '2x3', '2x4', '2x5'].forEach(k => { M.fact(p, k).lvl = 1; });
  assert.strictEqual(M.learningLoad(p), 4);
  const L = M.nextLesson(p, 1);
  assert.ok(L.rule, 'rule lessons come first and never wait');
  M.introduce(p, L, T0); M.introduce(p, M.nextLesson(p, 1), T0);
  assert.ok(!M.canLearn(p, M.nextLesson(p, 1)));
  M.fact(p, '2x2').lvl = 2;
  assert.ok(M.canLearn(p, M.nextLesson(p, 1)));
});

test('smart hunt picks the stage still under 80%', () => {
  const p = fresh();
  assert.strictEqual(M.smartStage(p), 1);
  M.STAGES[0].facts.forEach(k => { M.fact(p, k).lvl = 2; });
  M.updateOpen(p);
  assert.strictEqual(M.smartStage(p), 2);
});

test('pick always returns a fact from the open stages, for every kind', () => {
  const kinds = ['warmup', 'learn', 'review', 'boss', 'bonus', 'rule'];
  const p = fresh();
  for (const kind of kinds) assert.ok(M.STAGE_OF[M.pick(p, { kind, stage: 1, today: T0 })], 'empty profile ' + kind);
  M.introduce(p, M.nextLesson(p, 1), T0);
  M.fact(p, '2x7').lvl = 3; M.fact(p, '2x8').lvl = 2; M.fact(p, '2x8').due = T0;
  for (let i = 0; i < 2000; i++) {
    const kind = kinds[i % kinds.length], k = M.pick(p, { kind, stage: 1, today: T0, focus: ['2x2', '2x3'], avoid: new Set(['2x7']) });
    assert.strictEqual(M.STAGE_OF[k], 1, kind + ' ' + k);
  }
});

test('a hunt teaches facts left behind in an earlier stage', () => {
  const p = fresh();
  M.STAGES[0].facts.forEach(k => { M.fact(p, k).lvl = 2; });
  M.fact(p, '2x6').lvl = 0;
  M.STAGES[1].facts.forEach(k => { M.fact(p, k).lvl = 2; });
  M.updateOpen(p);
  assert.strictEqual(M.nextLesson(p, 2), null);
  assert.deepStrictEqual(M.huntLesson(p, 2).fresh, ['2x6']);
});

test('learn waves mix focus facts with known ones', () => {
  const p = fresh();
  M.STAGES[0].facts.filter(M.isRule).forEach(k => { M.fact(p, k).lvl = 2; });
  const focus = ['2x2', '2x3']; focus.forEach(k => { M.fact(p, k).lvl = 1; });
  let hits = 0;
  for (let i = 0; i < 4000; i++) if (focus.includes(M.pick(p, { kind: 'learn', stage: 1, today: T0, focus }))) hits++;
  assert.ok(hits > 1400 && hits < 2200, `focus share ${hits / 4000}`);
});

test('scout list has 18 different facts, easy tables first', () => {
  for (let i = 0; i < 200; i++) {
    const L = M.scoutList();
    assert.strictEqual(L.length, 18); assert.strictEqual(new Set(L).size, 18);
    assert.ok(M.isRule(L[0]) && M.isRule(L[1]));
  }
});

test('day log counts answers and time per table', () => {
  const p = fresh();
  M.logDay(p, '2026-11-19', '2x7', true, 2000);
  M.logDay(p, '2026-11-19', '2x7', false, 0);
  const d = M.logDay(p, '2026-11-19', '7x7', true, 4000);
  assert.deepStrictEqual([d.n, d.right, d.fast], [3, 2, 1]);
  assert.deepStrictEqual(d.t[7], [6000, 2]); assert.deepStrictEqual(d.t[2], [2000, 1]);
});

console.log(`\n${n} checks passed`);
