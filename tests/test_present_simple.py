import json
import random
from pathlib import Path

import pytest

from game.board import SIZE, Game
from game.lexicon import VERB_FORMS, load_lexicon
from game.packs.present_simple import ADVERB_WEIGHT, PresentSimplePack
from game.stats import WEAK_BOOST, ErrorStats, effective_weight
from game.tile import Tile

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data" / "lexicon.json"


@pytest.fixture
def pack():
    return PresentSimplePack(load_lexicon(LEXICON))


@pytest.fixture
def stats(tmp_path):
    return ErrorStats(tmp_path / "stats.json")


@pytest.fixture
def game(pack, stats):
    return Game(pack, stats, rng=random.Random(0), spawn_start=False)


def test_lexicon_has_two_hundred_seventy_verbs():
    lexicon = load_lexicon(LEXICON)
    assert len(lexicon.subjects) >= 63
    assert len(lexicon.adverbs) >= 72
    assert len(lexicon.objects) >= 45
    assert len(lexicon.verbs) == 270
    for entry in lexicon.verbs.values():
        for form in VERB_FORMS:
            assert entry[form]


def test_third_person_and_base_agreement(game, pack):
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("go", "s", "goes")
    game.grid[1][0] = pack.subject("I", "i")
    game.grid[1][1] = pack.verb("go", "base", "go")
    game.grid[2][0] = pack.subject("they", "they")
    game.grid[2][1] = pack.verb("watch", "base", "watch")
    game.grid[3][0] = pack.subject("it", "it")
    game.grid[3][1] = pack.verb("study", "s", "studies")

    assert game.move("left") is True
    assert game.grid[0][0].text == "she goes"
    assert game.grid[0][0].kind == "clause"
    assert game.grid[0][0].level == 2
    assert game.grid[1][0].text == "I go"
    assert game.grid[2][0].text == "they watch"
    assert game.grid[3][0].text == "it studies"
    assert game.score == 40 * (1 + 2 + 3 + 4)


def test_she_plus_go_is_a_near_miss_without_spawn(game, pack):
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("go", "base", "go")

    assert game.move("left") is False
    assert game.occupied() == 2
    assert game.score == 0
    assert game.grid[0][0].text == "she"
    assert game.grid[0][1].text == "go"
    assert len(game.hints) == 1
    assert game.hints[0].rule_id == "ps_3sg"
    assert game.hints[0].text == "she + go — для he/she/it в Present Simple нужно goes"
    assert game.session_errors["ps_3sg"] == 1


def test_i_plus_goes_asks_for_base_form(game, pack):
    game.grid[0][0] = pack.subject("I", "i")
    game.grid[0][1] = pack.verb("go", "s", "goes")

    game.move("left")

    assert game.score == 0
    assert game.hints[0].rule_id == "ps_base"
    assert game.hints[0].text == "I + goes — после I/you/we/they форма без -s: go"
    assert game.occupied() == 2


def test_verb_then_subject_keeps_reading_order(game, pack):
    game.grid[0][0] = pack.verb("go", "s", "goes")
    game.grid[0][1] = pack.subject("she", "she")

    assert game.move("left") is False
    assert game.grid[0][0].text == "goes"
    assert game.grid[0][1].text == "she"
    assert game.hints[0].rule_id == "ps_order"
    assert "goes she" not in game.hints[0].text
    assert game.occupied() == 2

    game.clear()
    game.grid[0][0] = pack.verb("go", "s", "goes")
    game.grid[0][1] = pack.subject("she", "she")
    assert game.move("right") is True
    assert game.grid[0][SIZE - 2].text == "goes"
    assert game.grid[0][SIZE - 1].text == "she"
    assert all(
        cell is None or cell.text != "goes she"
        for row in game.grid
        for cell in row
    )


def test_right_swipe_merges_left_to_right(game, pack):
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("go", "s", "goes")

    game.move("right")

    assert game.grid[0][SIZE - 1].text == "she goes"
    assert game.grid[0][SIZE - 1].kind == "clause"


