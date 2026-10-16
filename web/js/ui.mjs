import { Game, createPack } from "./engine.mjs";

const SAVE_KEY = "grammar-blocks-save";
const STATS_KEY = "grammar-blocks-stats";
const RECORD_KEY = "grammar-blocks-record";

const TENSE_OPTIONS = [
  ["present_simple", "Present Simple"],
  ["past_simple", "Past Simple"],
  ["future_simple", "Future Simple"],
  ["present_perfect", "Present Perfect"],
  ["present_continuous", "Present Continuous"],
];

const POLARITY_OPTIONS = [
  ["affirmative", "утверждение"],
  ["negative", "отрицание"],
  ["question", "вопрос"],
];

const KIND_CLASS = {
  subject: "tile-subject",
  verb: "tile-verb",
  adverb: "tile-adverb",
  aux: "tile-aux",
  object: "tile-object",
  negation: "tile-clause",
  question: "tile-clause",
  chain: "tile-clause",
  clause: "tile-clause",
  sentence: "tile-sentence",
};

const HANDBOOK = {
  "present_simple|affirmative": {
    title: "Present Simple, утверждение",
    rows: [
      [["tile-subject", "I / you / we / they"], ["tile-verb", "work"]],
      [["tile-subject", "he / she / it"], ["tile-verb", "works"]],
      [["tile-clause", "she likes"], ["tile-object", "music"], ["tile-adverb", "every day"]],
    ],
    text:
      "У I, you, we, they глагол без окончания: I work, you watch, they study, we live. " +
      "У he, she, it глагол с -s или -es: he works, she goes, it leaves. " +
      "Особые формы: have → has, do → does, study → studies.\n\n" +
      "Сначала собирается фраза: подлежащее и глагол. " +
      "Дополнение ставится сразу после неё: she likes music. " +
      "Обстоятельство замыкает предложение: she goes every day, they study usually.\n\n" +
      "Не собирается: he go, she leave, I goes, they works. " +
      "Обстоятельство и дополнение не ставятся перед фразой.",
  },
  "present_simple|negative": {
    title: "Present Simple, отрицание",
    rows: [
      [["tile-subject", "I / you / we / they"], ["tile-aux", "don't"], ["tile-verb", "work"]],
      [["tile-subject", "he / she / it"], ["tile-aux", "doesn't"], ["tile-verb", "go"]],
    ],
    text:
      "Сначала подлежащее и частица, потом глагол в первой форме, без -s.\n\n" +
      "I, you, we, they + don't: I don't work, they don't go. " +
      "he, she, it + doesn't: she doesn't go, he doesn't leave.\n\n" +
      "После don't и doesn't окончание -s не добавляется: she doesn't go, не she doesn't goes. " +
      "Не собирается: she don't work, I doesn't go.",
  },
  "present_simple|question": {
    title: "Present Simple, вопрос",
    rows: [
      [["tile-aux", "Do"], ["tile-subject", "I / you / we / they"], ["tile-verb", "work"]],
      [["tile-aux", "Does"], ["tile-subject", "he / she / it"], ["tile-verb", "go"]],
    ],
    text:
      "Вопрос начинается с частицы, подлежащее стоит после неё. Глагол снова в первой форме.\n\n" +
      "Do + I / you / we / they: Do you work? Do they study? " +
      "Does + he / she / it: Does she go? Does it leave?\n\n" +
      "Не собирается: Does you go, Do she work, Does he goes. " +
      "Вопрос не начинается с подлежащего.",
  },
  "past_simple|affirmative": {
    title: "Past Simple, утверждение",
    rows: [
      [["tile-subject", "I / they / she"], ["tile-verb", "left / went"]],
      [["tile-clause", "she liked"], ["tile-object", "music"], ["tile-adverb", "yesterday"]],
    ],
    text:
      "Любое подлежащее соединяется со второй формой глагола. Окончание -s здесь не используется.\n\n" +
      "Правильные глаголы получают -ed: watch → watched, play → played, study → studied. " +
      "Неправильные меняют основу: go → went, leave → left, see → saw, have → had, do → did.\n\n" +
      "I left, they went, she watched. " +
      "Дополнение после фразы: she liked music. " +
      "Обстоятельство прошедшего времени в конце: she went yesterday, they left last week.\n\n" +
      "Не собирается: they leave, I go, she goes. Это формы настоящего, не прошедшего.",
  },
  "past_simple|negative": {
    title: "Past Simple, отрицание",
    rows: [[["tile-subject", "I / she / they"], ["tile-aux", "didn't"], ["tile-verb", "go / leave"]]],
    text:
      "Подлежащее + didn't + первая форма глагола. Вторая форма после didn't не ставится.\n\n" +
      "I didn't go. She didn't leave. They didn't watch.\n\n" +
      "Не собирается: didn't went, didn't left, she didn't goes.",
  },
  "past_simple|question": {
    title: "Past Simple, вопрос",
    rows: [[["tile-aux", "Did"], ["tile-subject", "you / she / they"], ["tile-verb", "go / leave"]]],
    text:
      "Did стоит перед любым подлежащим. Глагол после него в первой форме.\n\n" +
      "Did you go? Did she leave? Did they watch?\n\n" +
      "Не собирается: Did she went, Did they left. Вопрос не начинается с подлежащего.",
  },
  "future_simple|affirmative": {
    title: "Future Simple, утверждение",
    rows: [
      [["tile-subject", "I / she / they"], ["tile-aux", "will"], ["tile-verb", "go"]],
      [["tile-clause", "she will go"], ["tile-adverb", "tomorrow"]],
    ],
    text:
      "Will стоит после любого подлежащего. Глагол после will в первой форме, без -s.\n\n" +
      "I will go. She will leave. They will watch.\n\n" +
      "Обстоятельство будущего в конце: she will go tomorrow.\n\n" +
      "Не собирается: she will goes, they will went.",
  },
  "future_simple|negative": {
    title: "Future Simple, отрицание",
    rows: [[["tile-subject", "I / she / they"], ["tile-aux", "won't"], ["tile-verb", "go"]]],
    text:
      "Won't + первая форма глагола.\n\n" +
      "I won't go. She won't leave. They won't watch.\n\n" +
      "Не собирается: won't went, won't goes.",
  },
  "future_simple|question": {
    title: "Future Simple, вопрос",
    rows: [[["tile-aux", "Will"], ["tile-subject", "you / she"], ["tile-verb", "go"]]],
    text:
      "Will стоит перед любым подлежащим. Глагол после него в первой форме.\n\n" +
      "Will you go? Will she leave?\n\n" +
      "Не собирается: Will she goes, Do she will.",
  },
  "present_perfect|affirmative": {
    title: "Present Perfect, утверждение",
    rows: [
      [["tile-subject", "I / you / we / they"], ["tile-aux", "have"], ["tile-verb", "gone"]],
      [["tile-subject", "he / she / it"], ["tile-aux", "has"], ["tile-verb", "seen"]],
      [["tile-clause", "she has seen"], ["tile-adverb", "already"]],
    ],
    text:
      "I, you, we, they + have + третья форма. he, she, it + has + третья форма.\n\n" +
      "I have gone. She has seen. They have written.\n\n" +
      "Обстоятельства: already, just, yet, ever, recently.\n\n" +
      "Не собирается: she have gone, he has went.",
  },
  "present_perfect|negative": {
    title: "Present Perfect, отрицание",
    rows: [
      [["tile-subject", "I / they"], ["tile-aux", "haven't"], ["tile-verb", "seen"]],
      [["tile-subject", "she"], ["tile-aux", "hasn't"], ["tile-verb", "gone"]],
    ],
    text:
      "haven't и hasn't стоят перед третьей формой.\n\n" +
      "I haven't seen. She hasn't gone.\n\n" +
      "Не собирается: she hasn't go, they haven't went.",
  },
  "present_perfect|question": {
    title: "Present Perfect, вопрос",
    rows: [
      [["tile-aux", "Have"], ["tile-subject", "you / they"], ["tile-verb", "gone"]],
      [["tile-aux", "Has"], ["tile-subject", "she"], ["tile-verb", "seen"]],
    ],
    text:
      "Have перед I, you, we, they. Has перед he, she, it. Глагол в третьей форме.\n\n" +
      "Have you gone? Has she seen?\n\n" +
      "Не собирается: Has you gone, Have she seen.",
  },
  "present_continuous|affirmative": {
    title: "Present Continuous, утверждение",
    rows: [
      [["tile-subject", "I"], ["tile-aux", "am"], ["tile-verb", "reading"]],
      [["tile-subject", "he / she / it"], ["tile-aux", "is"], ["tile-verb", "going"]],
      [["tile-subject", "you / we / they"], ["tile-aux", "are"], ["tile-verb", "watching"]],
    ],
    text:
      "I + am + форма с -ing. he, she, it + is + -ing. you, we, they + are + -ing.\n\n" +
      "I am reading. She is going. They are watching.\n\n" +
      "Обстоятельства: now, right now, at the moment.\n\n" +
      "Не собирается: she are going, I is reading, he going.",
  },
  "present_continuous|negative": {
    title: "Present Continuous, отрицание",
    rows: [
      [["tile-subject", "I"], ["tile-aux", "am not"], ["tile-verb", "reading"]],
      [["tile-subject", "she"], ["tile-aux", "isn't"], ["tile-verb", "going"]],
      [["tile-subject", "they"], ["tile-aux", "aren't"], ["tile-verb", "watching"]],
    ],
    text:
      "am not, isn't и aren't стоят перед формой с -ing.\n\n" +
      "I am not reading. She isn't going. They aren't watching.\n\n" +
      "Не собирается: she aren't going, I isn't reading.",
  },
  "present_continuous|question": {
    title: "Present Continuous, вопрос",
    rows: [
      [["tile-aux", "Am"], ["tile-subject", "I"], ["tile-verb", "reading"]],
      [["tile-aux", "Is"], ["tile-subject", "she"], ["tile-verb", "going"]],
      [["tile-aux", "Are"], ["tile-subject", "they"], ["tile-verb", "watching"]],
    ],
    text:
      "Am перед I, Is перед he/she/it, Are перед you/we/they. Глагол с -ing.\n\n" +
      "Am I reading? Is she going? Are they watching?\n\n" +
      "Не собирается: Are she going, Is I reading.",
  },
};

