const SIZE = 5;
const DIRECTIONS = ["left", "right", "up", "down"];
const PRESENT = "present_simple";
const PAST = "past_simple";
const FUTURE = "future_simple";
const PERFECT = "present_perfect";
const CONTINUOUS = "present_continuous";
const AFFIRMATIVE = "affirmative";
const NEGATIVE = "negative";
const QUESTION = "question";
const PHRASES_TO_UNLOCK_ADVERBS = 2;
const SENTENCES_TO_BANK = 3;
const REPLACEMENTS_PER_PART = 1;

const REPLACEMENT_KIND = {
  subject: "subject",
  verb: "verb",
  adverb: "adverb",
  clause: "subject",
  aux: "aux",
  object: "object",
  negation: "aux",
  question: "aux",
  chain: "aux",
};

const FORM_GROUP = {
  base: "base",
  s: "s",
  dont: "base",
  do: "base",
  doesnt: "s",
  does: "s",
  past: "any",
  didnt: "any",
  did: "any",
  ing: "any",
  pp: "any",
  will: "any",
  wont: "any",
  willq: "any",
  have: "base",
  havent: "base",
  haveq: "base",
  has: "s",
  hasnt: "s",
  hasq: "s",
  am: "am",
  amnot: "am",
  amq: "am",
  is: "is",
  isnt: "is",
  isq: "is",
  are: "are",
  arent: "are",
  areq: "are",
};

const AUX_FORMS = [
  ["dont", "don't", PRESENT, NEGATIVE],
  ["doesnt", "doesn't", PRESENT, NEGATIVE],
  ["didnt", "didn't", PAST, NEGATIVE],
  ["do", "Do", PRESENT, QUESTION],
  ["does", "Does", PRESENT, QUESTION],
  ["did", "Did", PAST, QUESTION],
  ["will", "will", FUTURE, AFFIRMATIVE],
  ["wont", "won't", FUTURE, NEGATIVE],
  ["willq", "Will", FUTURE, QUESTION],
  ["have", "have", PERFECT, AFFIRMATIVE],
  ["has", "has", PERFECT, AFFIRMATIVE],
  ["havent", "haven't", PERFECT, NEGATIVE],
  ["hasnt", "hasn't", PERFECT, NEGATIVE],
  ["haveq", "Have", PERFECT, QUESTION],
  ["hasq", "Has", PERFECT, QUESTION],
  ["am", "am", CONTINUOUS, AFFIRMATIVE],
  ["is", "is", CONTINUOUS, AFFIRMATIVE],
  ["are", "are", CONTINUOUS, AFFIRMATIVE],
  ["amnot", "am not", CONTINUOUS, NEGATIVE],
  ["isnt", "isn't", CONTINUOUS, NEGATIVE],
  ["arent", "aren't", CONTINUOUS, NEGATIVE],
  ["amq", "Am", CONTINUOUS, QUESTION],
  ["isq", "Is", CONTINUOUS, QUESTION],
  ["areq", "Are", CONTINUOUS, QUESTION],
];

function rule(id, left, right, resultKind, resultLevel, resultTense = null, polarity = null) {
  return { id, left, right, resultKind, resultLevel, resultTense, polarity };
}

function pattern(kind, extra = {}) {
  return { kind, form: null, tense: null, agreement: null, ...extra };
}