def test_vertical_merge_reads_top_to_bottom(game, pack):
    game.grid[2][0] = pack.subject("she", "she")
    game.grid[3][0] = pack.verb("go", "s", "goes")
    game.move("up")
    assert game.grid[0][0].text == "she goes"

    game.clear()
    game.grid[0][1] = pack.subject("he", "he")
    game.grid[1][1] = pack.verb("have", "s", "has")
    game.move("down")
    assert game.grid[SIZE - 1][1].text == "he has"

    game.clear()
    game.grid[0][0] = pack.verb("look", "base", "look")
    game.grid[1][0] = pack.subject("I", "i")
    game.move("up")
    assert game.grid[0][0].text == "I look"

    game.clear()
    game.grid[0][0] = pack.verb("try", "s", "tries")
    game.grid[1][0] = pack.subject("you", "you")
    assert game.move("up") is False
    assert game.hints[0].rule_id == "ps_base"
    assert game.grid[0][0].text == "tries"
    assert game.grid[1][0].text == "you"


def test_vertical_adverb_joins_the_clause_above_it(game, pack):
    game.grid[0][0] = pack.adverb("every morning", "morning")
    game.grid[1][0] = Tile(
        id="calls",
        text="Maria calls",
        kind="clause",
        level=2,
        tense="present_simple",
    )

    game.move("up")

    assert game.grid[0][0].text == "Maria calls every morning"
    assert game.grid[0][0].kind == "sentence"

    game.clear()
    game.grid[0][0] = pack.adverb("every morning", "morning")
    game.grid[0][1] = Tile(
        id="calls",
        text="Maria calls",
        kind="clause",
        level=2,
        tense="present_simple",
    )
    assert game.move("left") is False
    assert "после фразы" in game.hints[0].text


def test_same_tile_does_not_merge_twice_in_one_move(game, pack):
    game.grid[0][0] = pack.subject("I", "i")
    game.grid[0][1] = pack.verb("go", "base", "go")
    game.grid[0][2] = pack.adverb("every day", "adv")

    game.move("left")

    assert game.grid[0][0].text == "I go"
    assert game.grid[0][0].kind == "clause"
    assert game.grid[0][1].text == "every day"
    assert game.won is False
    assert game.score == 40
    for row in game.grid:
        for col, cell in enumerate(row):
            if cell is not None and cell.kind not in {"clause", "adverb"}:
                row[col] = None

    game.move("left")

    assert game.grid[0][0].text == "I go every day"
    assert game.grid[0][0].kind == "sentence"
    assert game.grid[0][0].level == 3
    assert game.won is True
    assert game.score == 120


def test_two_merges_in_one_move_raise_the_combo(game, pack):
    game.grid[0][0] = pack.subject("I", "i")
    game.grid[0][1] = pack.verb("like", "base", "like")
    game.grid[0][2] = pack.subject("she", "she")
    game.grid[0][3] = pack.verb("play", "s", "plays")

    game.move("left")

    assert game.grid[0][0].text == "I like"
    assert game.grid[0][1].text == "she plays"
    assert game.score == 40 + 80
    assert sum(cell.kind == "subject" for row in game.grid for cell in row if cell) == 2
    assert sum(cell.kind == "verb" for row in game.grid for cell in row if cell) == 2


def test_unrelated_tiles_stay_silent(game, pack):
    game.grid[0][0] = pack.adverb("always", "a")
    game.grid[0][1] = pack.adverb("often", "b")
    game.grid[1][0] = pack.subject("we", "we")
    game.grid[1][1] = pack.subject("you", "you")

    game.move("left")

    assert game.hints == []
    assert game.score == 0
    assert game.occupied() == 4


def test_new_verb_matches_a_subject_that_has_no_pair(game, pack):
    game.grid[1][1] = pack.subject("it", "it")
    game.grid[0][2] = pack.verb("write", "base", "write")
    game.grid[1][3] = pack.verb("feel", "base", "feel")

    game.spawn(kind="verb")

    spawned = [
        cell
        for row in game.grid
        for cell in row
        if cell is not None and cell.kind == "verb" and cell.id not in {"write", "feel"}
    ]
    assert len(spawned) == 1
    assert spawned[0].form == "s"


