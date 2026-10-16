import random
from collections import Counter

from game.merge import Hint, merge_score, resolve_merge
from game.stats import ErrorStats, effective_weight
from game.tile import Tile

SIZE = 5
ENGINE_REVISION = 6
SHUFFLES_PER_GAME = 3
DIRECTIONS = ("left", "right", "up", "down")
Grid = list[list[Tile | None]]


class Game:
    def __init__(
        self,
        pack,
        stats: ErrorStats,
        rng: random.Random | None = None,
        spawn_start: bool = True,
    ):
        self.pack = pack
        self.stats = stats
        self.rng = rng or random.Random()
        self.grid: Grid = _empty()
        self.score = 0
        self.won = False
        self.over = False
        self.hints: list[Hint] = []
        self.session_errors: Counter[str] = Counter()
        self.adverbs_unlocked = False
        self.phrases_built = 0
        self.sentences_collected = 0
        self.tense = "present_simple"
        self.polarity = "affirmative"
        self.objects_enabled = False
        self.notice = ""
        self.opening_mode: tuple | None = None
        self.shuffles_left = SHUFFLES_PER_GAME
        self._next_id = 1
        self._last_static_signature: tuple | None = None
        if spawn_start:
            self._deal_opening()
            self.opening_mode = (self.tense, self.polarity, self.objects_enabled)
            self.update_over()

    def new_id(self) -> str:
        value = str(self._next_id)
        self._next_id += 1
        return value

    def clear(self) -> None:
        self.grid = _empty()
        self.hints = []
        self.over = False
        self.adverbs_unlocked = False
        self.phrases_built = 0
        self.sentences_collected = 0
        self.notice = ""
        self._last_static_signature = None

    def sync_opening(self) -> None:
        self.ensure_state()
        if self.score or self.phrases_built or self.sentences_collected:
            return
        signature = (self.tense, self.polarity, self.objects_enabled)
        if self.opening_mode == signature:
            return
        self.grid = _empty()
        self.hints = []
        self.over = False
        self._last_static_signature = None
        self._deal_opening()
        self.opening_mode = signature
        self.update_over()

    def _deal_opening(self) -> None:
        if self.polarity == "question":
            self.spawn(kind="aux")
            self.spawn(kind="subject")
            self.spawn(kind="verb")
            return
        if self.polarity == "negative" or self.tense in _COMPOUND_TENSES:
            self.spawn(kind="subject")
            self.spawn(kind="aux")
            self.spawn(kind="verb")
            return
        self.spawn(kind="subject")
        self.spawn(kind="verb")
        self.spawn()

    def occupied(self) -> int:
        return sum(cell is not None for row in self.grid for cell in row)

    def ensure_state(self) -> None:
        if not hasattr(self, "sentences_collected"):
            self.sentences_collected = 0
        if not hasattr(self, "tense"):
            self.tense = "present_simple"
        if not hasattr(self, "polarity"):
            self.polarity = "affirmative"
        if not hasattr(self, "objects_enabled"):
            self.objects_enabled = False
        if not hasattr(self, "notice"):
            self.notice = ""
        if not hasattr(self, "opening_mode"):
            self.opening_mode = None
        if not hasattr(self, "shuffles_left"):
            self.shuffles_left = SHUFFLES_PER_GAME

    def move(self, direction: str) -> bool:
        if direction not in DIRECTIONS:
            raise ValueError(direction)
        if self.over:
            return False
        self.ensure_state()
        self.notice = ""
        self.pack.active_tense = self.tense
        self.pack.active_polarity = self.polarity
        before_tiles = _tiles_by_id(self.grid)
        before_clauses = _clause_ids(self.grid)
        adverbs_ready = self.adverbs_unlocked
        new_grid, score_delta, hints = apply_direction(
            self.grid, direction, self._resolver(direction, self.new_id)
        )
        changed = _ids(new_grid) != _ids(self.grid)
        self.grid = new_grid
        self.hints = hints
        self.score += score_delta
        self._record_hints(hints, changed)
        self.phrases_built += len(_clause_ids(self.grid) - before_clauses)
        made_goal = any(self.pack.is_goal(cell) for row in self.grid for cell in row if cell)
        self._update_stage()
        after_ids = {cell.id for row in self.grid for cell in row if cell}
        consumed = [tile for tile_id, tile in before_tiles.items() if tile_id not in after_ids]
        banked = self._bank_sentences()
        if made_goal or banked:
            self.won = True
        kinds = self._balance_kinds(_replacement_kinds(consumed), adverbs_ready)
        for kind in kinds:
            self.spawn(kind=kind)
        if adverbs_ready:
            self.top_up_adverbs()
        self.update_over()
        return changed

    def shuffle(self) -> bool:
        self.ensure_state()
        if self.shuffles_left <= 0:
            return False
        tiles = [cell for row in self.grid for cell in row if cell is not None]
        if len(tiles) < 2:
            return False
        before = _ids(self.grid)
        for _ in range(8):
            order = list(tiles)
            self.rng.shuffle(order)
            spots = [(row, col) for row in range(SIZE) for col in range(SIZE)]
            self.rng.shuffle(spots)
            grid = _empty()
            for tile, (row, col) in zip(order, spots):
                grid[row][col] = tile
            if _ids(grid) != before:
                self.grid = grid
                self.hints = []
                self.notice = ""
                self._last_static_signature = None
                self.shuffles_left -= 1
                self.update_over()
                return True
        return False

    def top_up_adverbs(self) -> None:
        if not self.adverbs_unlocked or self.clause_count() == 0:
            return
        for _ in range(2):
            have = sum(
                cell is not None and cell.kind == "adverb"
                for row in self.grid
                for cell in row
            )
            if have >= 2:
                return
            occupied = self.occupied()
            self.spawn(kind="adverb")
            if self.occupied() == occupied:
                return

    def spawn(self, kind: str | None = None) -> None:
        empties = [
            (row, col)
            for row in range(SIZE)
            for col in range(SIZE)
            if self.grid[row][col] is None
        ]
        if not empties:
            return
        specs = self._agreement_specs(self.spawn_pool(), kind)
        weights = [effective_weight(spec, self.session_errors) for spec in specs]
        spec = self.rng.choices(specs, weights=weights, k=1)[0]
        row, col = self.rng.choice(empties)
        self.grid[row][col] = spec.to_tile(self.new_id())

    def update_over(self) -> None:
        self.over = not self.has_move()

    def has_move(self) -> bool:
        current = _ids(self.grid)
        probe = {"n": 0}

        def probe_id() -> str:
            probe["n"] += 1
            return f"probe-{probe['n']}"

        for direction in DIRECTIONS:
            new_grid, _, _ = apply_direction(
                self.grid, direction, self._resolver(direction, probe_id)
            )
            if _ids(new_grid) != current:
                return True
        return False

    def clause_count(self) -> int:
        return sum(
            cell is not None and cell.kind == "clause"
            for row in self.grid
            for cell in row
        )

    def _agreement_specs(self, specs: list, kind: str | None) -> list:
        if kind is not None:
            narrowed = [spec for spec in specs if spec.kind == kind]
            if narrowed:
                specs = narrowed
        grouped: dict[str, list] = {}
        for spec in specs:
            grouped.setdefault(spec.kind, []).append(spec)
        chosen = []
        for spec_kind, group in grouped.items():
            matched = self._match_spawn_kind(spec_kind, group)
            chosen.extend(matched or group)
        return chosen

    def _match_spawn_kind(self, kind: str, specs: list) -> list:
        tiles = [cell for row in self.grid for cell in row if cell is not None]
        subjects = [tile for tile in tiles if tile.kind == "subject"]
        verbs = [tile for tile in tiles if tile.kind == "verb"]
        partners = verbs + [tile for tile in tiles if tile.kind == "aux"]
        if kind in {"verb", "aux"}:
            if not subjects:
                return specs
            present = {_form_group(tile.form) for tile in partners}
            present.discard(None)
            if "any" in present:
                return specs
            missing = set()
            for subject in subjects:
                group = _subject_need_group(self.tense, subject)
                if group != "any" and group not in present:
                    missing.add(group)
            allowed = missing or {
                _subject_need_group(self.tense, subject) for subject in subjects
            }
            allowed.discard("any")
            if not allowed:
                return specs
            return [
                spec
                for spec in specs
                if _form_group(spec.form) in allowed or _form_group(spec.form) == "any"
            ]
        if kind == "subject":
            groups = {_form_group(tile.form) for tile in partners}
            groups.discard(None)
            if not groups or "any" in groups:
                return specs
            have = {_subject_class(subject) for subject in subjects}
            needed: set[str] = set()
            for group_name in groups:
                for cls in _classes_for_group(group_name):
                    if cls not in have:
                        needed.add(cls)
            if not needed:
                for group_name in groups:
                    needed.update(_classes_for_group(group_name))
            if not needed:
                return specs
            return [spec for spec in specs if _subject_class(spec) in needed]
        return specs

    def collected_sentences(self) -> int:
        on_board = sum(
            cell is not None and cell.kind == "sentence"
            for row in self.grid
            for cell in row
        )
        return self.sentences_collected + on_board

    def spawn_pool(self) -> list:
        return [spec for spec in self.pack.spawn_specs if self._spec_allowed(spec)]

    def _spec_allowed(self, spec) -> bool:
        if spec.kind == "subject":
            return True
        if spec.kind == "verb":
            if self.tense == "past_simple" and self.polarity == "affirmative":
                return spec.form == "past"
            if self.tense == "present_perfect":
                return spec.form == "pp"
            if self.tense == "present_continuous":
                return spec.form == "ing"
            if self.tense == "future_simple":
                return spec.form == "base"
            if self.polarity == "affirmative":
                return spec.form in {"base", "s"}
            return spec.form == "base"
        if spec.kind == "adverb":
            return self.adverbs_unlocked and spec.tense == self.tense
        if spec.kind == "aux":
            return spec.tense == self.tense and spec.polarity == self.polarity
        if spec.kind == "object":
            return self.objects_enabled
        return False

    def _balance_kinds(self, kinds: list[str], adverbs_ready: bool) -> list[str]:
        kinds = list(kinds)
        if not kinds:
            return kinds
        count = Counter(cell.kind for row in self.grid for cell in row if cell is not None)

        def ensure(
            kind: str,
            minimum: int,
            candidates: tuple[str, ...],
            keep_last_subject: bool,
        ) -> None:
            while count[kind] + kinds.count(kind) < minimum:
                placed = False
                for candidate in candidates:
                    if candidate not in kinds:
                        continue
                    only_subject = (
                        keep_last_subject
                        and candidate == "subject"
                        and count["subject"] + kinds.count("subject") <= 1
                    )
                    if only_subject:
                        continue
                    kinds[kinds.index(candidate)] = kind
                    placed = True
                    break
                if not placed:
                    return

        subjects_waiting = count["subject"] > 0 or "subject" in kinds
        compound = self.tense in _COMPOUND_TENSES
        needs_aux = self.polarity in {"negative", "question"} or compound
        if self.polarity == "affirmative" and not compound and subjects_waiting and count["verb"] == 0:
            verb_from = ("subject", "object") if count["subject"] > 0 else ("object", "subject")
            ensure("verb", 1, verb_from, keep_last_subject=False)
        if needs_aux and count["aux"] == 0:
            ensure("aux", 1, ("object", "subject", "verb"), keep_last_subject=True)
        if needs_aux and count["verb"] == 0:
            ensure("verb", 1, ("object", "subject"), keep_last_subject=True)
        if adverbs_ready and count["clause"] > 0:
            ensure("adverb", 2, ("object", "subject", "verb", "aux"), keep_last_subject=False)
        if self.objects_enabled and count["clause"] > 0:
            ensure("object", 1, ("subject",), keep_last_subject=True)
        return kinds

    def _bank_sentences(self) -> int:
        found = [
            (row, col)
            for row in range(SIZE)
            for col in range(SIZE)
            if self.grid[row][col] is not None and self.grid[row][col].kind == "sentence"
        ]
        need = self.pack.sentences_to_bank
        if len(found) < need:
            return 0
        for row, col in found:
            self.grid[row][col] = None
        self.sentences_collected += len(found)
        self.notice = (
            f"{_ru_sentences(len(found))} сняты с поля. "
            f"Собрано: {self.sentences_collected}."
        )
        return len(found)

    def _update_stage(self) -> None:
        need = self.pack.phrases_to_unlock_adverbs
        if self.phrases_built >= need:
            self.adverbs_unlocked = True

    def spawn_weights(self) -> list[float]:
        return [effective_weight(spec, self.session_errors) for spec in self.pack.spawn_specs]

    def weak_topics(self) -> list[dict]:
        rule_ids = set(self.session_errors) | set(self.stats.errors)
        topics = []
        for rule_id in rule_ids:
            session_count = self.session_errors.get(rule_id, 0)
            total = self.stats.count(rule_id)
            if session_count == 0 and total == 0:
                continue
            topics.append(
                {
                    "id": rule_id,
                    "label": self.pack.topic_label(rule_id),
                    "count": session_count,
                    "total": total,
                    "boosted": session_count >= 3 and rule_id in self.pack.adaptive_rules,
                }
            )
        topics.sort(key=lambda item: (-item["count"], -item["total"], item["id"]))
        return topics

    def _resolver(self, direction: str, new_id):
        vertical = direction in ("up", "down")

        self.pack.active_tense = self.tense
        self.pack.active_polarity = self.polarity
        rules = _active_rules(self)

        def resolve(first: Tile, second: Tile):
            direct = resolve_merge(first, second, rules, self.pack.near_miss, new_id)
            if direct.ok or not vertical:
                return direct
            pair = {first.kind, second.kind}
            if pair not in _VERTICAL_PAIRS:
                return direct
            swapped = resolve_merge(second, first, rules, self.pack.near_miss, new_id)
            if swapped.ok or swapped.hint:
                return swapped
            return direct

        return resolve

    def _record_hints(self, hints: list[Hint], changed: bool) -> None:
        signature = tuple((hint.left_id, hint.right_id, hint.rule_id) for hint in hints)
        if not hints:
            if changed:
                self._last_static_signature = None
            return
        if changed or signature != self._last_static_signature:
            for hint in hints:
                self.session_errors[hint.rule_id] += 1
                self.stats.record(hint.rule_id)
        if changed:
            self._last_static_signature = None
        else:
            self._last_static_signature = signature