const RULES = [
  rule("ps_3sg", pattern("subject", { agreement: "3sg" }), pattern("verb", { form: "s" }), "clause", 2, PRESENT, AFFIRMATIVE),
  rule("ps_base", pattern("subject", { agreement: "not_3sg" }), pattern("verb", { form: "base" }), "clause", 2, PRESENT, AFFIRMATIVE),
  rule("past_verb", pattern("subject"), pattern("verb", { form: "past" }), "clause", 2, PAST, AFFIRMATIVE),
  rule("ps_habit", pattern("clause", { tense: PRESENT }), pattern("adverb", { tense: PRESENT }), "sentence", 3, PRESENT),
  rule("past_habit", pattern("clause", { tense: PAST }), pattern("adverb", { tense: PAST }), "sentence", 3, PAST),
  rule("neg_dont", pattern("subject", { agreement: "not_3sg" }), pattern("aux", { form: "dont" }), "negation", 2, PRESENT, NEGATIVE),
  rule("neg_doesnt", pattern("subject", { agreement: "3sg" }), pattern("aux", { form: "doesnt" }), "negation", 2, PRESENT, NEGATIVE),
  rule("neg_didnt", pattern("subject"), pattern("aux", { form: "didnt" }), "negation", 2, PAST, NEGATIVE),
  rule("neg_base", pattern("negation"), pattern("verb", { form: "base" }), "clause", 2, null, NEGATIVE),
  rule("q_do", pattern("aux", { form: "do" }), pattern("subject", { agreement: "not_3sg" }), "question", 2, PRESENT, QUESTION),
  rule("q_does", pattern("aux", { form: "does" }), pattern("subject", { agreement: "3sg" }), "question", 2, PRESENT, QUESTION),
  rule("q_did", pattern("aux", { form: "did" }), pattern("subject"), "question", 2, PAST, QUESTION),
  rule("q_base", pattern("question"), pattern("verb", { form: "base" }), "clause", 2, null, QUESTION),
  rule("fut_will", pattern("subject"), pattern("aux", { form: "will" }), "chain", 2, FUTURE, AFFIRMATIVE),
  rule("fut_wont", pattern("subject"), pattern("aux", { form: "wont" }), "negation", 2, FUTURE, NEGATIVE),
  rule("fut_willq", pattern("aux", { form: "willq" }), pattern("subject"), "question", 2, FUTURE, QUESTION),
  rule("fut_verb", pattern("chain"), pattern("verb", { form: "base" }), "clause", 2, FUTURE, AFFIRMATIVE),
  rule("fut_habit", pattern("clause", { tense: FUTURE }), pattern("adverb", { tense: FUTURE }), "sentence", 3, FUTURE),
  rule("perf_have", pattern("subject", { agreement: "not_3sg" }), pattern("aux", { form: "have" }), "chain", 2, PERFECT, AFFIRMATIVE),
  rule("perf_has", pattern("subject", { agreement: "3sg" }), pattern("aux", { form: "has" }), "chain", 2, PERFECT, AFFIRMATIVE),
  rule("perf_havent", pattern("subject", { agreement: "not_3sg" }), pattern("aux", { form: "havent" }), "negation", 2, PERFECT, NEGATIVE),
  rule("perf_hasnt", pattern("subject", { agreement: "3sg" }), pattern("aux", { form: "hasnt" }), "negation", 2, PERFECT, NEGATIVE),
  rule("perf_haveq", pattern("aux", { form: "haveq" }), pattern("subject", { agreement: "not_3sg" }), "question", 2, PERFECT, QUESTION),
  rule("perf_hasq", pattern("aux", { form: "hasq" }), pattern("subject", { agreement: "3sg" }), "question", 2, PERFECT, QUESTION),
  rule("perf_verb", pattern("chain"), pattern("verb", { form: "pp" }), "clause", 2, PERFECT, AFFIRMATIVE),
  rule("perf_neg_verb", pattern("negation"), pattern("verb", { form: "pp" }), "clause", 2, PERFECT, NEGATIVE),
  rule("perf_q_verb", pattern("question"), pattern("verb", { form: "pp" }), "clause", 2, PERFECT, QUESTION),
  rule("perf_habit", pattern("clause", { tense: PERFECT }), pattern("adverb", { tense: PERFECT }), "sentence", 3, PERFECT),
  rule("cont_am", pattern("subject", { agreement: "1sg" }), pattern("aux", { form: "am" }), "chain", 2, CONTINUOUS, AFFIRMATIVE),
  rule("cont_is", pattern("subject", { agreement: "3sg" }), pattern("aux", { form: "is" }), "chain", 2, CONTINUOUS, AFFIRMATIVE),
  rule("cont_are", pattern("subject", { agreement: "are" }), pattern("aux", { form: "are" }), "chain", 2, CONTINUOUS, AFFIRMATIVE),
  rule("cont_amnot", pattern("subject", { agreement: "1sg" }), pattern("aux", { form: "amnot" }), "negation", 2, CONTINUOUS, NEGATIVE),
  rule("cont_isnt", pattern("subject", { agreement: "3sg" }), pattern("aux", { form: "isnt" }), "negation", 2, CONTINUOUS, NEGATIVE),
  rule("cont_arent", pattern("subject", { agreement: "are" }), pattern("aux", { form: "arent" }), "negation", 2, CONTINUOUS, NEGATIVE),
  rule("cont_amq", pattern("aux", { form: "amq" }), pattern("subject", { agreement: "1sg" }), "question", 2, CONTINUOUS, QUESTION),
  rule("cont_isq", pattern("aux", { form: "isq" }), pattern("subject", { agreement: "3sg" }), "question", 2, CONTINUOUS, QUESTION),
  rule("cont_areq", pattern("aux", { form: "areq" }), pattern("subject", { agreement: "are" }), "question", 2, CONTINUOUS, QUESTION),
  rule("cont_verb", pattern("chain"), pattern("verb", { form: "ing" }), "clause", 2, CONTINUOUS, AFFIRMATIVE),
  rule("cont_neg_verb", pattern("negation"), pattern("verb", { form: "ing" }), "clause", 2, CONTINUOUS, NEGATIVE),
  rule("cont_q_verb", pattern("question"), pattern("verb", { form: "ing" }), "clause", 2, CONTINUOUS, QUESTION),
  rule("cont_habit", pattern("clause", { tense: CONTINUOUS }), pattern("adverb", { tense: CONTINUOUS }), "sentence", 3, CONTINUOUS),
  rule("object", pattern("clause"), pattern("object"), "clause", 2),
];

function is3sg(tile) {
  return tile.person === 3 && tile.number === "sg";
}

function is1sg(tile) {
  return tile.person === 1 && tile.number === "sg";
}

function matches(pat, tile) {
  if (tile.kind !== pat.kind) return false;
  if (pat.form != null && tile.form !== pat.form) return false;
  if (pat.tense != null && tile.tense !== pat.tense) return false;
  if (pat.agreement === "3sg" && !is3sg(tile)) return false;
  if (pat.agreement === "not_3sg" && is3sg(tile)) return false;
  if (pat.agreement === "1sg" && !is1sg(tile)) return false;
  if (pat.agreement === "are" && (is3sg(tile) || is1sg(tile))) return false;
  return true;
}

function mergeScore(level, comboIndex) {
  return 10 * 2 ** level * comboIndex;
}

