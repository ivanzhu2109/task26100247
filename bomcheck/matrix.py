"""适配矩阵：车型/变速箱取值集合 + 年份/排量闭区间，多行取并集。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class MatrixRow:
    """矩阵的一行：四个维度取值的任意组合。"""

    models: frozenset[str]
    year_min: int
    year_max: int
    displacement_min: int
    displacement_max: int
    transmissions: frozenset[str]


@dataclass(frozen=True)
class Matrix:
    """适配矩阵，多行表示并集。"""

    rows: tuple[MatrixRow, ...] = field(default_factory=tuple)

    def matches(self, config: object) -> bool:
        """判断配置是否命中矩阵任意一行。

        config 需具有 model / year / displacement / transmission 属性。
        """
        for row in self.rows:
            if (
                config.model in row.models
                and row.year_min <= config.year <= row.year_max
                and row.displacement_min <= config.displacement <= row.displacement_max
                and config.transmission in row.transmissions
            ):
                return True
        return False

    @staticmethod
    def from_rows(rows: Iterable[MatrixRow]) -> "Matrix":
        return Matrix(rows=tuple(rows))
