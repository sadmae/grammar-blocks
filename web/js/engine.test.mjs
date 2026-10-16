import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { Game, createPack } from "./engine.mjs";

const lexicon = JSON.parse(readFileSync(new URL("../lexicon.json", import.meta.url), "utf8"));

function start() {
  return new Game(createPack(lexicon), null, Math.random);
}

function kinds(game) {
  return game.grid.flat().filter(Boolean).map((cell) => cell.kind);
}

function texts(game) {
  return game.grid.flat().filter(Boolean).map((cell) => cell.text);
}

function wipe(game) {
  for (let row = 0; row < game.grid.length; row += 1) {
    for (let col = 0; col < game.grid[row].length; col += 1) game.grid[row][col] = null;
  }
}

test("opening deals a subject and a verb", () => {
  const game = start();
  assert.equal(game.occupied(), 3);
  assert.equal(game.adverbsUnlocked, false);
  assert.ok(kinds(game).includes("subject"));
  assert.ok(kinds(game).includes("verb"));
  assert.ok(kinds(game).every((kind) => kind === "subject" || kind === "verb"));
});

test("present base and third person", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  game.grid[0][0] = pack.subject("I", "i");
  game.grid[0][1] = pack.verb("go", "base", "go");
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "I go");
  assert.equal(game.grid[0][0].kind, "clause");
  assert.equal(game.score, 40);

  wipe(game);
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.verb("go", "base", "go");
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /goes/);

  wipe(game);
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.verb("go", "s", "goes");
  game.move("left");
  assert.equal(game.grid[0][0].text, "she goes");
});

test("horizontal order stays strict and vertical subject can sit under the verb", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  game.grid[0][0] = pack.verb("go", "base", "go");
  game.grid[0][1] = pack.subject("I", "i");
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /порядок слов/);

  wipe(game);
  game.grid[0][0] = pack.verb("go", "base", "go");
  game.grid[1][0] = pack.subject("I", "i");
  game.move("up");
  assert.equal(game.grid[0][0].text, "I go");
});

test("an adverb above a clause merges vertically and stays blocked in a row", () => {
  const game = start();
  const pack = game.pack;
  const clause = {
    id: "calls",
    text: "Maria calls",
    kind: "clause",
    level: 2,
    tense: "present_simple",
    lemma: "call",
    form: null,
    person: 3,
    number: "sg",
  };
  wipe(game);
  game.grid[0][0] = pack.adverb("every morning", "morning");
  game.grid[1][0] = clause;
  game.move("up");
  assert.equal(game.grid[0][0].text, "Maria calls every morning");
  assert.equal(game.grid[0][0].kind, "sentence");

  wipe(game);
  game.grid[0][0] = pack.adverb("every morning", "morning");
  game.grid[0][1] = { ...clause, id: "calls2" };
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /после фразы/);
});

test("past simple asks for the second form", () => {
  const game = start();
  const pack = game.pack;
  game.tense = PAST;
  wipe(game);
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.verb("leave", "base", "leave");
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /left/);

  wipe(game);
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.verb("leave", "past", "left");
  game.move("left");
  assert.equal(game.grid[0][0].text, "she left");
});

test("negative and question build with a particle and a base verb", () => {
  const game = start();
  const pack = game.pack;
  game.polarity = "negative";
  wipe(game);
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.aux("dont", "dont");
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /doesn't/);

  wipe(game);
  game.grid[0][0] = pack.subject("I", "i");
  game.grid[0][1] = pack.aux("dont", "dont");
  game.move("left");
  const negation = game.grid.flat().find((cell) => cell && cell.text === "I don't");
  wipe(game);
  game.grid[0][0] = negation;
  game.grid[0][1] = pack.verb("go", "base", "go");
  game.move("left");
  assert.equal(game.grid[0][0].text, "I don't go");

  game.polarity = "question";
  wipe(game);
  game.grid[0][0] = pack.aux("do", "do");
  game.grid[0][1] = pack.subject("she", "she");
  assert.equal(game.move("left"), false);
  assert.match(game.hints[0].text, /Does/);

  wipe(game);
  game.grid[0][0] = pack.aux("does", "does");
  game.grid[0][1] = pack.subject("she", "she");
  game.move("left");
  const question = game.grid.flat().find((cell) => cell && cell.text === "Does she");
  wipe(game);
  game.grid[0][0] = question;
  game.grid[0][1] = pack.verb("go", "base", "go");
  game.move("left");
  assert.equal(game.grid[0][0].text, "Does she go");
});

test("object follows the clause", () => {
  const game = start();
  const pack = game.pack;
  game.objectsEnabled = true;
  wipe(game);
  game.grid[0][0] = {
    id: "clause",
    text: "she likes",
    kind: "clause",
    level: 2,
    tense: "present_simple",
    lemma: "like",
    form: null,
    person: 3,
    number: "sg",
  };
  game.grid[0][1] = pack.object("music", "music");
  game.move("left");
  assert.equal(game.grid[0][0].text, "she likes music");
  assert.equal(game.grid[0][0].kind, "clause");
});

