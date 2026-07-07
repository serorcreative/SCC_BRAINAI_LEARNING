"""Configuration de la couche d'apprentissage BrainAI (JSON, sans dépendance).

BrainAI Learning **lit** la mémoire BrainAI (11) via son interface publique et en
dérive des apprentissages **propositionnels** (jamais appliqués). Il ne possède ni
ne modifie aucune autre couche.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from scc_brainai_learning.core.errors import ConfigError

LEARNING_ROOT = Path(__file__).resolve().parents[3]       # .../12_BRAINAI_LEARNING
DEFAULT_SCC_ROOT = LEARNING_ROOT.parent                    # .../01_CCSC
DEFAULT_CONFIG_PATH = LEARNING_ROOT / "config" / "learning.json"

DEFAULT_AS_OF = "2026-07-06T00:00:00+00:00"


@dataclass
class LearningConfig:
    """Emplacements observés et seuils déterministes de détection."""

    learning_root: Path = LEARNING_ROOT
    scc_root: Path = DEFAULT_SCC_ROOT
    data_dir: Path = LEARNING_ROOT / "data"
    as_of: str = DEFAULT_AS_OF
    # Seuils de détection (déterministes).
    min_frequency: int = 2          # occurrences mini pour retenir un signal
    strong_frequency: int = 5       # seuil de confiance renforcée
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def memory_src(self) -> Path:
        return self.scc_root / "11_BRAINAI_MEMORY" / "src"

    @property
    def memory_data_dir(self) -> Path:
        override = self.extra.get("memory_data_dir")
        if override:
            return Path(override)
        return self.scc_root / "11_BRAINAI_MEMORY" / "data"

    @property
    def learnings_path(self) -> Path:
        return self.data_dir / "learnings.jsonl"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learning_root": str(self.learning_root),
            "data_dir": str(self.data_dir),
            "memory_data_dir": str(self.memory_data_dir),
            "as_of": self.as_of,
            "min_frequency": self.min_frequency,
            "strong_frequency": self.strong_frequency,
        }


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> LearningConfig:
    config = LearningConfig()
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.learning_root
    if "scc_root" in raw:
        config.scc_root = _resolve(base, raw["scc_root"])
    paths = raw.get("paths", {})
    if "data_dir" in paths:
        config.data_dir = _resolve(base, paths["data_dir"])
    config.as_of = str(raw.get("as_of", DEFAULT_AS_OF))
    thresholds = raw.get("thresholds", {})
    config.min_frequency = int(thresholds.get("min_frequency", config.min_frequency))
    config.strong_frequency = int(thresholds.get("strong_frequency", config.strong_frequency))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["LEARNING_ROOT", "DEFAULT_SCC_ROOT", "DEFAULT_AS_OF", "LearningConfig", "load_config"]
