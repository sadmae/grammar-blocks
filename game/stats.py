import json
from pathlib import Path

from game.tile import SpawnSpec

WEAK_THRESHOLD = 3
WEAK_BOOST = 1.5


class ErrorStats:
    """Журнал ошибок на диске. Вес спавна считается по ошибкам текущей партии."""

    def __init__(self, path: Path | None = None):
        self.path = path
        self.errors: dict[str, int] = {}
        if path is not None and path.exists():
            self.errors = _read_errors(path)

    def record(self, rule_id: str) -> None:
        self.errors[rule_id] = self.errors.get(rule_id, 0) + 1
        self.save()

    def count(self, rule_id: str) -> int:
        return self.errors.get(rule_id, 0)

    def save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"errors": self.errors}
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def effective_weight(spec: SpawnSpec, session_errors: dict[str, int]) -> float:
    weak = any(
        session_errors.get(rule_id, 0) >= WEAK_THRESHOLD for rule_id in spec.boost_rules
    )
    if weak:
        return spec.weight * WEAK_BOOST
    return spec.weight


def _read_errors(path: Path) -> dict[str, int]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    errors = raw.get("errors", {})
    if not isinstance(errors, dict):
        return {}
    cleaned: dict[str, int] = {}
    for key, value in errors.items():
        cleaned[str(key)] = int(value)
    return cleaned
