# Copilot Agent Mode 用プロンプト例

以下は `planner`, `manager`, `worker` を Copilot の Agent Mode で運用する際に投げると良い具体的なプロンプト例です。

## 1) Planner に投げるプロンプト例
```
@planner
`research_plan.md` を読み、重要な要件を 5 点以内で箇条書きにしてください。出力は `mission_board.md` の「要約」欄に追記する形で記載してください。
特にデータ形式（CSV/TSV/JSON）、解析で必要な出力（平均、分散、グラフ等）、および簡単な前処理要件（欠損処理、フィルタリング条件）を明確にしてください。
```

## 2) Manager に投げるプロンプト例
```
@manager
`mission_board.md` を確認しました。planner の要件を受けて `worker` に渡す実行タスクを短く指示してください。
出力形式は `agents/output.txt` に書き込むログ形式で、最初に `TASK:`、その後に実行コマンド（例: `python agents/worker.py --run --data agents/sample_data.csv`）を示してください。
```

## 3) Worker 実行の指示例（手動プロンプト）
```
@worker
`agents/worker.py --run --data agents/sample_data.csv` を実行して、数値列の基本統計量（count, mean, std, min, max）を計算し、`agents/output.txt` に書き込んでください。実行ログをここに貼ってください。
```

## 注意点
- Copilot がファイル操作やターミナル実行に対して確認を求める場合は、VS Code の設定 `chat.tools.autoApprove` を適宜切り替えてください（自動承認はセキュリティリスクがあるため注意）。