def test_new_subject_matches_base_verbs(game, pack):
    game.grid[0][2] = pack.verb("write", "base", "write")
    game.grid[1][3] = pack.verb("feel", "base", "feel")

    game.spawn(kind="subject")

    spawned = [cell for row in game.grid for cell in row if cell is not None and cell.kind == "subject"]
    assert len(spawned) == 1
    assert spawned[0].is_3sg() is False


def test_merged_subject_is_replaced_by_a_new_subject(game, pack):
    game.grid[0][0] = pack.subject("they", "they")
    game.grid[0][1] = pack.verb("study", "base", "study")
    game.grid[0][2] = pack.verb("write", "s", "writes")

    game.move("left")

    texts = [cell.text for row in game.grid for cell in row if cell]
    kinds = [cell.kind for row in game.grid for cell in row if cell]
    assert "they study" in texts
    assert "writes" in texts
    assert kinds.count("subject") == 1
    assert kinds.count("verb") == 2
    assert kinds.count("clause") == 1


def test_slide_does_not_spawn_and_merge_replaces_the_lost_tile(game, pack):
    game.grid[0][3] = pack.subject("you", "you")
    assert game.move("left") is True
    assert game.grid[0][0].text == "you"
    assert game.occupied() == 1

    game.clear()
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][3] = pack.verb("do", "s", "does")
    assert game.move("left") is True
    assert game.grid[0][0].text == "she does"
    assert sum(cell.kind == "subject" for row in game.grid for cell in row if cell) == 1
    assert sum(cell.kind == "verb" for row in game.grid for cell in row if cell) == 1


def test_static_miss_is_not_counted_twice(game, pack, stats):
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("watch", "base", "watch")
    game.move("left")
    game.move("left")

    assert game.session_errors["ps_3sg"] == 1
    assert stats.count("ps_3sg") == 1
    stored = json.loads(stats.path.read_text(encoding="utf-8"))
    assert stored["errors"]["ps_3sg"] == 1
    assert game.hints[0].text == "she + watch — для he/she/it в Present Simple нужно watches"


def test_three_misses_boost_the_contrast_pair(game, pack):
    for index, lemma in enumerate(("go", "like", "play")):
        game.clear()
        game.grid[0][0] = pack.subject("she", f"s{index}")
        game.grid[0][1] = pack.verb(lemma, "base", f"v{index}")
        game.move("left")

    assert game.session_errors["ps_3sg"] == 3
    by_text = {spec.text: weight for spec, weight in zip(pack.spawn_specs, game.spawn_weights())}
    by_verb = {
        (spec.lemma, spec.form): weight
        for spec, weight in zip(pack.spawn_specs, game.spawn_weights())
        if spec.kind == "verb"
    }
    assert by_text["she"] == 7 * WEAK_BOOST
    assert by_text["I"] == 7
    assert by_verb[("go", "base")] == WEAK_BOOST
    assert by_verb[("go", "s")] == WEAK_BOOST
    assert by_text["every day"] == ADVERB_WEIGHT


def test_new_party_does_not_inherit_session_boost(pack, tmp_path):
    path = tmp_path / "stats.json"
    previous = ErrorStats(path)
    for _ in range(3):
        previous.record("ps_3sg")

    game = Game(pack, ErrorStats(path), spawn_start=False)
    assert game.session_errors["ps_3sg"] == 0
    assert game.stats.count("ps_3sg") == 3
    she = next(spec for spec in pack.spawn_specs if spec.text == "she")
    assert effective_weight(she, game.session_errors) == she.weight
    topics = game.weak_topics()
    assert topics[0]["id"] == "ps_3sg"
    assert topics[0]["count"] == 0
    assert topics[0]["total"] == 3
    assert topics[0]["boosted"] is False


def test_full_board_without_a_merge_is_game_over(game, pack):
    for row in range(SIZE):
        for col in range(SIZE):
            game.grid[row][col] = pack.verb("go", "base", f"{row}{col}")

    game.move("left")

    assert game.over is True
    assert game.occupied() == SIZE * SIZE
    assert game.move("right") is False
    assert game.occupied() == SIZE * SIZE


