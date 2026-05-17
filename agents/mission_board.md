# mission_board.md

## ミッション（掲示板）

- 状態: new
- 要約: 実験計画の要件を読み、解析用のPython関数を作成して実行するプロトタイプを作る
- 入力ファイル: research_plan.md（存在しない場合は仮の要件を作成して良い）
- 出力: agents/output.txt に実行ログを残す

## 手順（エージェント間のバケツリレー）
1. `planner` が `research_plan.md` を読み、要件の要点を `mission_board.md` に書く
2. `manager` が要件を確認し、`worker` に実行タスクを割り当てる
3. `worker` が `worker.py` の関数を作成／実行して結果を `agents/output.txt` に書き込む

---
更新履歴:
