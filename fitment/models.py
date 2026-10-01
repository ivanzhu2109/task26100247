"""数据模型：目录、适配矩阵、零件、BOM。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """一个配置：车型、年份、排量(毫升)、变速箱。"""
    model: str
    year: int
    displacement: int
    transmission: str


@dataclass(frozen=True)
class MatrixRow:
    """适配矩阵一行：车型/变速箱为允许值集合，年份/排量为闭区间。"""
    models: frozenset[str]
    transmissions: frozenset[str]
    year_min: int
    year_max: int
    displacement_min: int
    displacement_max: int


Matrix = tuple[MatrixRow, ...]


@dataclass(frozen=True)
class Catalog:
    """目录：声明各维度合法取值。"""
    models: tuple[str, ...]
    years: tuple[int, ...]
    displacements: tuple[int, ...]
    transmissions: tuple[str, ...]


@dataclass(frozen=True)
class Part:
    """零件：允许矩阵 + 禁用矩阵。"""
    part_id: str
    allow: Matrix = ()
    deny: Matrix = ()


@dataclass(frozen=True)
class BomEntry:
    """BOM条目：引用零件、必装位置、启用条件矩阵。"""
    entry_id: str
    part_id: str
    position: str
    enable: Matrix = ()


@dataclass(frozen=True)
class Bom:
    """BOM：必装位置集合、目标范围矩阵、条目列表。"""
    bom_id: str
    positions: frozenset[str]
    target: Matrix
    entries: tuple[BomEntry, ...] = ()