def test_full_board_with_a_legal_pair_can_still_move(game, pack):
    for row in range(SIZE):
        for col in range(SIZE):
            game.grid[row][col] = pack.adverb("often", f"a{row}{col}")
    game.grid[0][0] = pack.subject("we", "we")
    game.grid[0][1] = pack.verb("live", "base", "live")

    assert game.move("left") is True
    assert game.grid[0][0].text == "we live"
    assert game.occupied() == SIZE * SIZE
    assert game.over is False


def test_new_game_starts_with_three_tiles(pack, stats):
    started = Game(pack, stats, rng=random.Random(1))
    assert started.occupied() == 3
    assert started.over is False
    assert started.score == 0
    assert started.won is False
    assert started.adverbs_unlocked is False
    kinds = [cell.kind for row in started.grid for cell in row if cell]
    assert set(kinds) <= {"subject", "verb"}
    assert "subject" in kinds
    assert "verb" in kinds


def test_early_spawns_are_only_subjects_and_verbs(game):
    for _ in range(12):
        game.spawn()
    kinds = {cell.kind for row in game.grid for cell in row if cell}
    assert kinds <= {"subject", "verb"}
    assert game.adverbs_unlocked is False


def _clear_except_clauses(game):
    for row in range(SIZE):
        for col in range(SIZE):
            cell = game.grid[row][col]
            if cell is not None and cell.kind != "clause":
                game.grid[row][col] = None


def test_adverbs_unlock_after_two_phrases_and_then_spawn(game, pack):
    builds = (("I", "go", "base"), ("she", "like", "s"))
    for index, (subject, lemma, form) in enumerate(builds):
        _clear_except_clauses(game)
        game.grid[index][0] = pack.subject(subject, f"s{index}")
        game.grid[index][1] = pack.verb(lemma, form, f"v{index}")
        game.move("left")
        assert game.phrases_built == index + 1
    assert game.adverbs_unlocked is True
    assert not any(
        cell is not None and cell.kind == "adverb" for row in game.grid for cell in row
    )

    _clear_except_clauses(game)
    game.grid[2][0] = pack.subject("you", "you")
    game.grid[2][1] = pack.verb("read", "base", "read")
    game.move("left")

    kinds = [cell.kind for row in game.grid for cell in row if cell]
    assert "you read" in [cell.text for row in game.grid for cell in row if cell]
    assert kinds.count("adverb") == 2
    assert kinds.count("clause") == 3
    _clear_except_clauses(game)
    assert game.adverbs_unlocked is True


def test_blocked_move_adds_the_missing_second_adverb(game, pack):
    game.adverbs_unlocked = True
    game.phrases_built = 2
    game.grid[0][0] = pack.adverb("usually", "usually")
    game.grid[1][1] = _clause("she looks", "looks")

    assert game.move("right") is True

    assert game.score == 0
    assert _kinds(game).count("adverb") == 2
    assert "she looks" in _texts(game)


def test_one_adverb_on_the_board_is_brought_up_to_two(game, pack):
    game.adverbs_unlocked = True
    game.phrases_built = 2
    game.grid[0][0] = _clause("I go", "go")
    game.grid[1][0] = pack.adverb("often", "often")
    game.grid[2][0] = pack.subject("you", "you")
    game.grid[2][1] = pack.verb("read", "base", "read")

    game.move("left")

    assert "you read" in _texts(game)
    assert _kinds(game).count("adverb") == 2
    assert "verb" in _kinds(game)


def test_verb_returns_after_two_adverbs_without_dropping_below_two(game, pack):
    game.adverbs_unlocked = True
    game.phrases_built = 2
    game.grid[0][0] = _clause("I go", "go")
    game.grid[0][1] = pack.adverb("often", "often")
    game.grid[1][0] = pack.adverb("always", "always")

    game.move("left")

    assert _kinds(game).count("adverb") == 2
    assert "verb" in _kinds(game)
    assert "sentence" in _kinds(game)


def test_you_we_and_they_reject_s_form(game, pack):
    pairs = (("you", "like"), ("we", "play"), ("they", "try"))
    for row, (subject, lemma) in enumerate(pairs):
        game.grid[row][0] = pack.subject(subject, subject)
        game.grid[row][1] = pack.verb(lemma, "s", lemma)

    game.move("left")

    assert game.score == 0
    assert {hint.rule_id for hint in game.hints} == {"ps_base"}
    assert any("tries" in hint.text and "try" in hint.text for hint in game.hints)


