# 出力テンプレート（例）

このファイルは `worker` が生成する出力の構造化テンプレート例です。Copilot で解析結果を一貫した形式で出力させる場合は、このフォーマットに従うように指示してください。

1) JSON フォーマット（推奨・機械可読）

例:

```json
{
  "run_time": "2026-05-17T12:34:56Z",
  "task_id": "task-001",
  "data_path": "agents/sample_data.csv",
  "summary": {
    "row_count": 5,
    "numeric_columns": ["value","score"],
    "missing": {"value": 1}
  },
  "stats": {
    "value": {"count":4, "mean":18.75, "std":7.5, "min":10, "max":30},
    "score": {"count":5, "mean":0.62, "std":0.17, "min":0.4, "max":0.9}
  },
  "notes": "Processed with pandas vX.Y",
  "errors": null
}
```

説明:
- `run_time`: 実行時刻（UTC）
- `task_id`: 任意のタスク識別子
- `summary`: データの要約（行数、数値列名、欠損の個数など）
- `stats`: 各数値列ごとの基本統計量
- `notes`/`errors`: 実行時のメタ情報

2) テキスト/ログフォーマット（人間可読）

例:

```
run_time: 2026-05-17T12:34:56Z
task_id: task-001
data_path: agents/sample_data.csv
summary: row_count=5 numeric_columns=[value,score] missing={value:1}
-- stats --
value: count=4 mean=18.75 std=7.5 min=10 max=30
score: count=5 mean=0.62 std=0.17 min=0.4 max=0.9
notes: Processed with pandas vX.Y
errors: None
```

指示テンプレート（Copilot に投げる短い命令）:

```
結果はJSONで出力してください。フォーマットは agents/output.json とし、`run_time`, `data_path`, `summary`, `stats`, `notes`, `errors` のキーを含めてください。
```