function buildTile(ruleItem, left, right, tileId) {
  return {
    id: tileId,
    text: `${left.text} ${right.text}`,
    kind: ruleItem.resultKind,
    level: ruleItem.resultLevel,
    lemma: right.lemma || left.lemma || null,
    form: null,
    person: left.person != null ? left.person : right.person ?? null,
    number: left.number != null ? left.number : right.number ?? null,
    tense: ruleItem.resultTense || left.tense || right.tense || null,
  };
}

function resolveMerge(left, right, rules, nearMiss, newId) {
  for (const ruleItem of rules) {
    if (matches(ruleItem.left, left) && matches(ruleItem.right, right)) {
      return { ok: true, tile: buildTile(ruleItem, left, right, newId()), hint: null };
    }
  }
  return { ok: false, tile: null, hint: nearMiss(left, right) };
}

function emptyGrid() {
  return Array.from({ length: SIZE }, () => Array(SIZE).fill(null));
}

function gridIds(grid) {
  return grid.map((row) => row.map((cell) => (cell ? cell.id : "")).join(",")).join("|");
}

function tilesOf(grid) {
  const tiles = [];
  for (const row of grid) {
    for (const cell of row) {
      if (cell) tiles.push(cell);
    }
  }
  return tiles;
}

function clauseIds(grid) {
  return new Set(tilesOf(grid).filter((cell) => cell.kind === "clause").map((cell) => cell.id));
}

function formGroup(form) {
  if (form == null) return null;
  return FORM_GROUP[form] ?? null;
}

function ruSentences(count) {
  const tail = count % 100;
  const digit = count % 10;
  let word = "предложения";
  if ((tail >= 11 && tail <= 14) || digit === 0 || digit >= 5) word = "предложений";
  else if (digit === 1) word = "предложение";
  return `${count} ${word}`;
}

function choice(rng, items) {
  return items[Math.floor(rng() * items.length)];
}

function weightedChoice(rng, items, weights) {
  const total = weights.reduce((sum, weight) => sum + weight, 0);
  let mark = rng() * total;
  for (let index = 0; index < items.length; index += 1) {
    mark -= weights[index];
    if (mark < 0) return items[index];
  }
  return items[items.length - 1];
}

function shuffle(rng, items) {
  for (let index = items.length - 1; index > 0; index -= 1) {
    const swap = Math.floor(rng() * (index + 1));
    [items[index], items[swap]] = [items[swap], items[index]];
  }
}

function effectiveWeight(spec, sessionErrors) {
  const weak = spec.boostRules.some((ruleId) => (sessionErrors[ruleId] || 0) >= 3);
  return weak ? spec.weight * 1.5 : spec.weight;
}

function hint(ruleId, left, right, text) {
  return {
    ruleId,
    text: `${left.text} + ${right.text} — ${text}`,
    leftId: left.id,
    rightId: right.id,
  };
}

function verbForm(lexicon, lemma, form) {
  if (!lemma) return null;
  const entry = lexicon.verbs[lemma];
  return entry ? entry[form] || null : null;
}

export function createPack(data) {
  const verbs = {};
  for (const item of data.verbs) {
    verbs[item.lemma] = item;
  }
  const lexicon = {
    verbs,
    subjects: data.subjects,
    adverbs: data.adverbs,
    objects: data.objects || [],
  };
  const spawnSpecs = [];
  for (const subject of lexicon.subjects) {
    const third = subject.person === 3 && subject.number === "sg";
    spawnSpecs.push({
      weight: 7,
      boostRules: [third ? "ps_3sg" : "ps_base"],
      kind: "subject",
      text: subject.text,
      level: 1,
      lemma: null,
      form: null,
      person: subject.person,
      number: subject.number,
      tense: null,
      polarity: null,
    });
  }
  for (const [lemma, forms] of Object.entries(verbs)) {
    for (const form of ["base", "s", "past", "ing", "pp"]) {
      spawnSpecs.push({
        weight: 1,
        boostRules: ["ps_3sg", "ps_base", "past_verb"],
        kind: "verb",
        text: forms[form],
        level: 1,
        lemma,
        form,
        person: null,
        number: null,
        tense: form === "past" ? PAST : PRESENT,
        polarity: null,
      });
    }
  }
  for (const adverb of lexicon.adverbs) {
    spawnSpecs.push({
      weight: 8,
      boostRules: [],
      kind: "adverb",
      text: adverb.text,
      level: 1,
      lemma: null,
      form: null,
      person: null,
      number: null,
      tense: adverb.tense,
      polarity: null,
    });
  }
  for (const [form, text, tense, polarity] of AUX_FORMS) {
    spawnSpecs.push({
      weight: 6,
      boostRules: [],
      kind: "aux",
      text,
      level: 1,
      lemma: null,
      form,
      person: null,
      number: null,
      tense,
      polarity,
    });
  }
  for (const object of lexicon.objects) {
    spawnSpecs.push({
      weight: 6,
      boostRules: [],
      kind: "object",
      text: object.text,
      level: 1,
      lemma: null,
      form: null,
      person: null,
      number: null,
      tense: null,
      polarity: null,
    });
  }

  function findSpec(fields) {
    const spec = spawnSpecs.find((item) => Object.entries(fields).every(([key, value]) => item[key] === value));
    if (!spec) throw new Error(`Нет плитки ${JSON.stringify(fields)}`);
    return spec;
  }

  function toTile(spec, tileId) {
    return {
      id: tileId,
      text: spec.text,
      kind: spec.kind,
      level: spec.level,
      lemma: spec.lemma,
      form: spec.form,
      person: spec.person,
      number: spec.number,
      tense: spec.tense,
    };
  }

  const pack = {
    lexicon,
    rules: RULES,
    spawnSpecs,
    phrasesToUnlockAdverbs: PHRASES_TO_UNLOCK_ADVERBS,
    sentencesToBank: SENTENCES_TO_BANK,
    activeTense: PRESENT,
    activePolarity: AFFIRMATIVE,
    isGoal(tile) {
      return tile.kind === "sentence" && tile.level >= 3;
    },
    subject(text, tileId) {
      return toTile(findSpec({ kind: "subject", text }), tileId);
    },
    verb(lemma, form, tileId) {
      return toTile(findSpec({ kind: "verb", lemma, form }), tileId);
    },
    adverb(text, tileId) {
      return toTile(findSpec({ kind: "adverb", text }), tileId);
    },
    aux(form, tileId) {
      return toTile(findSpec({ kind: "aux", form }), tileId);
    },
    object(text, tileId) {
      return toTile(findSpec({ kind: "object", text }), tileId);
    },
    nearMiss(left, right) {
      return nearMiss(pack, left, right);
    },
  };
  return pack;
}