def _clause(text: str, tile_id: str) -> Tile:
    return Tile(id=tile_id, text=text, kind="clause", level=2, tense="present_simple")


def _sentence(text: str, tile_id: str) -> Tile:
    return Tile(id=tile_id, text=text, kind="sentence", level=3, tense="present_simple")


def _kinds(game):
    return [cell.kind for row in game.grid for cell in row if cell]


def _texts(game):
    return [cell.text for row in game.grid for cell in row if cell]


def test_verb_returns_when_subjects_have_no_pair(game, pack):
    game.adverbs_unlocked = True
    game.phrases_built = 2
    game.grid[0][0] = pack.subject("you", "you")
    game.grid[0][1] = pack.subject("she", "she")
    game.grid[1][0] = _clause("I give", "give")
    game.grid[1][1] = pack.adverb("often", "often")

    game.move("left")

    assert "verb" in _kinds(game)
    assert "you" in _texts(game)
    assert "she" in _texts(game)


def test_three_sentences_are_banked(game, pack):
    game.grid[0][0] = _sentence("I go often", "s1")
    game.grid[0][1] = _sentence("we live usually", "s2")
    game.grid[1][0] = _clause("they play", "clause")
    game.grid[1][1] = pack.adverb("always", "always")

    game.move("left")

    assert game.sentences_collected == 3
    assert game.collected_sentences() == 3
    assert "sentence" not in _kinds(game)
    assert "3 предложения сняты с поля" in game.notice
    assert "verb" in _kinds(game)


def test_past_simple_asks_for_the_second_form(game, pack):
    game.tense = "past_simple"
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("go", "base", "go")

    assert game.move("left") is False
    assert "went" in game.hints[0].text

    game.clear()
    game.tense = "past_simple"
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.verb("go", "past", "went")
    game.move("left")

    assert game.grid[0][0].text == "she went"
    assert game.grid[0][0].kind == "clause"


def test_negative_builds_with_dont_and_base_verb(game, pack):
    game.polarity = "negative"
    game.grid[0][0] = pack.subject("she", "she")
    game.grid[0][1] = pack.aux("dont", "dont")
    assert game.move("left") is False
    assert "doesn't" in game.hints[0].text

    game.clear()
    game.polarity = "negative"
    game.grid[0][0] = pack.subject("I", "i")
    game.grid[0][1] = pack.aux("dont", "dont")
    game.move("left")
    negation = next(cell for row in game.grid for cell in row if cell and cell.text == "I don't")
    verb = pack.verb("go", "base", "go")
    game.grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    game.grid[0][0] = negation
    game.grid[0][1] = verb
    game.move("left")

    assert game.grid[0][0].text == "I don't go"
    assert game.grid[0][0].kind == "clause"


def test_question_starts_with_do_or_does(game, pack):
    game.polarity = "question"
    game.grid[0][0] = pack.aux("do", "do")
    game.grid[0][1] = pack.subject("she", "she")
    assert game.move("left") is False
    assert "Does" in game.hints[0].text

    game.clear()
    game.polarity = "question"
    game.grid[0][0] = pack.aux("does", "does")
    game.grid[0][1] = pack.subject("she", "she")
    game.move("left")
    question = next(cell for row in game.grid for cell in row if cell and cell.text == "Does she")
    game.grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    game.grid[0][0] = question
    game.grid[0][1] = pack.verb("go", "base", "go")
    game.move("left")

    assert game.grid[0][0].text == "Does she go"


def test_object_follows_the_clause(game, pack):
    game.grid[0][0] = _clause("she likes", "likes")
    game.grid[0][1] = pack.object("music", "music")

    game.move("left")

    assert game.grid[0][0].text == "she likes music"
    assert game.grid[0][0].kind == "clause"


