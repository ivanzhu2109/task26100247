"""BOM 校验业务测试。

小目录业务预期（tests/data/catalog.json）：
- 车型 Alpha/Beta，年份 2023/2024，排量 1498/1998 毫升，变速箱 AT/MT。
- P-ENG-15 适配全部 1498 毫升配置；P-ENG-20 适配全部 1998 毫升配置。
- P-ADJ 用两条相邻年份行（2023、2024）共同覆盖全部 16 个目标配置。
- P-DENY 适配 Alpha/1498 的 2023-2024 全部配置，但单点禁用
  (Alpha, 2023, 1498, AT)。
"""

import pytest

from bomcheck import (
    Bom,
    BomEntry,
    Config,
    Matrix,
    MatrixRow,
    Part,
)

# BOM-PASS 目标范围内全部 16 个配置的明确业务预期：
# (配置, 预期启用条目, 预期是否通过)
EXPECTED_PASS_CONFIGS = [
    (Config("Alpha", 2023, 1498, "AT"), "E-ENG-15", True),
    (Config("Alpha", 2023, 1498, "MT"), "E-ENG-15", True),
    (Config("Alpha", 2023, 1998, "AT"), "E-ENG-20", True),
    (Config("Alpha", 2023, 1998, "MT"), "E-ENG-20", True),
    (Config("Alpha", 2024, 1498, "AT"), "E-ENG-15", True),
    (Config("Alpha", 2024, 1498, "MT"), "E-ENG-15", True),
    (Config("Alpha", 2024, 1998, "AT"), "E-ENG-20", True),
    (Config("Alpha", 2024, 1998, "MT"), "E-ENG-20", True),
    (Config("Beta", 2023, 1498, "AT"), "E-ENG-15", True),
    (Config("Beta", 2023, 1498, "MT"), "E-ENG-15", True),
    (Config("Beta", 2023, 1998, "AT"), "E-ENG-20", True),
    (Config("Beta", 2023, 1998, "MT"), "E-ENG-20", True),
    (Config("Beta", 2024, 1498, "AT"), "E-ENG-15", True),
    (Config("Beta", 2024, 1498, "MT"), "E-ENG-15", True),
    (Config("Beta", 2024, 1998, "AT"), "E-ENG-20", True),
    (Config("Beta", 2024, 1998, "MT"), "E-ENG-20", True),
]


@pytest.mark.parametrize(
    "config, expected_entry, expected_ok", EXPECTED_PASS_CONFIGS
)
def test_pass_bom_per_config_expectations(
    bom_pass, parts, config, expected_entry, expected_ok
):
    enabled = [
        entry.entry_id for entry in bom_pass.entries if entry.enable.matches(config)
    ]
    assert enabled == [expected_entry]
    assert (bom_pass.validate_config(config, parts) == ()) is expected_ok


def test_pass_bom_whole_validation_ok(bom_pass, catalog, parts):
    result = bom_pass.validate(catalog, parts)
    assert result.ok
    assert result.config is None
    assert result.issues == ()


def test_adjacent_allow_rows_cover_target(bom_adjacent, catalog, parts):
    """两条相邻允许行（2023、2024）共同覆盖目标范围，整份 BOM 通过。"""
    target_configs = catalog.configs_in(bom_adjacent.target)
    assert len(target_configs) == 16
    for config in target_configs:
        assert parts["P-ADJ"].fits(config)
    result = bom_adjacent.validate(catalog, parts)
    assert result.ok


def test_single_point_deny_rejected_and_located(bom_deny_point, catalog, parts):
    """允许域内部存在单点禁用：拒绝并定位到最小问题配置。"""
    # 业务预期：目标 4 个配置中仅 (Alpha, 2023, 1498, AT) 被禁用
    expected = {
        Config("Alpha", 2023, 1498, "AT"): False,
        Config("Alpha", 2023, 1498, "MT"): True,
        Config("Alpha", 2024, 1498, "AT"): True,
        Config("Alpha", 2024, 1498, "MT"): True,
    }
    for config, fits in expected.items():
        assert parts["P-DENY"].fits(config) is fits

    result = bom_deny_point.validate(catalog, parts)
    assert not result.ok
    assert result.config == Config("Alpha", 2023, 1498, "AT")
    assert [issue.kind for issue in result.issues] == ["unfit"]
    assert result.issues[0].position == "engine"
    assert "P-DENY" in result.issues[0].detail


