import json
from dataclasses import dataclass
from pathlib import Path

VERB_FORMS = ("base", "s", "past", "ing", "pp")


@dataclass(frozen=True)
class Lexicon:
    verbs: dict[str, dict[str, str]]
    subjects: tuple[dict, ...]
    adverbs: tuple[dict, ...]
    objects: tuple[dict, ...]

    def verb_form(self, lemma: str | None, form: str) -> str | None:
        if lemma is None:
            return None
        entry = self.verbs.get(lemma)
        if entry is None:
            return None
        return entry.get(form)


def load_lexicon(path: Path) -> Lexicon:
    data = json.loads(path.read_text(encoding="utf-8"))
    verbs: dict[str, dict[str, str]] = {}
    for item in data["verbs"]:
        lemma = item["lemma"]
        if lemma in verbs:
            raise ValueError(f"Повтор леммы в словаре: {lemma}")
        for form in VERB_FORMS:
            if not item.get(form):
                raise ValueError(f"У глагола {lemma} нет формы {form}")
        verbs[lemma] = item
    if not data["subjects"] or not data["adverbs"]:
        raise ValueError("В словаре нужны подлежащие и наречия")
    return Lexicon(
        verbs=verbs,
        subjects=tuple(data["subjects"]),
        adverbs=tuple(data["adverbs"]),
        objects=tuple(data.get("objects", ())),
    )