function nearMiss(pack, left, right) {
  const modeHint = modeHintFor(pack, left, right);
  if (modeHint) return modeHint;
  if (left.kind === "subject" && right.kind === "verb") return agreementHint(pack, left, right);
  if (left.kind === "verb" && right.kind === "subject") {
    return hint("ps_order", left, right, "порядок слов: сначала подлежащее, потом глагол");
  }
  if (left.kind === "adverb" && right.kind === "clause") {
    return hint("ps_order", left, right, "обстоятельство ставится после фразы");
  }
  if (left.kind === "object" && right.kind === "clause") {
    return hint("object", left, right, "дополнение ставится после фразы");
  }
  return null;
}

const NEG_PARTICLE = {
  [PRESENT]: "don't / doesn't",
  [PAST]: "didn't",
  [FUTURE]: "won't",
  [PERFECT]: "haven't / hasn't",
  [CONTINUOUS]: "am not / isn't / aren't",
};
const Q_PARTICLE = {
  [PRESENT]: "Do / Does",
  [PAST]: "Did",
  [FUTURE]: "Will",
  [PERFECT]: "Have / Has",
  [CONTINUOUS]: "Am / Is / Are",
};
const AFFIRM_AUX = {
  [FUTURE]: "сначала will, потом глагол без -s",
  [PERFECT]: "сначала have или has, потом третья форма глагола",
  [CONTINUOUS]: "сначала am, is или are, потом форма с -ing",
};
const VERB_AFTER = { [PERFECT]: "pp", [CONTINUOUS]: "ing" };
const FORM_LABEL = { base: "глагол без -s", pp: "третья форма", ing: "форма с -ing" };
const QUESTION_AUX = new Set(["do", "does", "did", "willq", "haveq", "hasq", "amq", "isq", "areq"]);

function modeHintFor(pack, left, right) {
  if (pack.activePolarity === NEGATIVE && left.kind === "subject" && right.kind === "verb") {
    const particle = NEG_PARTICLE[pack.activeTense] || "don't / doesn't";
    return hint("neg_base", left, right, `для отрицания сначала частица ${particle}, потом нужная форма глагола`);
  }
  if (pack.activePolarity === QUESTION && left.kind === "subject" && right.kind === "verb") {
    const particle = Q_PARTICLE[pack.activeTense] || "Do / Does";
    return hint("q_base", left, right, `вопрос начинается с ${particle}, потом подлежащее и нужная форма глагола`);
  }
  if (
    pack.activePolarity === AFFIRMATIVE &&
    (pack.activeTense === FUTURE || pack.activeTense === PERFECT || pack.activeTense === CONTINUOUS) &&
    left.kind === "subject" &&
    right.kind === "verb"
  ) {
    return hint(pack.activeTense === FUTURE ? "fut_will" : "perf_have", left, right, AFFIRM_AUX[pack.activeTense]);
  }
  if (
    pack.activePolarity === AFFIRMATIVE &&
    pack.activeTense === PAST &&
    left.kind === "subject" &&
    right.kind === "verb" &&
    right.form !== "past"
  ) {
    const expected = verbForm(pack.lexicon, right.lemma, "past") || "вторая форма";
    return hint("past_verb", left, right, `в Past Simple нужна вторая форма: ${expected}`);
  }
  if (left.kind === "subject" && right.kind === "aux") return auxAgreementHint(left, right);
  if (left.kind === "aux" && right.kind === "subject") return questionAgreementHint(left, right);
  const expectedForm = VERB_AFTER[pack.activeTense] || "base";
  if (
    (left.kind === "negation" || left.kind === "question" || left.kind === "chain") &&
    right.kind === "verb" &&
    right.form !== expectedForm
  ) {
    const label = FORM_LABEL[expectedForm];
    const expected = verbForm(pack.lexicon, right.lemma, expectedForm) || label;
    return hint(
      left.kind === "negation" ? "neg_base" : "q_base",
      left,
      right,
      `после частицы нужна форма «${label}»: ${expected}`,
    );
  }
  return null;
}

