"""从本地JSON载入目录、零件与BOM。

矩阵行JSON格式：
    {"models": [...], "transmissions": [...],
     "year": [最小, 最大], "displacement": [最小, 最大]}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Bom, BomEntry, Catalog, Matrix, MatrixRow, Part


def _read_json(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_row(raw: dict[str, Any]) -> MatrixRow:
    year_lo, year_hi = raw["year"]
    disp_lo, disp_hi = raw["displacement"]
    return MatrixRow(
        models=frozenset(raw["models"]),
        transmissions=frozenset(raw["transmissions"]),
        year_min=int(year_lo),
        year_max=int(year_hi),
        displacement_min=int(disp_lo),
        displacement_max=int(disp_hi),
    )


def _parse_matrix(raw: list[dict[str, Any]] | None) -> Matrix:
    return tuple(_parse_row(row) for row in raw or [])


def load_catalog(path: str | Path) -> Catalog:
    raw = _read_json(path)
    return Catalog(
        models=tuple(raw["models"]),
        years=tuple(int(y) for y in raw["years"]),
        displacements=tuple(int(d) for d in raw["displacements"]),
        transmissions=tuple(raw["transmissions"]),
    )


def load_part(path: str | Path) -> Part:
    raw = _read_json(path)
    return Part(
        part_id=raw["part_id"],
        allow=_parse_matrix(raw.get("allow")),
        deny=_parse_matrix(raw.get("deny")),
    )


def load_bom(path: str | Path) -> Bom:
    raw = _read_json(path)
    entries = tuple(
        BomEntry(
            entry_id=e["entry_id"],
            part_id=e["part_id"],
            position=e["position"],
            enable=_parse_matrix(e.get("enable")),
        )
        for e in raw.get("entries", [])
    )
    return Bom(
        bom_id=raw["bom_id"],
        positions=frozenset(raw["positions"]),
        target=_parse_matrix(raw.get("target")),
        entries=entries,
    )
