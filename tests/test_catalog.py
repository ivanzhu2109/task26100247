from bomcheck import Catalog, Config, Matrix, MatrixRow


def make_catalog():
    return Catalog(
        models=frozenset({"Alpha", "Beta"}),
        years=frozenset({2023, 2024}),
        displacements=frozenset({1498, 1998}),
        transmissions=frozenset({"AT", "MT"}),
    )


def test_configs_in_clips_to_declared_values():
    catalog = make_catalog()
    # 行覆盖目录未声明的取值（Gamma、2025、2500、DCT），应被裁剪
    matrix = Matrix.from_rows(
        [
            MatrixRow(
                models=frozenset({"Alpha", "Gamma"}),
                year_min=2024,
                year_max=2025,
                displacement_min=1998,
                displacement_max=2500,
                transmissions=frozenset({"AT", "DCT"}),
            )
        ]
    )
    assert catalog.configs_in(matrix) == [Config("Alpha", 2024, 1998, "AT")]


def test_configs_in_unions_and_sorts():
    catalog = make_catalog()
    matrix = Matrix.from_rows(
        [
            MatrixRow(
                models=frozenset({"Beta"}),
                year_min=2023,
                year_max=2023,
                displacement_min=1498,
                displacement_max=1498,
                transmissions=frozenset({"MT"}),
            ),
            MatrixRow(
                models=frozenset({"Alpha"}),
                year_min=2024,
                year_max=2024,
                displacement_min=1998,
                displacement_max=1998,
                transmissions=frozenset({"AT", "MT"}),
            ),
            # 与上一行完全重叠，应去重
            MatrixRow(
                models=frozenset({"Alpha"}),
                year_min=2024,
                year_max=2024,
                displacement_min=1998,
                displacement_max=1998,
                transmissions=frozenset({"AT"}),
            ),
        ]
    )
    configs = catalog.configs_in(matrix)
    # 排序：车型字典序优先于年份，Alpha 2024 排在 Beta 2023 之前
    assert configs == [
        Config("Alpha", 2024, 1998, "AT"),
        Config("Alpha", 2024, 1998, "MT"),
        Config("Beta", 2023, 1498, "MT"),
    ]