function auxAgreementHint(left, right) {
  const form = right.form;
  const first = is1sg(left);
  const third = is3sg(left);
  if (form === "doesnt" && !third) return hint("neg_dont", left, right, "после I/you/we/they нужна частица don't");
  if (form === "dont" && third) return hint("neg_doesnt", left, right, "для he/she/it нужна частица doesn't");
  if (QUESTION_AUX.has(form)) return hint("q_base", left, right, "в вопросе частица стоит перед подлежащим");
  if ((form === "has" || form === "hasnt") && !third) {
    const other = form === "hasnt" ? "haven't" : "have";
    return hint("perf_have", left, right, `после I/you/we/they нужна частица ${other}`);
  }
  if ((form === "have" || form === "havent") && third) {
    const other = form === "havent" ? "hasn't" : "has";
    return hint("perf_has", left, right, `для he/she/it нужна частица ${other}`);
  }
  if ((form === "am" || form === "amnot") && !first) {
    const other = third ? (form === "amnot" ? "isn't" : "is") : form === "amnot" ? "aren't" : "are";
    return hint("cont_am", left, right, `с этим подлежащим нужна частица ${other}`);
  }
  if ((form === "is" || form === "isnt") && first) {
    return hint("cont_am", left, right, `после I нужна частица ${form === "isnt" ? "am not" : "am"}`);
  }
  if ((form === "is" || form === "isnt") && !third) {
    return hint("cont_are", left, right, `после you/we/they нужна частица ${form === "isnt" ? "aren't" : "are"}`);
  }
  if ((form === "are" || form === "arent") && first) {
    return hint("cont_am", left, right, `после I нужна частица ${form === "arent" ? "am not" : "am"}`);
  }
  if ((form === "are" || form === "arent") && third) {
    return hint("cont_is", left, right, `для he/she/it нужна частица ${form === "arent" ? "isn't" : "is"}`);
  }
  return null;
}

function questionAgreementHint(left, right) {
  const form = left.form;
  const first = is1sg(right);
  const third = is3sg(right);
  if (form === "do" && third) return hint("q_does", left, right, "перед he/she/it нужно Does");
  if (form === "does" && !third) return hint("q_do", left, right, "перед I/you/we/they нужно Do");
  if (form === "haveq" && third) return hint("perf_hasq", left, right, "перед he/she/it нужно Has");
  if (form === "hasq" && !third) return hint("perf_haveq", left, right, "перед I/you/we/they нужно Have");
  if (form === "amq" && !first) return hint("cont_amq", left, right, `перед этим подлежащим нужно ${third ? "Is" : "Are"}`);
  if (form === "isq" && first) return hint("cont_amq", left, right, "перед I нужно Am");
  if (form === "isq" && !third) return hint("cont_areq", left, right, "перед you/we/they нужно Are");
  if (form === "areq" && first) return hint("cont_amq", left, right, "перед I нужно Am");
  if (form === "areq" && third) return hint("cont_isq", left, right, "перед he/she/it нужно Is");
  return null;
}

function agreementHint(pack, left, right) {
  if (is3sg(left)) {
    const expected = verbForm(pack.lexicon, right.lemma, "s") || "глагол с -s";
    return hint("ps_3sg", left, right, `для he/she/it в Present Simple нужно ${expected}`);
  }
  const expected = verbForm(pack.lexicon, right.lemma, "base") || "глагол без -s";
  return hint("ps_base", left, right, `после I/you/we/they форма без -s: ${expected}`);
}

function activeRules(game) {
  return game.pack.rules.filter((ruleItem) => {
    if (ruleItem.resultTense != null && ruleItem.resultTense !== game.tense) return false;
    if (ruleItem.polarity != null && ruleItem.polarity !== game.polarity) return false;
    if ((ruleItem.id === "neg_base" || ruleItem.id === "q_base") && (game.tense === PERFECT || game.tense === CONTINUOUS)) {
      return false;
    }
    return true;
  });
}

function slideLine(cells, towardStart, resolve, combo) {
  const tiles = cells.filter(Boolean);
  const hints = [];
  let score = 0;
  if (towardStart) {
    const kept = [];
    let index = 0;
    while (index < tiles.length) {
      if (index + 1 < tiles.length) {
        const outcome = resolve(tiles[index], tiles[index + 1]);
        if (outcome.ok) {
          combo += 1;
          score += mergeScore(outcome.tile.level, combo);
          kept.push(outcome.tile);
          index += 2;
          continue;
        }
        if (outcome.hint) hints.push(outcome.hint);
      }
      kept.push(tiles[index]);
      index += 1;
    }
    while (kept.length < SIZE) kept.push(null);
    return { line: kept, combo, score, hints };
  }
  const keptFromEnd = [];
  let index = tiles.length - 1;
  while (index >= 0) {
    if (index - 1 >= 0) {
      const outcome = resolve(tiles[index - 1], tiles[index]);
      if (outcome.ok) {
        combo += 1;
        score += mergeScore(outcome.tile.level, combo);
        keptFromEnd.push(outcome.tile);
        index -= 2;
        continue;
      }
      if (outcome.hint) hints.push(outcome.hint);
    }
    keptFromEnd.push(tiles[index]);
    index -= 1;
  }
  keptFromEnd.reverse();
  const padded = Array(SIZE - keptFromEnd.length).fill(null).concat(keptFromEnd);
  return { line: padded, combo, score, hints };
}

