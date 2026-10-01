# 车型适配与选装 BOM 校验库

由上层直接调用的 Python 库：目录与 BOM 从本地 JSON 载入，运行数据保存在内存。

## 概念

- **配置**：车型、年份、整数毫升排量、变速箱四个维度，只考虑目录声明的取值。
- **适配矩阵**：每行指定车型/变速箱的允许值集合、年份/排量的闭区间，表示这些
  取值的任意组合；多行表示并集。
- **零件适配**：配置命中至少一条允许行且不命中任何禁用行才适配；禁用优先，
  允许矩阵为空则不适配。
- **BOM 校验**：对每个目标配置，只计入命中启用条件的条目；每个必装位置必须
  恰有一个启用条目，且所有启用条目的零件都适配该配置。引用同一零件的多个
  条目分别计数。目标范围外的配置不影响结论。
- **整份校验**：全部目标配置通过才通过；否则返回最小问题配置（按车型、年份、
  排量、变速箱排序，字符串字典序、数字升序）。

## 数据格式

矩阵行 JSON：

```json
{
  "models": ["Alpha"],
  "year_min": 2023, "year_max": 2024,
  "displacement_min": 1498, "displacement_max": 1998,
  "transmissions": ["AT"]
}
```

目录 JSON（见 `tests/data/catalog.json`）：`catalog` 声明四维度合法取值，
`parts` 给出每个零件的 `allow` / `deny` 矩阵。

BOM JSON（见 `tests/data/bom_pass.json`）：`required_positions` 必装位置集合、
`target` 目标配置范围矩阵、`entries` 条目（零件、位置、启用条件矩阵）。

## 用法

```python
from bomcheck import load_catalog, load_bom

catalog, parts = load_catalog("catalog.json")
bom = load_bom("bom.json")

result = bom.validate(catalog, parts)
if result.ok:
    print("全部目标配置通过")
else:
    print("最小问题配置:", result.config)
    for issue in result.issues:
        print(issue.kind, issue.position, issue.detail)
```

## 运行测试

无第三方运行时依赖，测试使用 pytest：

```bash
python3 -m pytest
```

## 目录结构

- `bomcheck/matrix.py` — 适配矩阵与行匹配
- `bomcheck/catalog.py` — 目录与配置展开（裁剪到目录声明取值、排序去重）
- `bomcheck/parts.py` — 零件适配判定（禁用优先）
- `bomcheck/bom.py` — 单配置校验与整份 BOM 校验
- `bomcheck/loader.py` — 本地 JSON 载入
- `tests/` — 自动化测试与示例数据
