# fitment：车型适配与选装BOM校验库

纯 Python 库，由上层直接调用。目录与 BOM 从本地 JSON 载入，运行数据保存在内存，无任何外部服务依赖。

## 概念

- **配置**：`(车型, 年份, 排量毫升, 变速箱)` 四维，只考虑目录声明的取值。
- **适配矩阵**：每行指定车型/变速箱的允许值集合、年份/排量的闭区间，行内取交集、多行取并集。
- **零件适配**：命中至少一条允许行且不命中任何禁用行；禁用优先，允许矩阵为空则不适配。
- **BOM 校验**：对每个目标配置，只计入命中启用条件的条目；每个必装位置必须恰有一个启用条目（漏装 / 重复占位都会报错），且所有启用条目的零件都适配该配置。目标范围外的配置不影响结论。
- **结论**：全部目标配置通过才 `ok=True`，否则返回最小问题配置（按车型、年份、排量、变速箱排序，字符串字典序、数字升序）。

## JSON 格式

矩阵行统一为：

```json
{"models": ["Alpha"], "transmissions": ["AT", "MT"], "year": [2023, 2024], "displacement": [1498, 1998]}
```

- 目录 `catalog.json`：`{"models": [...], "years": [...], "displacements": [...], "transmissions": [...]}`
- 零件 `part.json`：`{"part_id": "...", "allow": [行...], "deny": [行...]}`
- BOM `bom.json`：`{"bom_id": "...", "positions": [...], "target": [行...], "entries": [{"entry_id", "part_id", "position", "enable": [行...]}]}`

示例见 `tests/data/`。

## 用法

```python
from fitment import load_catalog, load_part, load_bom, validate_bom

catalog = load_catalog("catalog.json")
part = load_part("part_engine_ok.json")
bom = load_bom("bom_ok.json")

result = validate_bom(catalog, bom, {part.part_id: part})
if not result.ok:
    issue = result.first_issue
    print(issue.config, issue.missing_positions, issue.duplicate_positions, issue.unfit_entries)
```

## 运行测试

```bash
python3 -m pytest tests/ -q
```
