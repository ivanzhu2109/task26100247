from bomcheck import Config, Matrix, MatrixRow


def make_row(**overrides):
    base = dict(
        models=frozenset({"Alpha"}),
        year_min=2023,
        year_max=2024,
        displacement_min=1498,
        displacement_max=1998,
        transmissions=frozenset({"AT"}),
    )
    base.update(overrides)
    return MatrixRow(**base)


def test_row_matches_closed_intervals():
    row = make_row()
    matrix = Matrix.from_rows([row])
    # 闭区间边界命中
    assert matrix.matches(Config("Alpha", 2023, 1498, "AT"))
    assert matrix.matches(Config("Alpha", 2024, 1998, "AT"))
    # 区间外不命中
    assert not matrix.matches(Config("Alpha", 2022, 1498, "AT"))
    assert not matrix.matches(Config("Alpha", 2025, 1498, "AT"))
    assert not matrix.matches(Config("Alpha", 2023, 1497, "AT"))
    assert not matrix.matches(Config("Alpha", 2023, 1999, "AT"))


def test_row_requires_set_membership():
    matrix = Matrix.from_rows([make_row()])
    assert not matrix.matches(Config("Beta", 2023, 1498, "AT"))
    assert not matrix.matches(Config("Alpha", 2023, 1498, "MT"))


def test_matrix_is_union_of_rows():
    matrix = Matrix.from_rows(
        [
            make_row(year_max=2023),
            make_row(year_min=2024, transmissions=frozenset({"MT"})),
        ]
    )
    assert matrix.matches(Config("Alpha", 2023, 1498, "AT"))
    assert matrix.matches(Config("Alpha", 2024, 1498, "MT"))
    assert not matrix.matches(Config("Alpha", 2024, 1498, "AT"))


def test_empty_matrix_matches_nothing():
    assert not Matrix().matches(Config("Alpha", 2023, 1498, "AT"))
