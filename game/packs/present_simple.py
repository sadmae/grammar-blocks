from game.lexicon import Lexicon
from game.merge import Hint, Pattern, Rule
from game.tile import SpawnSpec, Tile

PS_3SG = "ps_3sg"
PS_BASE = "ps_base"
PS_ORDER = "ps_order"
PS_HABIT = "ps_habit"
PAST_VERB = "past_verb"
PAST_HABIT = "past_habit"
NEG_DONT = "neg_dont"
NEG_DOESNT = "neg_doesnt"
NEG_DIDNT = "neg_didnt"
NEG_BASE = "neg_base"
Q_DO = "q_do"
Q_DOES = "q_does"
Q_DID = "q_did"
Q_BASE = "q_base"
OBJECT = "object"

SUBJECT_WEIGHT = 7
VERB_WEIGHT = 1
ADVERB_WEIGHT = 8
AUX_WEIGHT = 6
OBJECT_WEIGHT = 6
PHRASES_TO_UNLOCK_ADVERBS = 2
SENTENCES_TO_BANK = 3

AFFIRMATIVE = "affirmative"
NEGATIVE = "negative"
QUESTION = "question"
PRESENT = "present_simple"
PAST = "past_simple"
FUTURE = "future_simple"
PERFECT = "present_perfect"
CONTINUOUS = "present_continuous"