const board = document.querySelector("#board");
const seenIds = new Set();
let handbookKey = "";
let record = 0;
let freshRecord = false;
let game;
let pack;
let stats;
let installPrompt = null;

class LocalStats {
  constructor() {
    this.errors = {};
    try {
      const saved = JSON.parse(localStorage.getItem(STATS_KEY) || "{}");
      if (saved.errors && typeof saved.errors === "object") this.errors = saved.errors;
    } catch {
      this.errors = {};
    }
  }

  record(ruleId) {
    this.errors[ruleId] = (this.errors[ruleId] || 0) + 1;
    try {
      localStorage.setItem(STATS_KEY, JSON.stringify({ errors: this.errors }));
    } catch {
      /* частный режим может запретить запись */
    }
  }
}

function stageText() {
  const lines = {
    "negative|past_simple": "Отрицание: подлежащее + didn't + глагол без -s.",
    "negative|present_simple": "Отрицание: I/you/we/they + don't, he/she/it + doesn't, потом глагол без -s.",
    "negative|future_simple": "Отрицание: подлежащее + won't + глагол без -s.",
    "negative|present_perfect": "Отрицание: haven't / hasn't + третья форма.",
    "negative|present_continuous": "Отрицание: am not / isn't / aren't + форма с -ing.",
    "question|past_simple": "Вопрос: Did + подлежащее + глагол без -s.",
    "question|present_simple": "Вопрос: Do + I/you/we/they, Does + he/she/it, потом глагол без -s.",
    "question|future_simple": "Вопрос: Will + подлежащее + глагол без -s.",
    "question|present_perfect": "Вопрос: Have / Has + подлежащее + третья форма.",
    "question|present_continuous": "Вопрос: Am / Is / Are + подлежащее + форма с -ing.",
    "affirmative|past_simple": "Past Simple: подлежащее + вторая форма. Обстоятельство после фразы: she went yesterday.",
    "affirmative|future_simple": "Future Simple: подлежащее + will + глагол без -s. She will go tomorrow.",
    "affirmative|present_perfect": "Present Perfect: have/has + третья форма. She has gone already.",
    "affirmative|present_continuous": "Present Continuous: am/is/are + -ing. She is reading now.",
  };
  let mode = lines[`${game.polarity}|${game.tense}`];
  if (!mode && game.adverbsUnlocked) {
    mode = "Обстоятельства открыты. Поставьте их после фразы: she goes every day.";
  }
  if (!mode) {
    const need = game.pack.phrasesToUnlockAdverbs;
    mode = `Пока выпадают только подлежащие и глаголы. Собрано фраз: ${game.phrasesBuilt}/${need}.`;
  }
  if (game.objectsEnabled) mode += " Дополнение ставится после фразы: she likes music.";
  return mode;
}

