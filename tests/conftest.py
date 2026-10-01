from pathlib import Path

import pytest

from bomcheck import load_bom, load_catalog

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture()
def catalog_and_parts():
    return load_catalog(DATA_DIR / "catalog.json")


@pytest.fixture()
def catalog(catalog_and_parts):
    return catalog_and_parts[0]


@pytest.fixture()
def parts(catalog_and_parts):
    return catalog_and_parts[1]


@pytest.fixture()
def bom_pass():
    return load_bom(DATA_DIR / "bom_pass.json")


@pytest.fixture()
def bom_adjacent():
    return load_bom(DATA_DIR / "bom_adjacent.json")


@pytest.fixture()
def bom_deny_point():
    return load_bom(DATA_DIR / "bom_deny_point.json")