RULES = (
    Rule(
        id=PS_3SG,
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="verb", form="s"),
        result_kind="clause",
        result_level=2,
        result_tense=PRESENT,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id=PS_BASE,
        left=Pattern(kind="subject", agreement="not_3sg"),
        right=Pattern(kind="verb", form="base"),
        result_kind="clause",
        result_level=2,
        result_tense=PRESENT,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id=PAST_VERB,
        left=Pattern(kind="subject"),
        right=Pattern(kind="verb", form="past"),
        result_kind="clause",
        result_level=2,
        result_tense=PAST,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id=PS_HABIT,
        left=Pattern(kind="clause", tense=PRESENT),
        right=Pattern(kind="adverb", tense=PRESENT),
        result_kind="sentence",
        result_level=3,
        result_tense=PRESENT,
    ),
    Rule(
        id=PAST_HABIT,
        left=Pattern(kind="clause", tense=PAST),
        right=Pattern(kind="adverb", tense=PAST),
        result_kind="sentence",
        result_level=3,
        result_tense=PAST,
    ),
    Rule(
        id=NEG_DONT,
        left=Pattern(kind="subject", agreement="not_3sg"),
        right=Pattern(kind="aux", form="dont"),
        result_kind="negation",
        result_level=2,
        result_tense=PRESENT,
        polarity=NEGATIVE,
    ),
    Rule(
        id=NEG_DOESNT,
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="aux", form="doesnt"),
        result_kind="negation",
        result_level=2,
        result_tense=PRESENT,
        polarity=NEGATIVE,
    ),
    Rule(
        id=NEG_DIDNT,
        left=Pattern(kind="subject"),
        right=Pattern(kind="aux", form="didnt"),
        result_kind="negation",
        result_level=2,
        result_tense=PAST,
        polarity=NEGATIVE,
    ),
    Rule(
        id=NEG_BASE,
        left=Pattern(kind="negation"),
        right=Pattern(kind="verb", form="base"),
        result_kind="clause",
        result_level=2,
        polarity=NEGATIVE,
    ),
    Rule(
        id=Q_DO,
        left=Pattern(kind="aux", form="do"),
        right=Pattern(kind="subject", agreement="not_3sg"),
        result_kind="question",
        result_level=2,
        result_tense=PRESENT,
        polarity=QUESTION,
    ),
    Rule(
        id=Q_DOES,
        left=Pattern(kind="aux", form="does"),
        right=Pattern(kind="subject", agreement="3sg"),
        result_kind="question",
        result_level=2,
        result_tense=PRESENT,
        polarity=QUESTION,
    ),
    Rule(
        id=Q_DID,
        left=Pattern(kind="aux", form="did"),
        right=Pattern(kind="subject"),
        result_kind="question",
        result_level=2,
        result_tense=PAST,
        polarity=QUESTION,
    ),
    Rule(
        id=Q_BASE,
        left=Pattern(kind="question"),
        right=Pattern(kind="verb", form="base"),
        result_kind="clause",
        result_level=2,
        polarity=QUESTION,
    ),
    Rule(
        id="fut_will",
        left=Pattern(kind="subject"),
        right=Pattern(kind="aux", form="will"),
        result_kind="chain",
        result_level=2,
        result_tense=FUTURE,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="fut_wont",
        left=Pattern(kind="subject"),
        right=Pattern(kind="aux", form="wont"),
        result_kind="negation",
        result_level=2,
        result_tense=FUTURE,
        polarity=NEGATIVE,
    ),
    Rule(
        id="fut_willq",
        left=Pattern(kind="aux", form="willq"),
        right=Pattern(kind="subject"),
        result_kind="question",
        result_level=2,
        result_tense=FUTURE,
        polarity=QUESTION,
    ),
    Rule(
        id="fut_verb",
        left=Pattern(kind="chain"),
        right=Pattern(kind="verb", form="base"),
        result_kind="clause",
        result_level=2,
        result_tense=FUTURE,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="fut_habit",
        left=Pattern(kind="clause", tense=FUTURE),
        right=Pattern(kind="adverb", tense=FUTURE),
        result_kind="sentence",
        result_level=3,
        result_tense=FUTURE,
    ),
    Rule(
        id="perf_have",
        left=Pattern(kind="subject", agreement="not_3sg"),
        right=Pattern(kind="aux", form="have"),
        result_kind="chain",
        result_level=2,
        result_tense=PERFECT,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="perf_has",
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="aux", form="has"),
        result_kind="chain",
        result_level=2,
        result_tense=PERFECT,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="perf_havent",
        left=Pattern(kind="subject", agreement="not_3sg"),
        right=Pattern(kind="aux", form="havent"),
        result_kind="negation",
        result_level=2,
        result_tense=PERFECT,
        polarity=NEGATIVE,
    ),
    Rule(
        id="perf_hasnt",
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="aux", form="hasnt"),
        result_kind="negation",
        result_level=2,
        result_tense=PERFECT,
        polarity=NEGATIVE,
    ),
    Rule(
        id="perf_haveq",
        left=Pattern(kind="aux", form="haveq"),
        right=Pattern(kind="subject", agreement="not_3sg"),
        result_kind="question",
        result_level=2,
        result_tense=PERFECT,
        polarity=QUESTION,
    ),
    Rule(
        id="perf_hasq",
        left=Pattern(kind="aux", form="hasq"),
        right=Pattern(kind="subject", agreement="3sg"),
        result_kind="question",
        result_level=2,
        result_tense=PERFECT,
        polarity=QUESTION,
    ),
    Rule(
        id="perf_verb",
        left=Pattern(kind="chain"),
        right=Pattern(kind="verb", form="pp"),
        result_kind="clause",
        result_level=2,
        result_tense=PERFECT,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="perf_neg_verb",
        left=Pattern(kind="negation"),
        right=Pattern(kind="verb", form="pp"),
        result_kind="clause",
        result_level=2,
        result_tense=PERFECT,
        polarity=NEGATIVE,
    ),
    Rule(
        id="perf_q_verb",
        left=Pattern(kind="question"),
        right=Pattern(kind="verb", form="pp"),
        result_kind="clause",
        result_level=2,
        result_tense=PERFECT,
        polarity=QUESTION,
    ),
    Rule(
        id="perf_habit",
        left=Pattern(kind="clause", tense=PERFECT),
        right=Pattern(kind="adverb", tense=PERFECT),
        result_kind="sentence",
        result_level=3,
        result_tense=PERFECT,
    ),
    Rule(
        id="cont_am",
        left=Pattern(kind="subject", agreement="1sg"),
        right=Pattern(kind="aux", form="am"),
        result_kind="chain",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="cont_is",
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="aux", form="is"),
        result_kind="chain",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="cont_are",
        left=Pattern(kind="subject", agreement="are"),
        right=Pattern(kind="aux", form="are"),
        result_kind="chain",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="cont_amnot",
        left=Pattern(kind="subject", agreement="1sg"),
        right=Pattern(kind="aux", form="amnot"),
        result_kind="negation",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=NEGATIVE,
    ),
    Rule(
        id="cont_isnt",
        left=Pattern(kind="subject", agreement="3sg"),
        right=Pattern(kind="aux", form="isnt"),
        result_kind="negation",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=NEGATIVE,
    ),
    Rule(
        id="cont_arent",
        left=Pattern(kind="subject", agreement="are"),
        right=Pattern(kind="aux", form="arent"),
        result_kind="negation",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=NEGATIVE,
    ),
    Rule(
        id="cont_amq",
        left=Pattern(kind="aux", form="amq"),
        right=Pattern(kind="subject", agreement="1sg"),
        result_kind="question",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=QUESTION,
    ),
    Rule(
        id="cont_isq",
        left=Pattern(kind="aux", form="isq"),
        right=Pattern(kind="subject", agreement="3sg"),
        result_kind="question",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=QUESTION,
    ),
    Rule(
        id="cont_areq",
        left=Pattern(kind="aux", form="areq"),
        right=Pattern(kind="subject", agreement="are"),
        result_kind="question",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=QUESTION,
    ),
    Rule(
        id="cont_verb",
        left=Pattern(kind="chain"),
        right=Pattern(kind="verb", form="ing"),
        result_kind="clause",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=AFFIRMATIVE,
    ),
    Rule(
        id="cont_neg_verb",
        left=Pattern(kind="negation"),
        right=Pattern(kind="verb", form="ing"),
        result_kind="clause",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=NEGATIVE,
    ),
    Rule(
        id="cont_q_verb",
        left=Pattern(kind="question"),
        right=Pattern(kind="verb", form="ing"),
        result_kind="clause",
        result_level=2,
        result_tense=CONTINUOUS,
        polarity=QUESTION,
    ),
    Rule(
        id="cont_habit",
        left=Pattern(kind="clause", tense=CONTINUOUS),
        right=Pattern(kind="adverb", tense=CONTINUOUS),
        result_kind="sentence",
        result_level=3,
        result_tense=CONTINUOUS,
    ),
    Rule(
        id=OBJECT,
        left=Pattern(kind="clause"),
        right=Pattern(kind="object"),
        result_kind="clause",
        result_level=2,
    ),
)

