"""车型目录：声明四个维度的合法取值，并展开矩阵覆盖的配置。"""

from __future__ import annotations

from dataclasses import dataclass

from .matrix import Matrix


@dataclass(frozen=True, order=True)
class Config:
    """一个配置：车型、年份、整数毫升排量、变速箱。

    排序即最小问题配置的比较顺序：车型、年份、排量、变速箱。
    """

    model: str
    year: int
    displacement: int
    transmission: str


@dataclass(frozen=True)
class Catalog:
    """目录：声明各维度允许出现的取值。"""

    models: frozenset[str]
    years: frozenset[int]
    displacements: frozenset[int]
    transmissions: frozenset[str]

    def configs_in(self, matrix: Matrix) -> list[Config]:
        """展开矩阵在目录声明取值内覆盖的全部配置，按比较顺序排序。

        只考虑目录声明的取值：行内集合与目录取交集，
        年份/排量取闭区间内的目录声明值；多行并集去重。
        """
        configs: set[Config] = set()
        for row in matrix.rows:
            models = row.models & self.models
            transmissions = row.transmissions & self.transmissions
            years = {y for y in self.years if row.year_min <= y <= row.year_max}
            displacements = {
                d
                for d in self.displacements
                if row.displacement_min <= d <= row.displacement_max
            }
            for model in models:
                for year in years:
                    for displacement in displacements:
                        for transmission in transmissions:
                            configs.add(
                                Config(
                                    model=model,
                                    year=year,
                                    displacement=displacement,
                                    transmission=transmission,
                                )
                            )
        return sorted(configs)
