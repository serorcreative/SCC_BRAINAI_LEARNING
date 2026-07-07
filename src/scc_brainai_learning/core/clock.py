"""Primitives déterministes : sérialisation canonique et empreintes.

La couche d'apprentissage est **entièrement déterministe** : les identifiants et
les empreintes des apprentissages dérivent de leur **contenu** (mêmes détections
⇒ mêmes apprentissages). Stdlib pur, aucune horloge murale n'est requise.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def short_id(prefix: str, obj: Any) -> str:
    """Identifiant déterministe dérivé du contenu (idempotence des apprentissages)."""
    return f"{prefix}_{digest(obj)[:12]}"


__all__ = ["canonical", "digest", "short_id"]