def test_unplayed_board_redeals_past_verbs(game, pack):
    game.grid[0][0] = pack.verb("leave", "base", "leave")
    game.grid[1][0] = pack.subject("they", "they")
    game.grid[2][0] = pack.subject("I", "i")
    game.opening_mode = ("present_simple", "affirmative", False)

    game.tense = "past_simple"
    game.sync_opening()

    verbs = [cell for row in game.grid for cell in row if cell and cell.kind == "verb"]
    subjects = [cell for row in game.grid for cell in row if cell and cell.kind == "subject"]
    assert verbs and all(verb.form == "past" for verb in verbs)
    assert subjects
    game.grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    game.grid[0][0] = verbs[0]
    game.grid[1][0] = subjects[0]
    game.move("up")
    assert game.grid[0][0].kind == "clause"
    assert game.grid[0][0].text == f"{subjects[0].text} {verbs[0].text}"


def test_played_board_keeps_tiles_when_tense_changes(game, pack):
    game.grid[0][0] = pack.verb("leave", "base", "leave")
    game.score = 40
    game.opening_mode = ("present_simple", "affirmative", False)
    game.tense = "past_simple"

    game.sync_opening()

    assert game.grid[0][0].text == "leave"


def test_shuffle_rearranges_without_new_tiles(game, pack):
    game.grid[0][0] = pack.verb("try", "base", "try")
    game.grid[0][1] = pack.verb("feel", "base", "feel")
    game.grid[0][2] = pack.subject("you", "you")
    game.score = 40
    game.hints = []

    assert game.shuffle() is True

    texts = sorted(cell.text for row in game.grid for cell in row if cell)
    assert texts == ["feel", "try", "you"]
    assert game.occupied() == 3
    assert game.score == 40
    assert [game.grid[0][0], game.grid[0][1], game.grid[0][2]] != [
        pack.verb("try", "base", "try"),
        pack.verb("feel", "base", "feel"),
        pack.subject("you", "you"),
    ]
    assert game.shuffles_left == 2


def test_a_game_allows_only_three_shuffles(game, pack):
    game.grid[0][0] = pack.verb("try", "base", "try")
    game.grid[0][1] = pack.verb("feel", "base", "feel")
    game.grid[0][2] = pack.subject("you", "you")

    assert game.shuffle() is True
    assert game.shuffle() is True
    assert game.shuffle() is True
    frozen = [[cell.id if cell else None for cell in row] for row in game.grid]
    assert game.shuffles_left == 0
    assert game.shuffle() is False
    assert [[cell.id if cell else None for cell in row] for row in game.grid] == frozen


def test_mode_changes_the_spawn_pool(game):
    game.adverbs_unlocked = True
    game.tense = "past_simple"
    verbs = {spec.form for spec in game.spawn_pool() if spec.kind == "verb"}
    adverbs = {spec.text for spec in game.spawn_pool() if spec.kind == "adverb"}
    assert verbs == {"past"}
    assert "yesterday" in adverbs
    assert "often" not in adverbs

    game.tense = "present_simple"
    game.polarity = "question"
    forms = {spec.form for spec in game.spawn_pool() if spec.kind == "verb"}
    aux = {spec.text for spec in game.spawn_pool() if spec.kind == "aux"}
    assert forms == {"base"}
    assert aux == {"Do", "Does"}
    assert all(spec.kind != "object" for spec in game.spawn_pool())

    game.objects_enabled = True
    assert any(spec.kind == "object" for spec in game.spawn_pool())


def _place(game, pack, row, pairs):
    for col, (kind, *args) in enumerate(pairs):
        if kind == "subject":
            game.grid[row][col] = pack.subject(args[0], f"{args[0]}-{row}-{col}")
        elif kind == "verb":
            game.grid[row][col] = pack.verb(args[0], args[1], f"{args[0]}-{args[1]}-{col}")
        elif kind == "aux":
            game.grid[row][col] = pack.aux(args[0], f"{args[0]}-{row}-{col}")
        elif kind == "adverb":
            game.grid[row][col] = pack.adverb(args[0], f"adv-{row}-{col}")


