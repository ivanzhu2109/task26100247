from pathlib import Path

from bomcheck import Config, load_bom, load_catalog

DATA_DIR = Path(__file__).parent / "data"


def test_load_catalog_declares_dimensions_and_parts():
    catalog, parts = load_catalog(DATA_DIR / "catalog.json")
    assert catalog.models == frozenset({"Alpha", "Beta"})
    assert catalog.years == frozenset({2023, 2024})
    assert catalog.displacements == frozenset({1498, 1998})
    assert catalog.transmissions == frozenset({"AT", "MT"})
    assert set(parts) == {"P-ENG-15", "P-ENG-20", "P-ADJ", "P-DENY"}
    assert len(parts["P-ADJ"].allow.rows) == 2
    assert len(parts["P-DENY"].deny.rows) == 1


def test_load_bom_and_validate_end_to_end():
    catalog, parts = load_catalog(DATA_DIR / "catalog.json")
    bom = load_bom(DATA_DIR / "bom_pass.json")
    assert bom.bom_id == "BOM-PASS"
    assert bom.required_positions == frozenset({"engine"})
    assert len(bom.entries) == 2
    assert bom.validate(catalog, parts).ok


def test_load_deny_bom_locates_minimal_config():
    catalog, parts = load_catalog(DATA_DIR / "catalog.json")
    bom = load_bom(DATA_DIR / "bom_deny_point.json")
    result = bom.validate(catalog, parts)
    assert not result.ok
    assert result.config == Config("Alpha", 2023, 1498, "AT")
