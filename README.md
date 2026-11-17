# A14 碳排放 MRV 核查仓

面向企业碳排放 MRV（监测、报告、核查）的数据工程基线：接入活动数据凭证，统一单位，按期间解析排放因子版本，计算排放量，识别历史重述，并保留从凭证到排放结果的可追溯血缘。

## 运行

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m carbon_mrv.cli demo --db .demo-data/mrv.db
PYTHONPATH=src python3 -m carbon_mrv.cli ingest --evidence testdata/evidence.jsonl --factors testdata/factors.jsonl --db data/mrv.db
PYTHONPATH=src python3 -m carbon_mrv.cli calculate --db data/mrv.db
PYTHONPATH=src python3 -m carbon_mrv.cli trace --evidence-id EV-ELEC-001 --db data/mrv.db
PYTHONPATH=src python3 -m carbon_mrv.cli report --db data/mrv.db
```

## 职责拆分

- `models`：凭证、活动数据、因子、排放行、重述和血缘模型。
- `evidence_ingestor`：凭证校验、重复上报选择与迟到识别。
- `unit_converter`：活动数据单位换算，不执行排放计算。
- `factor_catalog`：按期间选择有效因子版本。
- `emission_engine`：纯排放计算与计算问题收集。
- `restatement_detector`：比较前后期间排放量并生成重述。
- `lineage`：构建凭证到排放行的追溯关系。
- 各 Repository：凭证、因子、当前排放行、重述和血缘分别存储。
- `service`：接入和计算用例编排。
- `report_queries` / `report` / `presentation` / `cli`：查询、组装、展示和参数解析。

## 可继续扩展的题目方向

1. 接入 Scope 1/2/3 多活动类型和排放因子地域版本。
2. 增加凭证文件哈希校验、附件存储和审计签章。
3. 实现期间关账、补录审批和重述版本链。
4. 将当前行表升级为 SCD2 排放事实表并支持按月增量重算。