function applyDirection(grid, direction, resolve) {
  const next = emptyGrid();
  const hints = [];
  let score = 0;
  let combo = 0;
  if (direction === "left" || direction === "right") {
    const towardStart = direction === "left";
    for (let row = 0; row < SIZE; row += 1) {
      const slid = slideLine(grid[row], towardStart, resolve, combo);
      next[row] = slid.line;
      combo = slid.combo;
      score += slid.score;
      hints.push(...slid.hints);
    }
    return { grid: next, score, hints };
  }
  const towardStart = direction === "up";
  for (let col = 0; col < SIZE; col += 1) {
    const column = [];
    for (let row = 0; row < SIZE; row += 1) column.push(grid[row][col]);
    const slid = slideLine(column, towardStart, resolve, combo);
    combo = slid.combo;
    score += slid.score;
    hints.push(...slid.hints);
    for (let row = 0; row < SIZE; row += 1) next[row][col] = slid.line[row];
  }
  return { grid: next, score, hints };
}

function replacementKinds(consumed) {
  const kinds = [];
  for (const tile of consumed) {
    const kind = REPLACEMENT_KIND[tile.kind];
    if (!kind) continue;
    for (let count = 0; count < REPLACEMENTS_PER_PART; count += 1) kinds.push(kind);
  }
  return kinds;
}

export class Game {
  constructor(pack, stats = null, rng = Math.random) {
    this.pack = pack;
    this.stats = stats;
    this.rng = rng;
    this.grid = emptyGrid();
    this.score = 0;
    this.won = false;
    this.over = false;
    this.hints = [];
    this.sessionErrors = {};
    this.adverbsUnlocked = false;
    this.phrasesBuilt = 0;
    this.sentencesCollected = 0;
    this.tense = PRESENT;
    this.polarity = AFFIRMATIVE;
    this.objectsEnabled = false;
    this.notice = "";
    this.openingMode = null;
    this.shufflesLeft = 3;
    this.nextId = 1;
    this.lastStaticSignature = null;
    this.dealOpening();
    this.openingMode = [this.tense, this.polarity, this.objectsEnabled].join("|");
    this.updateOver();
  }

  newId() {
    const value = String(this.nextId);
    this.nextId += 1;
    return value;
  }

  occupied() {
    return tilesOf(this.grid).length;
  }

  clauseCount() {
    return tilesOf(this.grid).filter((cell) => cell.kind === "clause").length;
  }

  collectedSentences() {
    const onBoard = tilesOf(this.grid).filter((cell) => cell.kind === "sentence").length;
    return this.sentencesCollected + onBoard;
  }

  syncOpening() {
    if (this.score || this.phrasesBuilt || this.sentencesCollected) return;
    const signature = [this.tense, this.polarity, this.objectsEnabled].join("|");
    if (this.openingMode === signature) return;
    this.grid = emptyGrid();
    this.hints = [];
    this.over = false;
    this.lastStaticSignature = null;
    this.dealOpening();
    this.openingMode = signature;
    this.updateOver();
  }

  dealOpening() {
    const compound = this.tense === FUTURE || this.tense === PERFECT || this.tense === CONTINUOUS;
    if (this.polarity === QUESTION) {
      this.spawn("aux");
      this.spawn("subject");
      this.spawn("verb");
      return;
    }
    if (this.polarity === NEGATIVE || compound) {
      this.spawn("subject");
      this.spawn("aux");
      this.spawn("verb");
      return;
    }
    this.spawn("subject");
    this.spawn("verb");
    this.spawn(null);
  }

  move(direction) {
    if (!DIRECTIONS.includes(direction)) throw new Error(direction);
    if (this.over) return false;
    this.notice = "";
    this.pack.activeTense = this.tense;
    this.pack.activePolarity = this.polarity;
    const beforeTiles = new Map(tilesOf(this.grid).map((tile) => [tile.id, tile]));
    const beforeClauses = clauseIds(this.grid);
    const adverbsReady = this.adverbsUnlocked;
    const applied = applyDirection(this.grid, direction, this.resolver(direction, () => this.newId()));
    const changed = gridIds(applied.grid) !== gridIds(this.grid);
    this.grid = applied.grid;
    this.hints = applied.hints;
    this.score += applied.score;
    this.recordHints(applied.hints, changed);
    const afterClauses = clauseIds(this.grid);
    let built = 0;
    for (const id of afterClauses) {
      if (!beforeClauses.has(id)) built += 1;
    }
    this.phrasesBuilt += built;
    const madeGoal = tilesOf(this.grid).some((cell) => this.pack.isGoal(cell));
    if (this.phrasesBuilt >= this.pack.phrasesToUnlockAdverbs) this.adverbsUnlocked = true;
    const afterIds = new Set(tilesOf(this.grid).map((cell) => cell.id));
    const consumed = [];
    for (const [id, tile] of beforeTiles) {
      if (!afterIds.has(id)) consumed.push(tile);
    }
    const banked = this.bankSentences();
    if (madeGoal || banked) this.won = true;
    const kinds = this.balanceKinds(replacementKinds(consumed), adverbsReady);
    for (const kind of kinds) this.spawn(kind);
    if (adverbsReady) this.topUpAdverbs();
    this.updateOver();
    return changed;
  }

