"""适配矩阵匹配。"""
from __future__ import annotations

from .models import Config, Matrix, MatrixRow


def row_matches(row: MatrixRow, config: Config) -> bool:
    """配置是否命中矩阵行：车型/变速箱在允许集合内，年份/排量在闭区间内。"""
    return (
        config.model in row.models
        and config.transmission in row.transmissions
        and row.year_min <= config.year <= row.year_max
        and row.displacement_min <= config.displacement <= row.displacement_max
    )


def matrix_matches(matrix: Matrix, config: Config) -> bool:
    """配置是否命中矩阵（多行取并集，空矩阵不命中）。"""
    return any(row_matches(row, config) for row in matrix)
