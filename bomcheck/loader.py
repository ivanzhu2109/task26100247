"""从本地 JSON 文件载入目录与 BOM。

矩阵行 JSON 结构::

    {
      "models": ["A"],
      "year_min": 2020, "year_max": 2022,
      "displacement_min": 1500, "displacement_max": 2000,
      "transmissions": ["AT"]
    }

目录 JSON:: {"catalog": {...四维度取值列表...}, "parts": [...]}
BOM JSON:: {"bom_id": ..., "required_positions": [...],
            "target": [行...], "entries": [...]}
"""

from __future__ import annotations

import json
from pathlib import Path

from .bom import Bom
from .catalog import Catalog
from .bom import BomEntry
from .matrix import Matrix, MatrixRow
from .parts import Part


def _row(data: dict) -> MatrixRow:
    return MatrixRow(
        models=frozenset(data["models"]),
        year_min=int(data["year_min"]),
        year_max=int(data["year_max"]),
        displacement_min=int(data["displacement_min"]),
        displacement_max=int(data["displacement_max"]),
        transmissions=frozenset(data["transmissions"]),
    )


def _matrix(data: list[dict] | None) -> Matrix:
    return Matrix.from_rows(_row(item) for item in (data or []))


def load_catalog(path: str | Path) -> tuple[Catalog, dict[str, Part]]:
    """载入目录 JSON，返回目录与零件表。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_catalog = data["catalog"]
    catalog = Catalog(
        models=frozenset(raw_catalog["models"]),
        years=frozenset(int(y) for y in raw_catalog["years"]),
        displacements=frozenset(int(d) for d in raw_catalog["displacements"]),
        transmissions=frozenset(raw_catalog["transmissions"]),
    )
    parts = {
        item["part_number"]: Part(
            part_number=item["part_number"],
            allow=_matrix(item.get("allow")),
            deny=_matrix(item.get("deny")),
        )
        for item in data.get("parts", [])
    }
    return catalog, parts


def load_bom(path: str | Path) -> Bom:
    """载入 BOM JSON。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = tuple(
        BomEntry(
            entry_id=item["entry_id"],
            part_number=item["part_number"],
            position=item["position"],
            enable=_matrix(item.get("enable")),
        )
        for item in data.get("entries", [])
    )
    return Bom(
        bom_id=data["bom_id"],
        required_positions=frozenset(data["required_positions"]),
        entries=entries,
        target=_matrix(data["target"]),
    )