function save() {
  const payload = {
    grid: game.grid,
    score: game.score,
    won: game.won,
    over: game.over,
    hints: game.hints,
    sessionErrors: game.sessionErrors,
    adverbsUnlocked: game.adverbsUnlocked,
    phrasesBuilt: game.phrasesBuilt,
    sentencesCollected: game.sentencesCollected,
    tense: game.tense,
    polarity: game.polarity,
    objectsEnabled: game.objectsEnabled,
    notice: game.notice,
    openingMode: game.openingMode,
    nextId: game.nextId,
    lastStaticSignature: game.lastStaticSignature,
    shufflesLeft: game.shufflesLeft,
  };
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(payload));
  } catch {
    /* партия просто не сохранится между визитами */
  }
}

function loadOrCreate() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return new Game(pack, stats);
    const data = JSON.parse(raw);
    if (!Array.isArray(data.grid) || data.grid.length !== 5) return new Game(pack, stats);
    const restored = new Game(pack, stats);
    Object.assign(restored, data);
    restored.pack.activeTense = restored.tense;
    restored.pack.activePolarity = restored.polarity;
    restored.topUpAdverbs();
    restored.updateOver();
    if (typeof restored.shufflesLeft !== "number") restored.shufflesLeft = 3;
    return restored;
  } catch {
    return new Game(pack, stats);
  }
}

