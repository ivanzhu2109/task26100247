"""BOM校验：漏装、重复占位、零件不适配。"""
from __future__ import annotations

from dataclasses import dataclass

from .matrix import matrix_matches
from .models import Bom, Catalog, Config, Part


@dataclass(frozen=True)
class ConfigIssue:
    """单个配置上的问题。"""
    config: Config
    missing_positions: tuple[str, ...] = ()
    duplicate_positions: tuple[str, ...] = ()
    unfit_entries: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    """整份BOM校验结论。"""
    ok: bool
    first_issue: ConfigIssue | None = None


def _config_key(config: Config) -> tuple[str, int, int, str]:
    """配置比较序：车型、年份、排量、变速箱。"""
    return (config.model, config.year, config.displacement, config.transmission)


def part_fits(part: Part, config: Config) -> bool:
    """零件是否适配配置：命中至少一条允许行且不命中任何禁用行。

    禁用优先；允许矩阵为空则不适配。
    """
    return matrix_matches(part.allow, config) and not matrix_matches(part.deny, config)


def target_configs(catalog: Catalog, bom: Bom) -> list[Config]:
    """目录声明取值中、命中BOM目标范围的全部配置，按比较序升序排列。"""
    configs = [
        Config(model, year, displacement, transmission)
        for model in catalog.models
        for year in catalog.years
        for displacement in catalog.displacements
        for transmission in catalog.transmissions
        if matrix_matches(bom.target, Config(model, year, displacement, transmission))
    ]
    configs.sort(key=_config_key)
    return configs


def check_config(bom: Bom, parts: dict[str, Part], config: Config) -> ConfigIssue | None:
    """检查单个配置；无问题返回None。"""
    enabled = [e for e in bom.entries if matrix_matches(e.enable, config)]

    missing: list[str] = []
    duplicate: list[str] = []
    for position in sorted(bom.positions):
        count = sum(1 for e in enabled if e.position == position)
        if count == 0:
            missing.append(position)
        elif count > 1:
            duplicate.append(position)

    unfit: list[str] = []
    for entry in enabled:
        part = parts.get(entry.part_id)
        if part is None:
            raise ValueError(f"条目 {entry.entry_id} 引用了未知零件 {entry.part_id}")
        if not part_fits(part, config):
            unfit.append(entry.entry_id)

    if missing or duplicate or unfit:
        return ConfigIssue(
            config=config,
            missing_positions=tuple(missing),
            duplicate_positions=tuple(duplicate),
            unfit_entries=tuple(unfit),
        )
    return None


def validate_bom(catalog: Catalog, bom: Bom, parts: dict[str, Part]) -> ValidationResult:
    """校验整份BOM；全部目标配置通过才ok，否则返回最小问题配置。"""
    for config in target_configs(catalog, bom):
        issue = check_config(bom, parts, config)
        if issue is not None:
            return ValidationResult(ok=False, first_issue=issue)
    return ValidationResult(ok=True)
