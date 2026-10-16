from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    id: str
    text: str
    kind: str
    level: int
    lemma: str | None = None
    form: str | None = None
    person: int | None = None
    number: str | None = None
    tense: str | None = None

    def is_3sg(self) -> bool:
        return self.person == 3 and self.number == "sg"


@dataclass(frozen=True)
class SpawnSpec:
    weight: float
    boost_rules: frozenset[str]
    kind: str
    text: str
    level: int = 1
    lemma: str | None = None
    form: str | None = None
    person: int | None = None
    number: str | None = None
    tense: str | None = None
    polarity: str | None = None

    def to_tile(self, tile_id: str) -> Tile:
        return Tile(
            id=tile_id,
            text=self.text,
            kind=self.kind,
            level=self.level,
            lemma=self.lemma,
            form=self.form,
            person=self.person,
            number=self.number,
            tense=self.tense,
        )