LABELS = {
    PS_3SG: "he/she/it + глагол с -s",
    PS_BASE: "I/you/we/they + глагол без -s",
    PS_ORDER: "порядок: подлежащее, затем глагол",
    PS_HABIT: "фраза + обстоятельство",
    PAST_VERB: "Past Simple: вторая форма глагола",
    PAST_HABIT: "прошедшая фраза + обстоятельство",
    NEG_DONT: "I/you/we/they + don't",
    NEG_DOESNT: "he/she/it + doesn't",
    NEG_DIDNT: "подлежащее + didn't",
    NEG_BASE: "после don't/doesn't/didn't глагол без -s",
    Q_DO: "Do + I/you/we/they",
    Q_DOES: "Does + he/she/it",
    Q_DID: "Did + подлежащее",
    Q_BASE: "после Do/Does/Did глагол без -s",
    OBJECT: "фраза + дополнение",
    "fut_will": "подлежащее + will",
    "fut_verb": "после will глагол без -s",
    "perf_has": "he/she/it + has",
    "perf_have": "I/you/we/they + have",
    "perf_verb": "после have/has третья форма",
    "cont_am": "I + am",
    "cont_is": "he/she/it + is",
    "cont_are": "you/we/they + are",
    "cont_verb": "после am/is/are форма с -ing",
}

AUX_FORMS = (
    ("dont", "don't", PRESENT, NEGATIVE),
    ("doesnt", "doesn't", PRESENT, NEGATIVE),
    ("didnt", "didn't", PAST, NEGATIVE),
    ("do", "Do", PRESENT, QUESTION),
    ("does", "Does", PRESENT, QUESTION),
    ("did", "Did", PAST, QUESTION),
    ("will", "will", FUTURE, AFFIRMATIVE),
    ("wont", "won't", FUTURE, NEGATIVE),
    ("willq", "Will", FUTURE, QUESTION),
    ("have", "have", PERFECT, AFFIRMATIVE),
    ("has", "has", PERFECT, AFFIRMATIVE),
    ("havent", "haven't", PERFECT, NEGATIVE),
    ("hasnt", "hasn't", PERFECT, NEGATIVE),
    ("haveq", "Have", PERFECT, QUESTION),
    ("hasq", "Has", PERFECT, QUESTION),
    ("am", "am", CONTINUOUS, AFFIRMATIVE),
    ("is", "is", CONTINUOUS, AFFIRMATIVE),
    ("are", "are", CONTINUOUS, AFFIRMATIVE),
    ("amnot", "am not", CONTINUOUS, NEGATIVE),
    ("isnt", "isn't", CONTINUOUS, NEGATIVE),
    ("arent", "aren't", CONTINUOUS, NEGATIVE),
    ("amq", "Am", CONTINUOUS, QUESTION),
    ("isq", "Is", CONTINUOUS, QUESTION),
    ("areq", "Are", CONTINUOUS, QUESTION),
)


