from bomcheck import Config, Matrix, MatrixRow, Part


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


def test_fits_when_allowed_and_not_denied():
    part = Part("P", Matrix.from_rows([make_row()]), Matrix())
    assert part.fits(Config("Alpha", 2023, 1498, "AT"))


def test_deny_takes_precedence_over_allow():
    part = Part(
        "P",
        Matrix.from_rows([make_row()]),
        Matrix.from_rows([make_row(year_min=2024, year_max=2024)]),
    )
    assert part.fits(Config("Alpha", 2023, 1498, "AT"))
    assert not part.fits(Config("Alpha", 2024, 1498, "AT"))


def test_empty_allow_matrix_never_fits():
    part = Part("P", Matrix(), Matrix())
    assert not part.fits(Config("Alpha", 2023, 1498, "AT"))