def apply_direction(grid: Grid, direction: str, resolve) -> tuple[Grid, int, list[Hint]]:
    new_grid = _empty()
    hints: list[Hint] = []
    score = 0
    combo = 0
    if direction in ("left", "right"):
        toward_start = direction == "left"
        for row in range(SIZE):
            line, combo, delta, line_hints = slide_line(
                grid[row], toward_start, resolve, combo
            )
            new_grid[row] = line
            score += delta
            hints.extend(line_hints)
        return new_grid, score, hints

    toward_start = direction == "up"
    for col in range(SIZE):
        column = [grid[row][col] for row in range(SIZE)]
        line, combo, delta, line_hints = slide_line(column, toward_start, resolve, combo)
        for row in range(SIZE):
            new_grid[row][col] = line[row]
        score += delta
        hints.extend(line_hints)
    return new_grid, score, hints


def slide_line(cells, toward_start: bool, resolve, combo: int):
    tiles = [cell for cell in cells if cell is not None]
    hints: list[Hint] = []
    score = 0
    if toward_start:
        index = 0
        kept: list[Tile] = []
        while index < len(tiles):
            if index + 1 < len(tiles):
                outcome = resolve(tiles[index], tiles[index + 1])
                if outcome.ok:
                    combo += 1
                    score += merge_score(outcome.tile.level, combo)
                    kept.append(outcome.tile)
                    index += 2
                    continue
                if outcome.hint:
                    hints.append(outcome.hint)
            kept.append(tiles[index])
            index += 1
        padded = kept + [None] * (SIZE - len(kept))
        return padded, combo, score, hints

    index = len(tiles) - 1
    kept_from_end: list[Tile] = []
    while index >= 0:
        if index - 1 >= 0:
            outcome = resolve(tiles[index - 1], tiles[index])
            if outcome.ok:
                combo += 1
                score += merge_score(outcome.tile.level, combo)
                kept_from_end.append(outcome.tile)
                index -= 2
                continue
            if outcome.hint:
                hints.append(outcome.hint)
        kept_from_end.append(tiles[index])
        index -= 1
    kept_from_end.reverse()
    padded = [None] * (SIZE - len(kept_from_end)) + kept_from_end
    return padded, combo, score, hints


