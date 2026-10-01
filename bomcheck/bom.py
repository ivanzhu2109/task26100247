"""选装 BOM：必装位置校验与整份 BOM 校验。"""

from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import Catalog, Config
from .matrix import Matrix
from .parts import Part


@dataclass(frozen=True)
class BomEntry:
    """BOM 条目：引用一个零件、一个必装位置，带启用条件矩阵。"""

    entry_id: str
    part_number: str
    position: str
    enable: Matrix


@dataclass(frozen=True)
class ConfigIssue:
    """单个配置上的问题。"""

    kind: str  # "missing" | "duplicate" | "unfit"
    position: str
    detail: str


@dataclass(frozen=True)
class ValidationResult:
    """整份 BOM 校验结论。"""

    ok: bool
    config: Config | None
    issues: tuple[ConfigIssue, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Bom:
    """选装 BOM：必装位置集合 + 条目列表 + 目标配置范围矩阵。"""

    bom_id: str
    required_positions: frozenset[str]
    entries: tuple[BomEntry, ...]
    target: Matrix

    def validate_config(
        self, config: Config, parts: dict[str, Part]
    ) -> tuple[ConfigIssue, ...]:
        """校验单个目标配置：漏装、重复占位、零件不适配。

        只计入命中启用条件的条目；每个必装位置必须恰有一个启用条目，
        且所有启用条目的零件都适配该配置。引用同一零件的条目分别计数。
        """
        issues: list[ConfigIssue] = []
        enabled = [entry for entry in self.entries if entry.enable.matches(config)]

        for position in sorted(self.required_positions):
            holders = [entry for entry in enabled if entry.position == position]
            if not holders:
                issues.append(
                    ConfigIssue("missing", position, "必装位置无启用条目")
                )
            elif len(holders) > 1:
                ids = ", ".join(entry.entry_id for entry in holders)
                issues.append(
                    ConfigIssue("duplicate", position, f"必装位置有多个启用条目: {ids}")
                )

        for entry in enabled:
            part = parts.get(entry.part_number)
            if part is None:
                issues.append(
                    ConfigIssue(
                        "unfit",
                        entry.position,
                        f"条目 {entry.entry_id} 引用了未知零件 {entry.part_number}",
                    )
                )
            elif not part.fits(config):
                issues.append(
                    ConfigIssue(
                        "unfit",
                        entry.position,
                        f"条目 {entry.entry_id} 的零件 {entry.part_number} 不适配该配置",
                    )
                )
        return tuple(issues)

    def validate(
        self, catalog: Catalog, parts: dict[str, Part]
    ) -> ValidationResult:
        """整份 BOM 校验：全部目标配置通过才通过，否则返回最小问题配置。

        配置按车型、年份、排量、变速箱升序扫描，首个存在问题的配置即最小
        问题配置；目标范围外的配置不影响结论。
        """
        for config in catalog.configs_in(self.target):
            issues = self.validate_config(config, parts)
            if issues:
                return ValidationResult(ok=False, config=config, issues=issues)
        return ValidationResult(ok=True, config=None)