  shuffle() {
    if (this.shufflesLeft <= 0) return false;
    const tiles = tilesOf(this.grid);
    if (tiles.length < 2) return false;
    const before = gridIds(this.grid);
    for (let attempt = 0; attempt < 8; attempt += 1) {
      const order = tiles.slice();
      shuffle(this.rng, order);
      const spots = [];
      for (let row = 0; row < SIZE; row += 1) {
        for (let col = 0; col < SIZE; col += 1) spots.push([row, col]);
      }
      shuffle(this.rng, spots);
      const grid = emptyGrid();
      order.forEach((tile, index) => {
        const [row, col] = spots[index];
        grid[row][col] = tile;
      });
      if (gridIds(grid) !== before) {
        this.grid = grid;
        this.hints = [];
        this.notice = "";
        this.lastStaticSignature = null;
        this.shufflesLeft -= 1;
        this.updateOver();
        return true;
      }
    }
    return false;
  }

  topUpAdverbs() {
    if (!this.adverbsUnlocked || this.clauseCount() === 0) return;
    for (let step = 0; step < 2; step += 1) {
      const have = tilesOf(this.grid).filter((cell) => cell.kind === "adverb").length;
      if (have >= 2) return;
      const occupied = this.occupied();
      this.spawn("adverb");
      if (this.occupied() === occupied) return;
    }
  }

  spawn(kind = null) {
    const empties = [];
    for (let row = 0; row < SIZE; row += 1) {
      for (let col = 0; col < SIZE; col += 1) {
        if (!this.grid[row][col]) empties.push([row, col]);
      }
    }
    if (!empties.length) return;
    const specs = this.agreementSpecs(this.spawnPool(), kind);
    const weights = specs.map((spec) => effectiveWeight(spec, this.sessionErrors));
    const spec = weightedChoice(this.rng, specs, weights);
    const [row, col] = choice(this.rng, empties);
    this.grid[row][col] = {
      id: this.newId(),
      text: spec.text,
      kind: spec.kind,
      level: spec.level,
      lemma: spec.lemma,
      form: spec.form,
      person: spec.person,
      number: spec.number,
      tense: spec.tense,
    };
  }

  updateOver() {
    this.over = !this.hasMove();
  }

  hasMove() {
    const current = gridIds(this.grid);
    let probe = 0;
    const probeId = () => {
      probe += 1;
      return `probe-${probe}`;
    };
    for (const direction of DIRECTIONS) {
      const applied = applyDirection(this.grid, direction, this.resolver(direction, probeId));
      if (gridIds(applied.grid) !== current) return true;
    }
    return false;
  }

  spawnPool() {
    return this.pack.spawnSpecs.filter((spec) => this.specAllowed(spec));
  }

  specAllowed(spec) {
    if (spec.kind === "subject") return true;
    if (spec.kind === "verb") {
      if (this.tense === PAST && this.polarity === AFFIRMATIVE) return spec.form === "past";
      if (this.tense === PERFECT) return spec.form === "pp";
      if (this.tense === CONTINUOUS) return spec.form === "ing";
      if (this.tense === FUTURE) return spec.form === "base";
      if (this.polarity === AFFIRMATIVE) return spec.form === "base" || spec.form === "s";
      return spec.form === "base";
    }
    if (spec.kind === "adverb") return this.adverbsUnlocked && spec.tense === this.tense;
    if (spec.kind === "aux") return spec.tense === this.tense && spec.polarity === this.polarity;
    if (spec.kind === "object") return this.objectsEnabled;
    return false;
  }

  agreementSpecs(specs, kind) {
    let pool = specs;
    if (kind) {
      const narrowed = specs.filter((spec) => spec.kind === kind);
      if (narrowed.length) pool = narrowed;
    }
    const grouped = new Map();
    for (const spec of pool) {
      if (!grouped.has(spec.kind)) grouped.set(spec.kind, []);
      grouped.get(spec.kind).push(spec);
    }
    const chosen = [];
    for (const [specKind, group] of grouped) {
      const matched = this.matchSpawnKind(specKind, group);
      chosen.push(...(matched.length ? matched : group));
    }
    return chosen;
  }

  matchSpawnKind(kind, specs) {
    const tiles = tilesOf(this.grid);
    const subjects = tiles.filter((tile) => tile.kind === "subject");
    const verbs = tiles.filter((tile) => tile.kind === "verb");
    const partners = verbs.concat(tiles.filter((tile) => tile.kind === "aux"));
    if (kind === "verb" || kind === "aux") {
      if (!subjects.length) return specs;
      const present = new Set(partners.map((tile) => formGroup(tile.form)).filter(Boolean));
      if (present.has("any")) return specs;
      const missing = new Set();
      for (const subject of subjects) {
        const group = subjectNeedGroup(this.tense, subject);
        if (group !== "any" && !present.has(group)) missing.add(group);
      }
      const allowed = missing.size
        ? missing
        : new Set(subjects.map((subject) => subjectNeedGroup(this.tense, subject)).filter((group) => group !== "any"));
      if (!allowed.size) return specs;
      return specs.filter((spec) => allowed.has(formGroup(spec.form)) || formGroup(spec.form) === "any");
    }
    if (kind === "subject") {
      const groups = new Set(partners.map((tile) => formGroup(tile.form)).filter(Boolean));
      if (!groups.size || groups.has("any")) return specs;
      const have = new Set(subjects.map((subject) => subjectClass(subject)));
      const needed = new Set();
      for (const groupName of groups) {
        for (const cls of classesForGroup(groupName)) {
          if (!have.has(cls)) needed.add(cls);
        }
      }
      if (!needed.size) {
        for (const groupName of groups) {
          for (const cls of classesForGroup(groupName)) needed.add(cls);
        }
      }
      if (!needed.size) return specs;
      return specs.filter((spec) => needed.has(subjectClass(spec)));
    }
    return specs;
  }