def _empty() -> Grid:
    return [[None for _ in range(SIZE)] for _ in range(SIZE)]


def _tiles_by_id(grid: Grid) -> dict[str, Tile]:
    return {cell.id: cell for row in grid for cell in row if cell is not None}


REPLACEMENT_KIND = {
    "subject": "subject",
    "verb": "verb",
    "adverb": "adverb",
    "clause": "subject",
    "aux": "aux",
    "object": "object",
    "negation": "aux",
    "question": "aux",
    "chain": "aux",
}

_FORM_GROUP = {
    "base": "base",
    "s": "s",
    "dont": "base",
    "do": "base",
    "doesnt": "s",
    "does": "s",
    "past": "any",
    "didnt": "any",
    "did": "any",
    "ing": "any",
    "pp": "any",
    "will": "any",
    "wont": "any",
    "willq": "any",
    "have": "base",
    "havent": "base",
    "haveq": "base",
    "has": "s",
    "hasnt": "s",
    "hasq": "s",
    "am": "am",
    "amnot": "am",
    "amq": "am",
    "is": "is",
    "isnt": "is",
    "isq": "is",
    "are": "are",
    "arent": "are",
    "areq": "are",
}

_COMPOUND_TENSES = frozenset({"future_simple", "present_perfect", "present_continuous"})
_VERTICAL_PAIRS = (
    {"verb", "subject"},
    {"aux", "subject"},
    {"clause", "adverb"},
    {"chain", "verb"},
    {"negation", "verb"},
    {"question", "verb"},
)
_BASE_AFTER_PARTICLE = frozenset({"neg_base", "q_base"})
_SPECIAL_VERB_TENSES = frozenset({"present_perfect", "present_continuous"})