test("two adverbs appear after the second phrase", () => {
  const game = start();
  const pack = game.pack;
  const builds = [
    ["I", "go", "base"],
    ["she", "like", "s"],
  ];
  wipe(game);
  builds.forEach(([subject, lemma, form], index) => {
    for (let row = 0; row < 5; row += 1) {
      for (let col = 0; col < 5; col += 1) {
        const cell = game.grid[row][col];
        if (cell && cell.kind !== "clause") game.grid[row][col] = null;
      }
    }
    game.grid[index][0] = pack.subject(subject, `s${index}`);
    game.grid[index][1] = pack.verb(lemma, form, `v${index}`);
    game.move("left");
  });
  assert.equal(game.adverbsUnlocked, true);
  assert.equal(kinds(game).includes("adverb"), false);

  for (let row = 0; row < 5; row += 1) {
    for (let col = 0; col < 5; col += 1) {
      const cell = game.grid[row][col];
      if (cell && cell.kind !== "clause") game.grid[row][col] = null;
    }
  }
  game.grid[2][0] = pack.subject("you", "you");
  game.grid[2][1] = pack.verb("read", "base", "read");
  game.move("left");
  assert.equal(kinds(game).filter((kind) => kind === "adverb").length, 2);
  assert.equal(kinds(game).filter((kind) => kind === "clause").length, 3);
});

test("a blocked slide still brings the second adverb", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  game.adverbsUnlocked = true;
  game.phrasesBuilt = 2;
  game.grid[0][0] = pack.adverb("usually", "usually");
  game.grid[1][1] = {
    id: "looks",
    text: "she looks",
    kind: "clause",
    level: 2,
    tense: "present_simple",
    lemma: "look",
    form: null,
    person: 3,
    number: "sg",
  };
  assert.equal(game.move("right"), true);
  assert.equal(game.score, 0);
  assert.equal(kinds(game).filter((kind) => kind === "adverb").length, 2);
});

test("three sentences are banked", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  const sentence = (text, id) => ({
    id,
    text,
    kind: "sentence",
    level: 3,
    tense: "present_simple",
    lemma: null,
    form: null,
    person: null,
    number: null,
  });
  game.grid[0][0] = sentence("I go often", "s1");
  game.grid[0][1] = sentence("we live usually", "s2");
  game.grid[1][0] = {
    id: "clause",
    text: "they play",
    kind: "clause",
    level: 2,
    tense: "present_simple",
    lemma: "play",
    form: null,
    person: 3,
    number: "pl",
  };
  game.grid[1][1] = pack.adverb("always", "always");
  game.move("left");
  assert.equal(game.sentencesCollected, 3);
  assert.equal(kinds(game).includes("sentence"), false);
  assert.match(game.notice, /3 предложения сняты с поля/);
});

test("an unplayed board redeals past verbs", () => {
  const game = start();
  assert.equal(game.score, 0);
  game.tense = "past_simple";
  game.syncOpening();
  const verbs = game.grid.flat().filter((cell) => cell && cell.kind === "verb");
  assert.ok(verbs.length >= 1);
  assert.ok(verbs.every((cell) => cell.form === "past"));
});

test("shuffle keeps the same tiles", () => {
  const game = start();
  const before = texts(game).sort();
  const occupied = game.occupied();
  assert.equal(game.shuffle(), true);
  assert.deepEqual(texts(game).sort(), before);
  assert.equal(game.occupied(), occupied);
  assert.equal(game.score, 0);
  assert.equal(game.shufflesLeft, 2);
});

test("a game allows only three shuffles", () => {
  const game = start();
  assert.equal(game.shuffle(), true);
  assert.equal(game.shuffle(), true);
  assert.equal(game.shuffle(), true);
  const frozen = game.grid.map((row) => row.map((cell) => (cell ? cell.id : null)));
  assert.equal(game.shufflesLeft, 0);
  assert.equal(game.shuffle(), false);
  assert.deepEqual(
    game.grid.map((row) => row.map((cell) => (cell ? cell.id : null))),
    frozen,
  );
});

test("two merges in one move raise the combo", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  game.grid[0][0] = pack.subject("I", "i");
  game.grid[0][1] = pack.verb("like", "base", "like");
  game.grid[0][2] = pack.subject("she", "she");
  game.grid[0][3] = pack.verb("play", "s", "plays");
  game.move("left");
  assert.equal(game.grid[0][0].text, "I like");
  assert.equal(game.grid[0][1].text, "she plays");
  assert.equal(game.score, 120);
});

test("future, perfect and continuous build the right chain", () => {
  const game = start();
  const pack = game.pack;
  wipe(game);
  game.tense = "future_simple";
  game.grid[0][0] = pack.subject("I", "i");
  game.grid[0][1] = pack.aux("will", "will");
  game.grid[0][2] = pack.verb("go", "base", "go");
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "I will");
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "I will go");

  wipe(game);
  game.score = 0;
  game.tense = "present_perfect";
  game.polarity = "negative";
  game.grid[0][0] = pack.subject("she", "she");
  game.grid[0][1] = pack.aux("hasnt", "hasnt");
  game.grid[0][2] = pack.verb("go", "base", "go");
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "she hasn't");
  assert.equal(game.move("left"), false);
  for (let row = 0; row < game.grid.length; row += 1) {
    for (let col = 0; col < game.grid[row].length; col += 1) {
      const cell = game.grid[row][col];
      if (cell && cell.kind === "verb") game.grid[row][col] = pack.verb("go", "pp", "gone");
    }
  }
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "she hasn't gone");

  wipe(game);
  game.tense = "present_continuous";
  game.polarity = "affirmative";
  game.grid[0][0] = pack.subject("you", "you");
  game.grid[0][1] = pack.aux("are", "are");
  game.grid[0][2] = pack.verb("work", "ing", "working");
  assert.equal(game.move("left"), true);
  assert.equal(game.move("left"), true);
  assert.equal(game.grid[0][0].text, "you are working");
});

const PAST = "past_simple";
