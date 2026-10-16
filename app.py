import html
import importlib
from pathlib import Path

import streamlit as st

import game.board as board
from game.board import SIZE, Game
from game.lexicon import load_lexicon
from game.packs.present_simple import PresentSimplePack
from game.stats import ErrorStats
from game.tile import Tile

ROOT = Path(__file__).resolve().parent
LEXICON_PATH = ROOT / "data" / "lexicon.json"
STATS_PATH = ROOT / "data" / "stats.json"

KIND_CLASS = {
    "subject": "tile-subject",
    "verb": "tile-verb",
    "adverb": "tile-adverb",
    "aux": "tile-aux",
    "object": "tile-object",
    "negation": "tile-clause",
    "question": "tile-clause",
    "chain": "tile-clause",
    "clause": "tile-clause",
    "sentence": "tile-sentence",
}

TENSE_OPTIONS = {
    "Present Simple": "present_simple",
    "Past Simple": "past_simple",
    "Future Simple": "future_simple",
    "Present Perfect": "present_perfect",
    "Present Continuous": "present_continuous",
}
POLARITY_OPTIONS = {
    "утверждение": "affirmative",
    "отрицание": "negative",
    "вопрос": "question",
}

CSS = f"""
<style>
.stApp {{ background: #faf8ef; }}
.block-container {{
  max-width: 640px;
  padding-top: 1.1rem;
  margin-left: auto;
  margin-right: auto;
}}
.topbar {{
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 12px;
}}
.topbar h1 {{
  margin: 0;
  color: #776e65;
  font-size: 2.5rem;
  line-height: 1;
  font-weight: 800;
}}
.tagline {{ margin: 6px 0 0; color: #a89b8c; font-size: 0.92rem; }}
.scores {{ display: flex; gap: 8px; }}
.score {{
  background: #bbada0;
  color: #f9f6f2;
  border-radius: 6px;
  min-width: 92px;
  text-align: center;
  padding: 6px 12px 8px;
}}
.score span {{
  display: block;
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 700;
}}
.score strong {{ display: block; font-size: 1.55rem; line-height: 1.1; }}
.status, .banner {{
  border-radius: 8px;
  padding: 8px 12px;
  margin: 0 0 10px;
  color: #776e65;
}}
.status {{ background: #eee4da; }}
.banner {{ background: #edc850; color: #3d3010; font-weight: 700; }}
.banner-over {{ background: #f2b179; color: #3d2410; font-weight: 700; }}
.board {{
  display: grid;
  grid-template-columns: repeat({SIZE}, 1fr);
  gap: 10px;
  background: #bbada0;
  padding: 10px;
  border-radius: 12px;
  max-width: 520px;
  margin: 0 auto 8px;
}}
.cell {{
  min-height: 84px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-weight: 700;
  font-size: 0.95rem;
  line-height: 1.15;
  padding: 6px;
}}
.cell span {{ word-break: break-word; }}
.cell-empty {{ background: rgba(238, 228, 218, 0.55); }}
.tile-subject {{ background: #6a96c8; color: #10233f; }}
.tile-verb {{ background: #e4ad78; color: #3d2410; }}
.tile-adverb {{ background: #c4a6d4; color: #2d143f; }}
.tile-aux {{ background: #78b7ae; color: #10312e; }}
.tile-object {{ background: #8fb584; color: #143018; }}
.tile-clause {{ background: #e3c15a; color: #3d3010; font-size: 0.82rem; }}
.tile-sentence {{ background: #e07a5f; color: #ffffff; font-size: 0.78rem; }}
.legend {{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin: 0 auto 14px;
  max-width: 520px;
}}
.legend span {{
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 700;
}}
.formula {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin: 6px 0;
}}
.formula .chip {{
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.85rem;
  font-weight: 600;
}}
.formula .plus {{ font-weight: 700; color: #776e65; }}
.st-key-modebar .stButton button {{
  border-radius: 999px;
  min-height: 40px;
  font-weight: 700;
  border: 1px solid #d8cfc6;
  background: #fffdf8;
  color: #776e65;
}}
.st-key-modebar .stButton button[kind="primary"] {{
  background: #8f7a66;
  border-color: #8f7a66;
  color: #f9f6f2;
}}
.st-key-arrows {{ max-width: 280px; margin: 0 auto; }}
.st-key-arrows .stButton button {{
  background: #8f7a66;
  color: #f9f6f2;
  border: none;
  border-radius: 10px;
  min-height: 56px;
  font-size: 1.35rem;
  font-weight: 700;
}}
.st-key-arrows .stButton button:hover {{
  background: #9f8a76;
  color: #fff;
}}
.st-key-actions {{ max-width: 420px; margin: 4px auto 0; }}
.st-key-actions .stButton button {{
  background: transparent;
  color: #8f7a66;
  border: 2px solid #bbada0;
  border-radius: 10px;
  min-height: 44px;
  font-weight: 700;
}}
.st-key-modebar .stButton,
.st-key-arrows .stButton,
.st-key-actions .stButton {{ margin-bottom: 0; }}
div[data-testid="stAlert"] {{ border-radius: 8px; }}
</style>
"""