class PresentSimplePack:
    def __init__(self, lexicon: Lexicon):
        self.lexicon = lexicon
        self.rules = RULES
        self.adaptive_rules = frozenset({PS_3SG, PS_BASE, PAST_VERB, NEG_DOESNT, Q_DOES})
        self.phrases_to_unlock_adverbs = PHRASES_TO_UNLOCK_ADVERBS
        self.sentences_to_bank = SENTENCES_TO_BANK
        self.spawn_specs = _spawn_specs(lexicon)
        self.active_tense = PRESENT
        self.active_polarity = AFFIRMATIVE

    def is_goal(self, tile: Tile) -> bool:
        return tile.kind == "sentence" and tile.level >= 3

    def topic_label(self, rule_id: str) -> str:
        return LABELS.get(rule_id, rule_id)

    def subject(self, text: str, tile_id: str) -> Tile:
        return _find(self.spawn_specs, tile_id, kind="subject", text=text)

    def verb(self, lemma: str, form: str, tile_id: str) -> Tile:
        return _find(self.spawn_specs, tile_id, kind="verb", lemma=lemma, form=form)

    def adverb(self, text: str, tile_id: str) -> Tile:
        return _find(self.spawn_specs, tile_id, kind="adverb", text=text)

    def aux(self, form: str, tile_id: str) -> Tile:
        return _find(self.spawn_specs, tile_id, kind="aux", form=form)

    def object(self, text: str, tile_id: str) -> Tile:
        return _find(self.spawn_specs, tile_id, kind="object", text=text)

    def near_miss(self, left: Tile, right: Tile) -> Hint | None:
        mode_hint = self._mode_hint(left, right)
        if mode_hint is not None:
            return mode_hint
        if left.kind == "subject" and right.kind == "verb":
            return self._agreement_hint(left, right)
        if left.kind == "verb" and right.kind == "subject":
            return Hint(
                rule_id=PS_ORDER,
                text=(
                    f"{left.text} + {right.text} — порядок слов: "
                    "сначала подлежащее, потом глагол"
                ),
                left_id=left.id,
                right_id=right.id,
            )
        if left.kind == "adverb" and right.kind == "clause":
            return Hint(
                rule_id=PS_ORDER,
                text=f"{left.text} + {right.text} — обстоятельство ставится после фразы",
                left_id=left.id,
                right_id=right.id,
            )
        if left.kind == "object" and right.kind == "clause":
            return Hint(
                rule_id=OBJECT,
                text=f"{left.text} + {right.text} — дополнение ставится после фразы",
                left_id=left.id,
                right_id=right.id,
            )
        return None

    def _mode_hint(self, left: Tile, right: Tile) -> Hint | None:
        if self.active_polarity == NEGATIVE and left.kind == "subject" and right.kind == "verb":
            particle = _NEG_PARTICLE.get(self.active_tense, "don't / doesn't")
            return self._hint(
                NEG_BASE,
                left,
                right,
                f"для отрицания сначала частица {particle}, потом нужная форма глагола",
            )
        if self.active_polarity == QUESTION and left.kind == "subject" and right.kind == "verb":
            particle = _Q_PARTICLE.get(self.active_tense, "Do / Does")
            return self._hint(
                Q_BASE,
                left,
                right,
                f"вопрос начинается с {particle}, потом подлежащее и нужная форма глагола",
            )
        if (
            self.active_polarity == AFFIRMATIVE
            and self.active_tense in {FUTURE, PERFECT, CONTINUOUS}
            and left.kind == "subject"
            and right.kind == "verb"
        ):
            return self._hint(
                "fut_will" if self.active_tense == FUTURE else "perf_have",
                left,
                right,
                _AFFIRM_AUX[self.active_tense],
            )
        if (
            self.active_polarity == AFFIRMATIVE
            and self.active_tense == PAST
            and left.kind == "subject"
            and right.kind == "verb"
            and right.form != "past"
        ):
            expected = self.lexicon.verb_form(right.lemma, "past") or "вторая форма"
            return self._hint(
                PAST_VERB,
                left,
                right,
                f"в Past Simple нужна вторая форма: {expected}",
            )
        if left.kind == "subject" and right.kind == "aux":
            return self._aux_agreement_hint(left, right)
        if left.kind == "aux" and right.kind == "subject":
            return self._question_agreement_hint(left, right)
        expected_form = _VERB_AFTER.get(self.active_tense, "base")
        if left.kind in {"negation", "question", "chain"} and right.kind == "verb" and right.form != expected_form:
            label = _FORM_LABEL[expected_form]
            expected = self.lexicon.verb_form(right.lemma, expected_form) or label
            return self._hint(
                NEG_BASE if left.kind == "negation" else Q_BASE,
                left,
                right,
                f"после частицы нужна форма «{label}»: {expected}",
            )
        return None

    def _aux_agreement_hint(self, left: Tile, right: Tile) -> Hint | None:
        form = right.form
        first = _is_1sg(left)
        third = left.is_3sg()
        if form == "doesnt" and not third:
            return self._hint(NEG_DONT, left, right, "после I/you/we/they нужна частица don't")
        if form == "dont" and third:
            return self._hint(NEG_DOESNT, left, right, "для he/she/it нужна частица doesn't")
        if form in {"do", "does", "did", "willq", "haveq", "hasq", "amq", "isq", "areq"}:
            return self._hint(
                Q_BASE,
                left,
                right,
                "в вопросе частица стоит перед подлежащим",
            )
        if form in {"has", "hasnt"} and not third:
            particle = "hasn't" if form == "hasnt" else "has"
            other = "haven't" if form == "hasnt" else "have"
            return self._hint("perf_have", left, right, f"после I/you/we/they нужна частица {other}, не {particle}")
        if form in {"have", "havent"} and third:
            particle = "haven't" if form == "havent" else "have"
            other = "hasn't" if form == "havent" else "has"
            return self._hint("perf_has", left, right, f"для he/she/it нужна частица {other}, не {particle}")
        if form in {"am", "amnot"} and not first:
            other = "is" if third else "are"
            if form == "amnot":
                other = "isn't" if third else "aren't"
            return self._hint("cont_am", left, right, f"с этим подлежащим нужна частица {other}")
        if form in {"is", "isnt"} and first:
            other = "am not" if form == "isnt" else "am"
            return self._hint("cont_am", left, right, f"после I нужна частица {other}")
        if form in {"is", "isnt"} and not third:
            other = "aren't" if form == "isnt" else "are"
            return self._hint("cont_are", left, right, f"после you/we/they нужна частица {other}")
        if form in {"are", "arent"} and first:
            other = "am not" if form == "arent" else "am"
            return self._hint("cont_am", left, right, f"после I нужна частица {other}")
        if form in {"are", "arent"} and third:
            other = "isn't" if form == "arent" else "is"
            return self._hint("cont_is", left, right, f"для he/she/it нужна частица {other}")
        return None

    def _question_agreement_hint(self, left: Tile, right: Tile) -> Hint | None:
        form = left.form
        first = _is_1sg(right)
        third = right.is_3sg()
        if form == "do" and third:
            return self._hint(Q_DOES, left, right, "перед he/she/it нужно Does")
        if form == "does" and not third:
            return self._hint(Q_DO, left, right, "перед I/you/we/they нужно Do")
        if form == "haveq" and third:
            return self._hint("perf_hasq", left, right, "перед he/she/it нужно Has")
        if form == "hasq" and not third:
            return self._hint("perf_haveq", left, right, "перед I/you/we/they нужно Have")
        if form == "amq" and not first:
            other = "Is" if third else "Are"
            return self._hint("cont_amq", left, right, f"перед этим подлежащим нужно {other}")
        if form == "isq" and first:
            return self._hint("cont_amq", left, right, "перед I нужно Am")
        if form == "isq" and not third:
            return self._hint("cont_areq", left, right, "перед you/we/they нужно Are")
        if form == "areq" and first:
            return self._hint("cont_amq", left, right, "перед I нужно Am")
        if form == "areq" and third:
            return self._hint("cont_isq", left, right, "перед he/she/it нужно Is")
        return None

    def _agreement_hint(self, left: Tile, right: Tile) -> Hint:
        if left.is_3sg():
            expected = self.lexicon.verb_form(right.lemma, "s") or "глагол с -s"
            return self._hint(
                PS_3SG,
                left,
                right,
                f"для he/she/it в Present Simple нужно {expected}",
            )
        expected = self.lexicon.verb_form(right.lemma, "base") or "глагол без -s"
        return self._hint(
            PS_BASE,
            left,
            right,
            f"после I/you/we/they форма без -s: {expected}",
        )

    def _hint(self, rule_id: str, left: Tile, right: Tile, text: str) -> Hint:
        return Hint(
            rule_id=rule_id,
            text=f"{left.text} + {right.text} — {text}",
            left_id=left.id,
            right_id=right.id,
        )