  balanceKinds(kinds, adverbsReady) {
    kinds = kinds.slice();
    if (!kinds.length) return kinds;
    const count = {};
    for (const tile of tilesOf(this.grid)) count[tile.kind] = (count[tile.kind] || 0) + 1;
    const have = (kind) => count[kind] || 0;
    const ensure = (kind, minimum, candidates, keepLastSubject) => {
      while (have(kind) + kinds.filter((item) => item === kind).length < minimum) {
        let placed = false;
        for (const candidate of candidates) {
          const index = kinds.indexOf(candidate);
          if (index < 0) continue;
          const onlySubject =
            keepLastSubject &&
            candidate === "subject" &&
            have("subject") + kinds.filter((item) => item === "subject").length <= 1;
          if (onlySubject) continue;
          kinds[index] = kind;
          placed = true;
          break;
        }
        if (!placed) return;
      }
    };
    const subjectsWaiting = have("subject") > 0 || kinds.includes("subject");
    const compound = this.tense === FUTURE || this.tense === PERFECT || this.tense === CONTINUOUS;
    const needsAux = this.polarity === NEGATIVE || this.polarity === QUESTION || compound;
    if (this.polarity === AFFIRMATIVE && !compound && subjectsWaiting && have("verb") === 0) {
      const verbFrom = have("subject") > 0 ? ["subject", "object"] : ["object", "subject"];
      ensure("verb", 1, verbFrom, false);
    }
    if (needsAux && have("aux") === 0) {
      ensure("aux", 1, ["object", "subject", "verb"], true);
    }
    if (needsAux && have("verb") === 0) {
      ensure("verb", 1, ["object", "subject"], true);
    }
    if (adverbsReady && have("clause") > 0) {
      ensure("adverb", 2, ["object", "subject", "verb", "aux"], false);
    }
    if (this.objectsEnabled && have("clause") > 0) {
      ensure("object", 1, ["subject"], true);
    }
    return kinds;
  }

  bankSentences() {
    const found = [];
    for (let row = 0; row < SIZE; row += 1) {
      for (let col = 0; col < SIZE; col += 1) {
        const cell = this.grid[row][col];
        if (cell && cell.kind === "sentence") found.push([row, col]);
      }
    }
    if (found.length < this.pack.sentencesToBank) return 0;
    for (const [row, col] of found) this.grid[row][col] = null;
    this.sentencesCollected += found.length;
    this.notice = `${ruSentences(found.length)} сняты с поля. Собрано: ${this.sentencesCollected}.`;
    return found.length;
  }

  resolver(direction, newId) {
    const vertical = direction === "up" || direction === "down";
    this.pack.activeTense = this.tense;
    this.pack.activePolarity = this.polarity;
    const rules = activeRules(this);
    return (first, second) => {
      const direct = resolveMerge(first, second, rules, (left, right) => this.pack.nearMiss(left, right), newId);
      if (direct.ok || !vertical) return direct;
      const pair = new Set([first.kind, second.kind]);
      const swappable = [
        ["verb", "subject"],
        ["aux", "subject"],
        ["clause", "adverb"],
        ["chain", "verb"],
        ["negation", "verb"],
        ["question", "verb"],
      ].some(([leftKind, rightKind]) => pair.has(leftKind) && pair.has(rightKind) && pair.size === 2);
      if (!swappable) return direct;
      const swapped = resolveMerge(second, first, rules, (left, right) => this.pack.nearMiss(left, right), newId);
      if (swapped.ok || swapped.hint) return swapped;
      return direct;
    };
  }

  recordHints(hints, changed) {
    const signature = hints.map((item) => `${item.leftId}:${item.rightId}:${item.ruleId}`).join("|");
    if (!hints.length) {
      if (changed) this.lastStaticSignature = null;
      return;
    }
    if (changed || signature !== this.lastStaticSignature) {
      for (const item of hints) {
        this.sessionErrors[item.ruleId] = (this.sessionErrors[item.ruleId] || 0) + 1;
        if (this.stats) this.stats.record(item.ruleId);
      }
    }
    this.lastStaticSignature = changed ? null : signature;
  }
}

function subjectClass(tile) {
  if (is1sg(tile)) return "1sg";
  if (tile.person === 3 && tile.number === "sg") return "3sg";
  return "other";
}

function subjectNeedGroup(tense, subject) {
  if (tense === CONTINUOUS) {
    if (is1sg(subject)) return "am";
    if (is3sg(subject)) return "is";
    return "are";
  }
  if (tense === PAST || tense === FUTURE) return "any";
  return is3sg(subject) ? "s" : "base";
}

function classesForGroup(group) {
  if (group === "s" || group === "is") return ["3sg"];
  if (group === "am") return ["1sg"];
  if (group === "are") return ["other"];
  if (group === "base") return ["1sg", "other"];
  return [];
}

export { SIZE, PRESENT, PAST, FUTURE, PERFECT, CONTINUOUS, AFFIRMATIVE, NEGATIVE, QUESTION };
