"""车型适配与选装BOM校验的自动化测试。

小目录：车型 {Alpha, Beta} × 年份 {2023, 2024} × 排量 {1498, 1998} × 变速箱 {AT, MT}，
共16个配置，全部在BOM目标范围内。配置比较序为 (车型, 年份, 排量, 变速箱)，
因此全目录最小配置是 (Alpha, 2023, 1498, AT)。
"""
from __future__ import annotations

from pathlib import Path

import pytest

from fitment import (
    Config,
    load_bom,
    load_catalog,
    load_part,
    part_fits,
    target_configs,
    validate_bom,
)

DATA = Path(__file__).parent / "data"

ALL_CONFIGS = [
    Config(model, year, displacement, transmission)
    for model in ("Alpha", "Beta")
    for year in (2023, 2024)
    for displacement in (1498, 1998)
    for transmission in ("AT", "MT")
]

DENY_POINT = Config("Alpha", 2024, 1998, "MT")


@pytest.fixture
def catalog():
    return load_catalog(DATA / "catalog.json")


@pytest.fixture
def part_ok():
    return load_part(DATA / "part_engine_ok.json")


@pytest.fixture
def part_deny():
    return load_part(DATA / "part_engine_deny.json")


def test_target_configs_cover_whole_catalog(catalog):
    bom = load_bom(DATA / "bom_ok.json")
    assert target_configs(catalog, bom) == sorted(
        ALL_CONFIGS, key=lambda c: (c.model, c.year, c.displacement, c.transmission)
    )
    assert len(target_configs(catalog, bom)) == 16


def test_adjacent_allow_rows_cover_each_config(catalog, part_ok):
    """两条相邻允许行（2023行+2024行）共同覆盖全部16个目标配置。"""
    for config in ALL_CONFIGS:
        assert part_fits(part_ok, config), f"{config} 应适配"


def test_adjacent_allow_rows_bom_passes(catalog, part_ok):
    """两条相邻允许行共同覆盖目标范围时，整份BOM校验通过。"""
    bom = load_bom(DATA / "bom_ok.json")
    result = validate_bom(catalog, bom, {"P-ENG-A": part_ok})
    assert result.ok
    assert result.first_issue is None


def test_single_point_deny_fitment(catalog, part_deny):
    """允许域内部单点禁用：仅 (Alpha, 2024, 1998, MT) 不适配，其余15个配置适配。"""
    for config in ALL_CONFIGS:
        assert part_fits(part_deny, config) == (config != DENY_POINT), config


def test_single_point_deny_bom_rejected_and_located(catalog, part_deny):
    """单点禁用导致整份BOM拒绝，并精确定位到最小问题配置。"""
    bom = load_bom(DATA / "bom_deny.json")
    result = validate_bom(catalog, bom, {"P-ENG-B": part_deny})
    assert not result.ok
    issue = result.first_issue
    assert issue is not None
    assert issue.config == DENY_POINT
    assert issue.unfit_entries == ("E-ENG-1",)
    assert issue.missing_positions == ()
    assert issue.duplicate_positions == ()


def test_missing_position(catalog, part_ok):
    """gearbox 必装位置无启用条目：每个配置都漏装，最小问题配置为全目录最小者。"""
    bom = load_bom(DATA / "bom_missing.json")
    result = validate_bom(catalog, bom, {"P-ENG-A": part_ok})
    assert not result.ok
    issue = result.first_issue
    assert issue.config == Config("Alpha", 2023, 1498, "AT")
    assert issue.missing_positions == ("gearbox",)


def test_duplicate_position_same_part_counts_twice(catalog, part_ok):
    """两个条目引用同一零件仍分别计数：engine 位置出现重复占位。"""
    bom = load_bom(DATA / "bom_duplicate.json")
    result = validate_bom(catalog, bom, {"P-ENG-A": part_ok})
    assert not result.ok
    issue = result.first_issue
    assert issue.config == Config("Alpha", 2023, 1498, "AT")
    assert issue.duplicate_positions == ("engine",)


def test_empty_allow_matrix_never_fits(catalog):
    """允许矩阵为空则不适配。"""
    part = load_part(DATA / "part_engine_deny.json")
    empty_allow = type(part)(part_id="P-EMPTY", allow=(), deny=())
    for config in ALL_CONFIGS:
        assert not part_fits(empty_allow, config)


def test_configs_outside_target_ignored(catalog, part_deny):
    """目标范围外的配置不影响结论：目标只取 Beta，禁用点在 Alpha，应通过。"""
    bom = load_bom(DATA / "bom_deny.json")
    beta_only = type(bom)(
        bom_id=bom.bom_id,
        positions=bom.positions,
        target=(
            type(bom.target[0])(
                models=frozenset({"Beta"}),
                transmissions=frozenset({"AT", "MT"}),
                year_min=2023,
                year_max=2024,
                displacement_min=1498,
                displacement_max=1998,
            ),
        ),
        entries=bom.entries,
    )
    result = validate_bom(catalog, beta_only, {"P-ENG-B": part_deny})
    assert result.ok


def test_unknown_part_reference_raises(catalog):
    bom = load_bom(DATA / "bom_ok.json")
    with pytest.raises(ValueError, match="P-ENG-A"):
        validate_bom(catalog, bom, {})