def test_future_simple_builds_will_and_base_verb(game, pack):
    game.clear()
    game.tense = "future_simple"
    _place(game, pack, 0, [("subject", "I"), ("aux", "will"), ("verb", "go", "base")])
    assert game.move("left") is True
    assert game.grid[0][0].text == "I will"
    assert game.move("left") is True
    assert game.grid[0][0].text == "I will go"
    assert game.grid[0][0].kind == "clause"

    game.clear()
    game.tense = "future_simple"
    game.polarity = "negative"
    _place(game, pack, 0, [("subject", "she"), ("aux", "wont"), ("verb", "go", "base")])
    assert game.move("left") is True
    assert game.grid[0][0].text == "she won't"
    assert game.move("left") is True
    assert game.grid[0][0].text == "she won't go"

    game.clear()
    game.tense = "future_simple"
    game.polarity = "question"
    _place(game, pack, 0, [("aux", "willq"), ("subject", "she"), ("verb", "go", "base")])
    assert game.move("left") is True
    assert game.grid[0][0].text == "Will she"
    assert game.move("left") is True
    assert game.grid[0][0].text == "Will she go"


def test_present_perfect_uses_have_has_and_third_form(game, pack):
    game.clear()
    game.tense = "present_perfect"
    _place(game, pack, 0, [("subject", "I"), ("aux", "have"), ("verb", "go", "pp")])
    assert game.move("left") is True
    assert game.move("left") is True
    assert game.grid[0][0].text == "I have gone"

    game.clear()
    game.tense = "present_perfect"
    _place(game, pack, 0, [("subject", "she"), ("aux", "have")])
    assert game.move("left") is False
    assert "has" in game.hints[0].text

    game.clear()
    game.tense = "present_perfect"
    game.polarity = "negative"
    _place(game, pack, 0, [("subject", "she"), ("aux", "hasnt"), ("verb", "go", "base")])
    assert game.move("left") is True
    assert game.grid[0][0].text == "she hasn't"
    verb = next(cell for row in game.grid for cell in row if cell is not None and cell.kind == "verb")
    built = game.grid[0][0]
    game.grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    game.grid[0][0] = built
    game.grid[0][1] = verb
    assert game.move("left") is False
    assert "gone" in game.hints[0].text
    game.grid[0][1] = pack.verb("go", "pp", "gone")
    assert game.move("left") is True
    assert game.grid[0][0].text == "she hasn't gone"


def test_present_continuous_agrees_am_is_are(game, pack):
    game.clear()
    game.tense = "present_continuous"
    _place(game, pack, 0, [("subject", "I"), ("aux", "am"), ("verb", "work", "ing")])
    assert game.move("left") is True
    assert game.move("left") is True
    assert game.grid[0][0].text == "I am working"

    game.clear()
    game.tense = "present_continuous"
    _place(game, pack, 0, [("subject", "she"), ("aux", "are")])
    assert game.move("left") is False
    assert "is" in game.hints[0].text

    game.clear()
    game.tense = "present_continuous"
    _place(game, pack, 0, [("subject", "you"), ("aux", "are"), ("verb", "work", "ing")])
    assert game.move("left") is True
    assert game.move("left") is True
    assert game.grid[0][0].text == "you are working"


def test_compound_opening_deals_an_auxiliary(game):
    game.tense = "future_simple"
    game.sync_opening()
    kinds = [cell.kind for row in game.grid for cell in row if cell]
    assert "aux" in kinds
    assert "subject" in kinds
    verbs = {cell.form for row in game.grid for cell in row if cell and cell.kind == "verb"}
    assert verbs == {"base"}

    game.score = 0
    game.phrases_built = 0
    game.sentences_collected = 0
    game.tense = "present_simple"
    game.sync_opening()
    kinds = [cell.kind for row in game.grid for cell in row if cell]
    assert "aux" not in kinds


def test_new_tenses_keep_their_own_adverbs(game):
    game.adverbs_unlocked = True
    game.tense = "future_simple"
    adverbs = {spec.text for spec in game.spawn_pool() if spec.kind == "adverb"}
    assert "tomorrow" in adverbs
    assert "often" not in adverbs
    assert "now" not in adverbs

    game.tense = "present_continuous"
    adverbs = {spec.text for spec in game.spawn_pool() if spec.kind == "adverb"}
    forms = {spec.form for spec in game.spawn_pool() if spec.kind == "verb"}
    assert "now" in adverbs
    assert forms == {"ing"}
    assert "tomorrow" not in adverbs
