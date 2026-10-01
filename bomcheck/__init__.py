"""车型适配与选装 BOM 校验库。

目录与 BOM 从本地 JSON 载入，运行数据保存在内存，由上层直接调用。
"""

from .matrix import MatrixRow, Matrix
from .catalog import Config, Catalog
from .parts import Part
from .bom import Bom, BomEntry, ConfigIssue, ValidationResult
from .loader import load_catalog, load_bom

__all__ = [
    "MatrixRow",
    "Matrix",
    "Config",
    "Catalog",
    "Part",
    "Bom",
    "BomEntry",
    "ConfigIssue",
    "ValidationResult",
    "load_catalog",
    "load_bom",
]