def new_game() -> Game:
    lexicon = load_lexicon(LEXICON_PATH)
    pack = PresentSimplePack(lexicon)
    stats = ErrorStats(STATS_PATH)
    return Game(pack, stats)


def tile_html(tile: Tile | None) -> str:
    if tile is None:
        return '<div class="cell cell-empty"></div>'
    css = KIND_CLASS.get(tile.kind, "tile-verb")
    return f'<div class="cell {css}"><span>{html.escape(tile.text)}</span></div>'


def stage_text(game: Game, have: int, need: int) -> str:
    lines = {
        ("negative", "past_simple"): "Отрицание: подлежащее + didn't + глагол без -s.",
        ("negative", "present_simple"): "Отрицание: I/you/we/they + don't, he/she/it + doesn't, потом глагол без -s.",
        ("negative", "future_simple"): "Отрицание: подлежащее + won't + глагол без -s.",
        ("negative", "present_perfect"): "Отрицание: haven't / hasn't + третья форма.",
        ("negative", "present_continuous"): "Отрицание: am not / isn't / aren't + форма с -ing.",
        ("question", "past_simple"): "Вопрос: Did + подлежащее + глагол без -s.",
        ("question", "present_simple"): "Вопрос: Do + I/you/we/they, Does + he/she/it, потом глагол без -s.",
        ("question", "future_simple"): "Вопрос: Will + подлежащее + глагол без -s.",
        ("question", "present_perfect"): "Вопрос: Have / Has + подлежащее + третья форма.",
        ("question", "present_continuous"): "Вопрос: Am / Is / Are + подлежащее + форма с -ing.",
        ("affirmative", "past_simple"): "Past Simple: подлежащее + вторая форма. Обстоятельство после фразы: she went yesterday.",
        ("affirmative", "future_simple"): "Future Simple: подлежащее + will + глагол без -s. She will go tomorrow.",
        ("affirmative", "present_perfect"): "Present Perfect: have/has + третья форма. She has gone already.",
        ("affirmative", "present_continuous"): "Present Continuous: am/is/are + -ing. She is reading now.",
    }
    mode = lines.get((game.polarity, game.tense))
    if mode is None and game.adverbs_unlocked:
        mode = "Обстоятельства открыты. Поставьте их после фразы: she goes every day."
    if mode is None:
        mode = f"Пока выпадают только подлежащие и глаголы. Собрано фраз: {have}/{need}."
    if game.objects_enabled:
        mode += " Дополнение ставится после фразы: she likes music."
    return mode


def board_html(game: Game) -> str:
    cells = [tile_html(tile) for row in game.grid for tile in row]
    return '<div class="board">' + "".join(cells) + "</div>"


def _formula(rows: list[list[tuple[str, str]]]) -> str:
    lines = []
    for row in rows:
        parts = []
        for index, (kind, text) in enumerate(row):
            if index:
                parts.append('<span class="plus">+</span>')
            parts.append(f'<span class="chip {kind}">{html.escape(text)}</span>')
        lines.append('<div class="formula">' + "".join(parts) + "</div>")
    return "".join(lines)


