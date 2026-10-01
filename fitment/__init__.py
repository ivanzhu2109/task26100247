"""车型适配与选装BOM校验库。"""
from .loader import load_bom, load_catalog, load_part
from .models import Bom, BomEntry, Catalog, Config, MatrixRow, Part
from .validator import ConfigIssue, ValidationResult, part_fits, target_configs, validate_bom

__all__ = [
    "Bom",
    "BomEntry",
    "Catalog",
    "Config",
    "ConfigIssue",
    "MatrixRow",
    "Part",
    "ValidationResult",
    "load_bom",
    "load_catalog",
    "load_part",
    "part_fits",
    "target_configs",
    "validate_bom",
]