function button(label, selected, onClick) {
  const node = document.createElement("button");
  node.type = "button";
  node.className = selected ? "pill is-on" : "pill";
  node.textContent = label;
  node.setAttribute("aria-pressed", selected ? "true" : "false");
  node.addEventListener("click", onClick);
  return node;
}

function renderModes() {
  const tense = document.querySelector("#tense-modes");
  const play = document.querySelector("#play-modes");
  tense.replaceChildren();
  play.replaceChildren();
  for (const [value, label] of TENSE_OPTIONS) {
    tense.append(button(label, game.tense === value, () => chooseMode({ tense: value })));
  }
  for (const [value, label] of POLARITY_OPTIONS) {
    play.append(button(label, game.polarity === value, () => chooseMode({ polarity: value })));
  }
  play.append(button("дополнение", game.objectsEnabled, () => chooseMode({ objectsEnabled: !game.objectsEnabled })));
}

function chooseMode(change) {
  if (change.tense && change.tense !== game.tense) game.tense = change.tense;
  else if (change.polarity && change.polarity !== game.polarity) game.polarity = change.polarity;
  else if (Object.prototype.hasOwnProperty.call(change, "objectsEnabled")) {
    game.objectsEnabled = change.objectsEnabled;
  } else {
    return;
  }
  game.pack.activeTense = game.tense;
  game.pack.activePolarity = game.polarity;
  game.syncOpening();
  game.topUpAdverbs();
  save();
  render();
}

function renderBoard() {
  const cells = [];
  const current = new Set();
  for (const row of game.grid) {
    for (const tile of row) {
      const cell = document.createElement("div");
      cell.setAttribute("role", "gridcell");
      if (!tile) {
        cell.className = "cell cell-empty";
        cell.setAttribute("aria-label", "пусто");
      } else {
        current.add(tile.id);
        const kind = KIND_CLASS[tile.kind] || "tile-verb";
        cell.className = `cell ${kind}`;
        if (!seenIds.has(tile.id)) cell.classList.add("tile-new");
        const span = document.createElement("span");
        span.textContent = tile.text;
        cell.append(span);
        cell.setAttribute("aria-label", tile.text);
      }
      cells.push(cell);
    }
  }
  board.replaceChildren(...cells);
  seenIds.clear();
  for (const id of current) seenIds.add(id);
}

function showBox(id, text, extraClass) {
  const node = document.querySelector(id);
  if (!text) {
    node.hidden = true;
    node.textContent = "";
    return;
  }
  node.hidden = false;
  node.className = extraClass;
  node.textContent = text;
}

function formula(rows) {
  const wrap = document.createElement("div");
  for (const row of rows) {
    const line = document.createElement("div");
    line.className = "formula";
    row.forEach(([kind, text], index) => {
      if (index) {
        const plus = document.createElement("span");
        plus.className = "plus";
        plus.textContent = "+";
        line.append(plus);
      }
      const chip = document.createElement("span");
      chip.className = `chip ${kind}`;
      chip.textContent = text;
      line.append(chip);
    });
    wrap.append(line);
  }
  return wrap;
}

function renderHandbook() {
  const body = document.querySelector("#handbook-body");
  body.replaceChildren();
  const intro = document.createElement("p");
  intro.textContent =
    "Предложение собирается по порядку: подлежащее → глагол → дополнение → обстоятельство. " +
    "На поле этот порядок идёт слева направо. Подлежащее и глагол собираются и по вертикали, даже если глагол оказался сверху. " +
    "Фраза и обстоятельство тоже собираются по вертикали, даже если обстоятельство оказалось сверху. " +
    "В вопросе порядок другой: сначала частица, потом подлежащее.";
  body.append(intro);
  const key = `${game.tense}|${game.polarity}`;
  body.append(scheme(HANDBOOK[key]));
  const rest = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = "Все схемы";
  rest.append(summary);
  for (const [other, page] of Object.entries(HANDBOOK)) {
    if (other === key) continue;
    rest.append(scheme(page));
  }
  body.append(rest);
}