def _spawn_specs(lexicon: Lexicon) -> tuple[SpawnSpec, ...]:
    specs: list[SpawnSpec] = []
    for subject in lexicon.subjects:
        is_3sg = subject["person"] == 3 and subject["number"] == "sg"
        specs.append(
            SpawnSpec(
                weight=SUBJECT_WEIGHT,
                boost_rules=frozenset({PS_3SG if is_3sg else PS_BASE}),
                kind="subject",
                text=subject["text"],
                person=subject["person"],
                number=subject["number"],
            )
        )
    for lemma, forms in lexicon.verbs.items():
        for form in ("base", "s", "past", "ing", "pp"):
            specs.append(
                SpawnSpec(
                    weight=VERB_WEIGHT,
                    boost_rules=frozenset({PS_3SG, PS_BASE, PAST_VERB}),
                    kind="verb",
                    text=forms[form],
                    lemma=lemma,
                    form=form,
                    tense=PAST if form == "past" else PRESENT,
                )
            )
    for adverb in lexicon.adverbs:
        specs.append(
            SpawnSpec(
                weight=ADVERB_WEIGHT,
                boost_rules=frozenset(),
                kind="adverb",
                text=adverb["text"],
                tense=adverb["tense"],
            )
        )
    for form, text, tense, polarity in AUX_FORMS:
        specs.append(
            SpawnSpec(
                weight=AUX_WEIGHT,
                boost_rules=frozenset(),
                kind="aux",
                text=text,
                form=form,
                tense=tense,
                polarity=polarity,
            )
        )
    for obj in lexicon.objects:
        specs.append(
            SpawnSpec(
                weight=OBJECT_WEIGHT,
                boost_rules=frozenset(),
                kind="object",
                text=obj["text"],
            )
        )
    return tuple(specs)


def _is_1sg(tile: Tile) -> bool:
    return tile.person == 1 and tile.number == "sg"


_NEG_PARTICLE = {
    PRESENT: "don't / doesn't",
    PAST: "didn't",
    FUTURE: "won't",
    PERFECT: "haven't / hasn't",
    CONTINUOUS: "am not / isn't / aren't",
}
_Q_PARTICLE = {
    PRESENT: "Do / Does",
    PAST: "Did",
    FUTURE: "Will",
    PERFECT: "Have / Has",
    CONTINUOUS: "Am / Is / Are",
}
_AFFIRM_AUX = {
    FUTURE: "сначала will, потом глагол без -s",
    PERFECT: "сначала have или has, потом третья форма глагола",
    CONTINUOUS: "сначала am, is или are, потом форма с -ing",
}
_VERB_AFTER = {PERFECT: "pp", CONTINUOUS: "ing"}
_FORM_LABEL = {"base": "глагол без -s", "pp": "третья форма", "ing": "форма с -ing"}


def _find(specs: tuple[SpawnSpec, ...], tile_id: str, **fields) -> Tile:
    for spec in specs:
        if all(getattr(spec, key) == value for key, value in fields.items()):
            return spec.to_tile(tile_id)
    raise KeyError(fields)