def make_row(**overrides):
    base = dict(
        models=frozenset({"Alpha"}),
        year_min=2023,
        year_max=2023,
        displacement_min=1498,
        displacement_max=1498,
        transmissions=frozenset({"AT"}),
    )
    base.update(overrides)
    return MatrixRow(**base)


def make_bom(entries, positions=("engine",), target_rows=None):
    rows = target_rows if target_rows is not None else [make_row()]
    return Bom(
        bom_id="B",
        required_positions=frozenset(positions),
        entries=tuple(entries),
        target=Matrix.from_rows(rows),
    )


def test_missing_position_detected(catalog, parts):
    entry = BomEntry("E1", "P-ENG-15", "engine", Matrix.from_rows([make_row()]))
    bom = make_bom([entry], positions=("engine", "radio"))
    result = bom.validate(catalog, parts)
    assert not result.ok
    assert result.config == Config("Alpha", 2023, 1498, "AT")
    assert [issue.kind for issue in result.issues] == ["missing"]
    assert result.issues[0].position == "radio"


def test_duplicate_position_detected_even_with_same_part(catalog, parts):
    """两个条目引用同一零件仍分别计数，构成重复占位。"""
    enable = Matrix.from_rows([make_row()])
    entries = [
        BomEntry("E1", "P-ENG-15", "engine", enable),
        BomEntry("E2", "P-ENG-15", "engine", enable),
    ]
    result = make_bom(entries).validate(catalog, parts)
    assert not result.ok
    assert [issue.kind for issue in result.issues] == ["duplicate"]
    assert "E1" in result.issues[0].detail
    assert "E2" in result.issues[0].detail


def test_disabled_entry_not_counted(catalog, parts):
    """未命中启用条件的条目不计入：启用条件互斥时不构成重复占位。"""
    entries = [
        BomEntry("E1", "P-ENG-15", "engine", Matrix.from_rows([make_row()])),
        BomEntry(
            "E2",
            "P-ENG-15",
            "engine",
            Matrix.from_rows([make_row(year_min=2024, year_max=2024)]),
        ),
    ]
    result = make_bom(entries).validate(catalog, parts)
    assert result.ok


def test_configs_outside_target_do_not_affect_result(catalog, parts):
    """目标范围外的配置不影响结论。"""
    # 零件仅适配 Alpha，但目标只含 Alpha：Beta 上不适配不影响结论
    entry = BomEntry("E1", "P-ADJ", "engine", Matrix.from_rows([make_row()]))
    narrow_part = Part(
        "P-NARROW",
        Matrix.from_rows([make_row()]),
        Matrix(),
    )
    bom = make_bom([BomEntry("E1", "P-NARROW", "engine", entry.enable)])
    result = bom.validate(catalog, {**parts, "P-NARROW": narrow_part})
    assert result.ok


def test_minimal_problem_config_ordering(catalog, parts):
    """最小问题配置按车型、年份、排量、变速箱顺序定位。"""
    # 零件禁用 (Beta, 2023, 1498, MT)；Alpha 全部适配
    deny_row = MatrixRow(
        models=frozenset({"Beta"}),
        year_min=2023,
        year_max=2023,
        displacement_min=1498,
        displacement_max=1498,
        transmissions=frozenset({"MT"}),
    )
    allow_row = MatrixRow(
        models=frozenset({"Alpha", "Beta"}),
        year_min=2023,
        year_max=2024,
        displacement_min=1498,
        displacement_max=1998,
        transmissions=frozenset({"AT", "MT"}),
    )
    part = Part("P-X", Matrix.from_rows([allow_row]), Matrix.from_rows([deny_row]))
    entry = BomEntry("E1", "P-X", "engine", Matrix.from_rows([allow_row]))
    bom = make_bom([entry], target_rows=[allow_row])
    result = bom.validate(catalog, {"P-X": part})
    assert not result.ok
    assert result.config == Config("Beta", 2023, 1498, "MT")