def _form_group(form: str | None) -> str | None:
    if form is None:
        return None
    return _FORM_GROUP.get(form)


def _active_rules(game: Game) -> list:
    rules = []
    for rule in game.pack.rules:
        if rule.result_tense not in (None, game.tense):
            continue
        if rule.polarity not in (None, game.polarity):
            continue
        if rule.id in _BASE_AFTER_PARTICLE and game.tense in _SPECIAL_VERB_TENSES:
            continue
        rules.append(rule)
    return rules


def _is_1sg(tile: Tile) -> bool:
    return tile.person == 1 and tile.number == "sg"


def _subject_class(tile) -> str:
    if _is_1sg(tile):
        return "1sg"
    if tile.person == 3 and tile.number == "sg":
        return "3sg"
    return "other"


def _subject_need_group(tense: str, subject: Tile) -> str:
    if tense == "present_continuous":
        if _is_1sg(subject):
            return "am"
        if subject.is_3sg():
            return "is"
        return "are"
    if tense in {"past_simple", "future_simple"}:
        return "any"
    return "s" if subject.is_3sg() else "base"


def _classes_for_group(group: str) -> set[str]:
    if group in {"s", "is"}:
        return {"3sg"}
    if group == "am":
        return {"1sg"}
    if group == "are":
        return {"other"}
    if group == "base":
        return {"1sg", "other"}
    return set()


def _ru_sentences(count: int) -> str:
    tail = count % 100
    digit = count % 10
    if 11 <= tail <= 14 or digit == 0 or digit >= 5:
        word = "предложений"
    elif digit == 1:
        word = "предложение"
    else:
        word = "предложения"
    return f"{count} {word}"


REPLACEMENTS_PER_PART = 1


def _replacement_kinds(consumed: list[Tile]) -> list[str]:
    kinds: list[str] = []
    for tile in consumed:
        kind = REPLACEMENT_KIND.get(tile.kind)
        if kind is None:
            continue
        kinds.extend([kind] * REPLACEMENTS_PER_PART)
    return kinds


def _clause_ids(grid: Grid) -> set[str]:
    return {
        cell.id
        for row in grid
        for cell in row
        if cell is not None and cell.kind == "clause"
    }


def _ids(grid: Grid) -> tuple:
    return tuple(
        tuple(cell.id if cell else None for cell in row) for row in grid
    )