function scheme(page) {
  const block = document.createElement("section");
  block.className = "scheme";
  const title = document.createElement("h2");
  title.textContent = page.title;
  const text = document.createElement("p");
  text.textContent = page.text;
  block.append(title, formula(page.rows), text);
  return block;
}

function renderLegend() {
  const legend = document.querySelector("#legend");
  const items = [
    ["tile-subject", "подлежащее"],
    ["tile-verb", "глагол"],
    ["tile-adverb", "обстоятельство"],
    ["tile-aux", "частица"],
    ["tile-object", "дополнение"],
    ["tile-clause", "фраза"],
    ["tile-sentence", "предложение"],
  ];
  legend.replaceChildren(
    ...items.map(([kind, label]) => {
      const span = document.createElement("span");
      span.className = kind;
      span.textContent = label;
      return span;
    }),
  );
}

function overText() {
  if (game.shufflesLeft > 0) {
    return `Ходов больше нет. Осталось перемешиваний: ${game.shufflesLeft}.`;
  }
  return "Ходов больше нет. Перемешивания закончились. Начните новую партию.";
}

function noteRecord() {
  if (game.score > record) {
    record = game.score;
    freshRecord = true;
    try {
      localStorage.setItem(RECORD_KEY, String(record));
    } catch {
      /* рекорд останется до обновления страницы */
    }
  }
}

function render() {
  noteRecord();
  document.querySelector("#score").textContent = String(game.score);
  document.querySelector("#record").textContent = String(record);
  document.querySelector("#collected").textContent = String(game.collectedSentences());
  const shuffle = document.querySelector("#shuffle");
  shuffle.textContent = `Перемешать · ${game.shufflesLeft}`;
  shuffle.disabled = game.shufflesLeft <= 0;
  document.querySelector("#status").textContent = stageText();
  showBox("#record-banner", freshRecord ? `Новый рекорд: ${record}` : "", "banner");
  showBox("#notice", game.over ? overText() : game.notice, game.over ? "banner over" : "banner");
  showBox("#hint", game.hints.map((item) => item.text).join(" "), "banner hint");
  renderModes();
  renderBoard();
  const key = `${game.tense}|${game.polarity}`;
  if (key !== handbookKey) {
    handbookKey = key;
    renderHandbook();
  }
}

function play(direction) {
  game.move(direction);
  save();
  render();
}

function restart() {
  const tense = game.tense;
  const polarity = game.polarity;
  const objectsEnabled = game.objectsEnabled;
  try {
    localStorage.removeItem(SAVE_KEY);
  } catch {
    /* новая партия всё равно начнётся в памяти */
  }
  game = new Game(pack, stats);
  game.tense = tense;
  game.polarity = polarity;
  game.objectsEnabled = objectsEnabled;
  game.pack.activeTense = tense;
  game.pack.activePolarity = polarity;
  game.syncOpening();
  seenIds.clear();
  freshRecord = false;
  save();
  render();
}

function bind() {
  document.querySelector("#shuffle").addEventListener("click", () => {
    if (!game.shuffle()) return;
    save();
    render();
  });
  document.querySelector("#restart").addEventListener("click", restart);
  window.addEventListener("keydown", (event) => {
    const dirs = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" };
    const dir = dirs[event.key];
    if (!dir) return;
    event.preventDefault();
    play(dir);
  });

  let start = null;
  board.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    start = { x: event.clientX, y: event.clientY, id: event.pointerId };
    board.setPointerCapture(event.pointerId);
  });
  board.addEventListener("pointerup", (event) => {
    if (!start || event.pointerId !== start.id) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    start = null;
    if (Math.hypot(dx, dy) < 28) return;
    play(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "right" : "left") : (dy > 0 ? "down" : "up"));
  });
  board.addEventListener("pointercancel", () => {
    start = null;
  });

  const standalone =
    window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  if (standalone) document.querySelector("#install-box").hidden = true;
  document.querySelector("#install").addEventListener("click", async () => {
    if (!installPrompt) return;
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
    document.querySelector("#install").hidden = true;
  });
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    document.querySelector("#install").hidden = false;
    document.querySelector("#install-fallback").hidden = true;
  });
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
}

const response = await fetch(new URL("../lexicon.json", import.meta.url));
pack = createPack(await response.json());
stats = new LocalStats();
game = loadOrCreate();
save();
record = Number(localStorage.getItem(RECORD_KEY) || 0);
if (!Number.isFinite(record)) record = 0;
renderLegend();
bind();
render();