HANDBOOK = {
    ("present_simple", "affirmative"): {
        "title": "Present Simple, утверждение",
        "rows": [
            [("tile-subject", "I / you / we / they"), ("tile-verb", "work")],
            [("tile-subject", "he / she / it"), ("tile-verb", "works")],
            [("tile-clause", "she likes"), ("tile-object", "music"), ("tile-adverb", "every day")],
        ],
        "text": (
            "У I, you, we, they глагол без окончания: I work, you watch, they study, we live. "
            "У he, she, it глагол с -s или -es: he works, she goes, it leaves. "
            "Особые формы: have → has, do → does, study → studies.\n\n"
            "Сначала собирается фраза: подлежащее и глагол. "
            "Дополнение ставится сразу после неё: she likes music. "
            "Обстоятельство замыкает предложение: she goes every day, they study usually.\n\n"
            "Не собирается: he go, she leave, I goes, they works. "
            "Обстоятельство и дополнение не ставятся перед фразой."
        ),
    },
    ("present_simple", "negative"): {
        "title": "Present Simple, отрицание",
        "rows": [
            [("tile-subject", "I / you / we / they"), ("tile-aux", "don't"), ("tile-verb", "work")],
            [("tile-subject", "he / she / it"), ("tile-aux", "doesn't"), ("tile-verb", "go")],
        ],
        "text": (
            "Сначала подлежащее и частица, потом глагол в первой форме, без -s.\n\n"
            "I, you, we, they + don't: I don't work, they don't go. "
            "he, she, it + doesn't: she doesn't go, he doesn't leave.\n\n"
            "После don't и doesn't окончание -s не добавляется: she doesn't go, не she doesn't goes. "
            "Не собирается: she don't work, I doesn't go."
        ),
    },
    ("present_simple", "question"): {
        "title": "Present Simple, вопрос",
        "rows": [
            [("tile-aux", "Do"), ("tile-subject", "I / you / we / they"), ("tile-verb", "work")],
            [("tile-aux", "Does"), ("tile-subject", "he / she / it"), ("tile-verb", "go")],
        ],
        "text": (
            "Вопрос начинается с частицы, подлежащее стоит после неё. Глагол снова в первой форме.\n\n"
            "Do + I / you / we / they: Do you work? Do they study? "
            "Does + he / she / it: Does she go? Does it leave?\n\n"
            "Не собирается: Does you go, Do she work, Does he goes. "
            "Вопрос не начинается с подлежащего."
        ),
    },
    ("past_simple", "affirmative"): {
        "title": "Past Simple, утверждение",
        "rows": [
            [("tile-subject", "I / they / she"), ("tile-verb", "left / went")],
            [("tile-clause", "she liked"), ("tile-object", "music"), ("tile-adverb", "yesterday")],
        ],
        "text": (
            "Любое подлежащее соединяется со второй формой глагола. Окончание -s здесь не используется.\n\n"
            "Правильные глаголы получают -ed: watch → watched, play → played, study → studied. "
            "Неправильные меняют основу: go → went, leave → left, see → saw, have → had, do → did.\n\n"
            "I left, they went, she watched. "
            "Дополнение после фразы: she liked music. "
            "Обстоятельство прошедшего времени в конце: she went yesterday, they left last week.\n\n"
            "Не собирается: they leave, I go, she goes. Это формы настоящего, не прошедшего."
        ),
    },
    ("past_simple", "negative"): {
        "title": "Past Simple, отрицание",
        "rows": [
            [("tile-subject", "I / she / they"), ("tile-aux", "didn't"), ("tile-verb", "go / leave")],
        ],
        "text": (
            "Подлежащее + didn't + первая форма глагола. Вторая форма после didn't не ставится.\n\n"
            "I didn't go. She didn't leave. They didn't watch.\n\n"
            "Не собирается: didn't went, didn't left, she didn't goes."
        ),
    },
    ("past_simple", "question"): {
        "title": "Past Simple, вопрос",
        "rows": [
            [("tile-aux", "Did"), ("tile-subject", "you / she / they"), ("tile-verb", "go / leave")],
        ],
        "text": (
            "Did стоит перед любым подлежащим. Глагол после него в первой форме.\n\n"
            "Did you go? Did she leave? Did they watch?\n\n"
            "Не собирается: Did she went, Did they left. Вопрос не начинается с подлежащего."
        ),
    },
    ("future_simple", "affirmative"): {
        "title": "Future Simple, утверждение",
        "rows": [
            [("tile-subject", "I / she / they"), ("tile-aux", "will"), ("tile-verb", "go")],
            [("tile-clause", "she will go"), ("tile-adverb", "tomorrow")],
        ],
        "text": (
            "Will стоит после любого подлежащего. Глагол после will в первой форме, без -s.\n\n"
            "I will go. She will leave. They will watch.\n\n"
            "Обстоятельство будущего в конце: she will go tomorrow.\n\n"
            "Не собирается: she will goes, they will went."
        ),
    },
    ("future_simple", "negative"): {
        "title": "Future Simple, отрицание",
        "rows": [[("tile-subject", "I / she / they"), ("tile-aux", "won't"), ("tile-verb", "go")]],
        "text": (
            "Won't + первая форма глагола.\n\n"
            "I won't go. She won't leave. They won't watch.\n\n"
            "Не собирается: won't went, won't goes."
        ),
    },
    ("future_simple", "question"): {
        "title": "Future Simple, вопрос",
        "rows": [[("tile-aux", "Will"), ("tile-subject", "you / she"), ("tile-verb", "go")]],
        "text": (
            "Will стоит перед любым подлежащим. Глагол после него в первой форме.\n\n"
            "Will you go? Will she leave?\n\n"
            "Не собирается: Will she goes, Do she will."
        ),
    },
    ("present_perfect", "affirmative"): {
        "title": "Present Perfect, утверждение",
        "rows": [
            [("tile-subject", "I / you / we / they"), ("tile-aux", "have"), ("tile-verb", "gone")],
            [("tile-subject", "he / she / it"), ("tile-aux", "has"), ("tile-verb", "seen")],
            [("tile-clause", "she has seen"), ("tile-adverb", "already")],
        ],
        "text": (
            "I, you, we, they + have + третья форма. he, she, it + has + третья форма.\n\n"
            "I have gone. She has seen. They have written.\n\n"
            "Обстоятельства: already, just, yet, ever, recently.\n\n"
            "Не собирается: she have gone, he has went."
        ),
    },
    ("present_perfect", "negative"): {
        "title": "Present Perfect, отрицание",
        "rows": [
            [("tile-subject", "I / they"), ("tile-aux", "haven't"), ("tile-verb", "seen")],
            [("tile-subject", "she"), ("tile-aux", "hasn't"), ("tile-verb", "gone")],
        ],
        "text": (
            "haven't и hasn't стоят перед третьей формой.\n\n"
            "I haven't seen. She hasn't gone.\n\n"
            "Не собирается: she hasn't go, they haven't went."
        ),
    },
    ("present_perfect", "question"): {
        "title": "Present Perfect, вопрос",
        "rows": [
            [("tile-aux", "Have"), ("tile-subject", "you / they"), ("tile-verb", "gone")],
            [("tile-aux", "Has"), ("tile-subject", "she"), ("tile-verb", "seen")],
        ],
        "text": (
            "Have перед I, you, we, they. Has перед he, she, it. Глагол в третьей форме.\n\n"
            "Have you gone? Has she seen?\n\n"
            "Не собирается: Has you gone, Have she seen."
        ),
    },
    ("present_continuous", "affirmative"): {
        "title": "Present Continuous, утверждение",
        "rows": [
            [("tile-subject", "I"), ("tile-aux", "am"), ("tile-verb", "reading")],
            [("tile-subject", "he / she / it"), ("tile-aux", "is"), ("tile-verb", "going")],
            [("tile-subject", "you / we / they"), ("tile-aux", "are"), ("tile-verb", "watching")],
        ],
        "text": (
            "I + am + форма с -ing. he, she, it + is + -ing. you, we, they + are + -ing.\n\n"
            "I am reading. She is going. They are watching.\n\n"
            "Обстоятельства: now, right now, at the moment.\n\n"
            "Не собирается: she are going, I is reading, he going."
        ),
    },
    ("present_continuous", "negative"): {
        "title": "Present Continuous, отрицание",
        "rows": [
            [("tile-subject", "I"), ("tile-aux", "am not"), ("tile-verb", "reading")],
            [("tile-subject", "she"), ("tile-aux", "isn't"), ("tile-verb", "going")],
            [("tile-subject", "they"), ("tile-aux", "aren't"), ("tile-verb", "watching")],
        ],
        "text": (
            "am not, isn't и aren't стоят перед формой с -ing.\n\n"
            "I am not reading. She isn't going. They aren't watching.\n\n"
            "Не собирается: she aren't going, I isn't reading."
        ),
    },
    ("present_continuous", "question"): {
        "title": "Present Continuous, вопрос",
        "rows": [
            [("tile-aux", "Am"), ("tile-subject", "I"), ("tile-verb", "reading")],
            [("tile-aux", "Is"), ("tile-subject", "she"), ("tile-verb", "going")],
            [("tile-aux", "Are"), ("tile-subject", "they"), ("tile-verb", "watching")],
        ],
        "text": (
            "Am перед I, Is перед he/she/it, Are перед you/we/they. Глагол с -ing.\n\n"
            "Am I reading? Is she going? Are they watching?\n\n"
            "Не собирается: Are she going, Is I reading."
        ),
    },
}


