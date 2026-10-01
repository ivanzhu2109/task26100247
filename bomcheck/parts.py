"""零件：允许矩阵 + 禁用矩阵，禁用优先。"""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import Config
from .matrix import Matrix


@dataclass(frozen=True)
class Part:
    """零件适配规则：命中至少一条允许行且不命中任何禁用行才适配。"""

    part_number: str
    allow: Matrix
    deny: Matrix

    def fits(self, config: Config) -> bool:
        """判断零件是否适配该配置。

        命中至少一条允许行且不命中任何禁用行才适配；
        禁用优先，允许矩阵为空则不适配。
        """
        if self.deny.matches(config):
            return False
        return self.allow.matches(config)
