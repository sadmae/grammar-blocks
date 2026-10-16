from collections.abc import Callable
from dataclasses import dataclass

from game.tile import Tile


@dataclass(frozen=True)
class Pattern:
    kind: str
    form: str | None = None
    tense: str | None = None
    agreement: str | None = None


@dataclass(frozen=True)
class Rule:
    id: str
    left: Pattern
    right: Pattern
    result_kind: str
    result_level: int
    result_tense: str | None = None
    polarity: str | None = None


@dataclass(frozen=True)
class Hint:
    rule_id: str
    text: str
    left_id: str
    right_id: str


@dataclass(frozen=True)
class MergeOutcome:
    ok: bool
    tile: Tile | None = None
    hint: Hint | None = None


def matches(pattern: Pattern, tile: Tile) -> bool:
    if tile.kind != pattern.kind:
        return False
    if pattern.form is not None and tile.form != pattern.form:
        return False
    if pattern.tense is not None and tile.tense != pattern.tense:
        return False
    if pattern.agreement == "3sg" and not tile.is_3sg():
        return False
    if pattern.agreement == "not_3sg" and tile.is_3sg():
        return False
    if pattern.agreement == "1sg" and not _is_1sg(tile):
        return False
    if pattern.agreement == "are" and (tile.is_3sg() or _is_1sg(tile)):
        return False
    return True


def _is_1sg(tile: Tile) -> bool:
    return tile.person == 1 and tile.number == "sg"


def merge_score(level: int, combo_index: int) -> int:
    """Очки слияния: 10 * 2^level, дальше по ходу множитель комбо."""
    return 10 * (2**level) * combo_index


def resolve_merge(
    left: Tile,
    right: Tile,
    rules: tuple[Rule, ...] | list[Rule],
    near_miss: Callable[[Tile, Tile], Hint | None],
    new_id: Callable[[], str],
) -> MergeOutcome:
    for rule in rules:
        if matches(rule.left, left) and matches(rule.right, right):
            return MergeOutcome(ok=True, tile=_build(rule, left, right, new_id()))
    return MergeOutcome(ok=False, hint=near_miss(left, right))


def _build(rule: Rule, left: Tile, right: Tile, tile_id: str) -> Tile:
    return Tile(
        id=tile_id,
        text=f"{left.text} {right.text}",
        kind=rule.result_kind,
        level=rule.result_level,
        lemma=right.lemma or left.lemma,
        person=left.person if left.person is not None else right.person,
        number=left.number if left.number is not None else right.number,
        tense=rule.result_tense or left.tense or right.tense,
    )