def render_handbook(game: Game) -> None:
    with st.expander("Справочник"):
        _handbook_body(game)


def _handbook_body(game: Game) -> None:
    st.markdown(
        "Предложение собирается по порядку: **подлежащее → глагол → дополнение → обстоятельство**. "
        "На поле этот порядок идёт слева направо. "
        "Подлежащее и глагол собираются и по вертикали, даже если глагол оказался сверху. "
        "Фраза и обстоятельство тоже собираются по вертикали, даже если обстоятельство оказалось сверху. "
        "В вопросе порядок другой: сначала частица, потом подлежащее."
    )
    page = HANDBOOK[(game.tense, game.polarity)]
    st.markdown(f"**{page['title']}**")
    st.markdown(_formula(page["rows"]), unsafe_allow_html=True)
    st.markdown(page["text"])
    with st.expander("Все схемы"):
        for (tense, polarity), item in HANDBOOK.items():
            if (tense, polarity) == (game.tense, game.polarity):
                continue
            st.markdown(f"**{item['title']}**")
            st.markdown(_formula(item["rows"]), unsafe_allow_html=True)
            st.markdown(item["text"])


def _note(text: str, kind: str = "status") -> str:
    return f'<p class="{kind}">{html.escape(text)}</p>'


def _pill(label: str, selected: bool, key: str) -> bool:
    return st.button(
        label,
        key=key,
        type="primary" if selected else "secondary",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title="Grammar Blocks", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)

    if "game" not in st.session_state:
        st.session_state.game = new_game()
    if "tense_label" not in st.session_state:
        st.session_state.tense_label = "Present Simple"
    if "polarity_label" not in st.session_state:
        st.session_state.polarity_label = "утверждение"
    if "objects_on" not in st.session_state:
        st.session_state.objects_on = False
    game: Game = st.session_state.game
    if getattr(board, "ENGINE_REVISION", 0) < 6:
        importlib.reload(board)
    game_cls = board.Game
    if game.__class__ is not game_cls:
        game.__class__ = game_cls
    game.ensure_state()
    game.tense = TENSE_OPTIONS[st.session_state.tense_label]
    game.polarity = POLARITY_OPTIONS[st.session_state.polarity_label]
    game.objects_enabled = st.session_state.objects_on
    game.sync_opening()
    game.top_up_adverbs()
    if "record" not in st.session_state:
        st.session_state.record = 0
    if game.score > st.session_state.record:
        st.session_state.record = game.score

    st.markdown(
        f"""
        <div class="topbar">
          <div>
            <h1>Grammar Blocks</h1>
            <p class="tagline">После слияния вместо каждой части появляется одна новая плитка.</p>
          </div>
          <div class="scores">
            <div class="score"><span>Очки</span><strong>{game.score}</strong></div>
            <div class="score record"><span>Рекорд</span><strong>{st.session_state.record}</strong></div>
            <div class="score"><span>Собрано</span><strong>{game.collected_sentences()}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="modebar"):
        labels = list(TENSE_OPTIONS)
        for index in range(0, len(labels), 2):
            cols = st.columns(2)
            for col, label in zip(cols, labels[index : index + 2]):
                with col:
                    if _pill(label, st.session_state.tense_label == label, f"tense_{label}"):
                        st.session_state.tense_label = label
                        st.rerun()
        affirm, negative, question, objects = st.columns(4)
        with affirm:
            if _pill("утверждение", st.session_state.polarity_label == "утверждение", "pol_aff"):
                st.session_state.polarity_label = "утверждение"
                st.rerun()
        with negative:
            if _pill("отрицание", st.session_state.polarity_label == "отрицание", "pol_neg"):
                st.session_state.polarity_label = "отрицание"
                st.rerun()
        with question:
            if _pill("вопрос", st.session_state.polarity_label == "вопрос", "pol_q"):
                st.session_state.polarity_label = "вопрос"
                st.rerun()
        with objects:
            if _pill("дополнение", st.session_state.objects_on, "objects_toggle"):
                st.session_state.objects_on = not st.session_state.objects_on
                st.rerun()

    need = game.pack.phrases_to_unlock_adverbs
    have = game.phrases_built
    if game.notice:
        st.markdown(_note(game.notice, "banner"), unsafe_allow_html=True)
    elif game.won:
        st.markdown(
            _note("Цель собрана. Три готовых предложения снимаются с поля и остаются в счёте.", "banner"),
            unsafe_allow_html=True,
        )
    st.markdown(_note(stage_text(game, have, need)), unsafe_allow_html=True)
    for hint in game.hints:
        st.warning(hint.text)
    if game.over:
        if game.shuffles_left > 0:
            over_text = f"Ходов больше нет. Осталось перемешиваний: {game.shuffles_left}."
        else:
            over_text = "Ходов больше нет. Перемешивания закончились. Начните новую партию."
        st.markdown(_note(over_text, "status banner-over"), unsafe_allow_html=True)

    st.markdown(board_html(game), unsafe_allow_html=True)
    st.markdown(
        """
        <div class="legend">
          <span class="tile-subject">подлежащее</span>
          <span class="tile-verb">глагол</span>
          <span class="tile-adverb">обстоятельство</span>
          <span class="tile-aux">частица</span>
          <span class="tile-object">дополнение</span>
          <span class="tile-clause">фраза</span>
          <span class="tile-sentence">предложение</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="arrows"):
        _, up_col, _ = st.columns(3)
        with up_col:
            up = st.button("↑", key="up", use_container_width=True)
        left_col, down_col, right_col = st.columns(3)
        with left_col:
            left = st.button("←", key="left", use_container_width=True)
        with down_col:
            down = st.button("↓", key="down", use_container_width=True)
        with right_col:
            right = st.button("→", key="right", use_container_width=True)

    pressed = None
    if up:
        pressed = "up"
    elif left:
        pressed = "left"
    elif down:
        pressed = "down"
    elif right:
        pressed = "right"
    if pressed:
        game.move(pressed)
        st.rerun()

    with st.container(key="actions"):
        shuffle_col, new_col = st.columns(2)
        with shuffle_col:
            shuffle = st.button(
                f"Перемешать · {game.shuffles_left}",
                key="shuffle",
                use_container_width=True,
                disabled=game.shuffles_left <= 0,
            )
        with new_col:
            restart = st.button("Новая партия", key="restart", use_container_width=True)
    if shuffle:
        game.shuffle()
        st.rerun()
    if restart:
        st.session_state.game = new_game()
        st.rerun()

    render_handbook(game)


if __name__ == "__main__":
    main()
