# Agent 実行シーケンス（Copilot Agent Mode 用）

目的: `planner` → `manager` → `worker` の順で自律実行させるための、Copilot Chat に投げる具体的なプロンプト集。

前提:
- VS Code でワークスペースを開く
- Copilot Chat を Agent Mode にする
- `agents/*.agent.md`（例: `planner.agent.md`, `manager.agent.md`）がプロジェクト内にある
- 自動承認を行う場合は `chat.tools.autoApprove` を `true` にする（セキュリティ注意）

使い方の流れ:
1. まず `planner` に要件の整理を依頼する
2. `manager` にタスク割当を指示させる
3. `worker` を実行して結果を `agents/output.txt` に書かせる

----

## 1) Planner に投げる（要件抽出）
下のブロックを Copilot Chat の入力欄に貼って送信してください（@planner を使える場合は先頭に付けます）。

```
@planner
あなたは planner エージェントです。ワークスペース内の `agents/research_plan.md`（存在しない場合は `research_plan.md` を作成して、簡単な仮要件を作ってください）を読み、次の内容を `agents/mission_board.md` の「要約」欄に追記してください。

- 重要要件を最大5点で箇条書き
- 入力データの想定形式（CSV/TSV/JSON）
- 必要な解析出力（例: 平均、分散、プロット）
- 前処理に必要な処理（欠損処理、フィルタ条件）

出力は短く、箇条書きで。完了したら "PLANNER: DONE" と一行返してください。
```

期待される動作: Copilot が `agents/mission_board.md` を更新し、要約欄に要件を追加します。

----

## 2) Manager に投げる（タスク割当）
Planner の出力を受けて `manager` に次のプロンプトを投げます。

```
@manager
`agents/mission_board.md` を読み、planner が出した要件をもとに `worker` に実行させる具体的なタスクを作ってください。
出力フォーマットは以下の通りにしてください（プレーンテキスト）:

TASK:
<実行コマンド>

例:
TASK:
python agents/worker.py --run --data agents/sample_data.csv

完了したら "MANAGER: TASK ASSIGNED" と一行返してください。
```

期待される動作: `manager` が `agents/mission_board.md` に実行コマンドを追記、またはチャットに示します。

----

## 3) Worker に実行させる（自動実行 or 手動）
Manager の出力（TASK）を受けて `worker` に実行を依頼します。Copilot が端末実行をサポートしている場合はそのままターミナル実行を行えます。自動承認が無い場合は確認手順が入ります。

直接実行プロンプト（Copilot にターミナル操作を許可しているとき）:

```
@worker
実行コマンド: `python agents/worker.py --run --data agents/sample_data.csv`
上記をターミナルで実行し、`agents/output.txt` の内容をここに貼ってください。エラーが出た場合はエラーメッセージを添えてください。
```

もし Copilot がターミナル操作をしない（手動実行が必要）なら、ユーザーが次を実行します:

```powershell
python agents/worker.py --run --data agents/sample_data.csv
```

完了後、`agents/output.txt` の最初の20行をチャットに貼ってください。

----

## まとめて一括で投げる（自律シーケンス）
Copilot が複数のエージェント役割を切り替えられる場合、以下の一括指示で端から端まで自律的に回せることがあります（自動承認が有効でない場合は途中でユーザー承認が止まります）。

```
あなたは複数の役割を演じるエージェントです。以下の順で実行してください:
1) planner として `agents/research_plan.md` を読み、要点を `agents/mission_board.md` に書く
2) manager として `mission_board.md` を読んで実行コマンド（TASK）を決める
3) worker として決められたコマンドをターミナルで実行し、`agents/output.txt` の中身をここに貼る

途中でわからない点があれば質問してください。すべて実行したら "PIPELINE: COMPLETE" と一行で返してください。
```

注意: この一括指示は非常に強力ですが、Copilot の設定によっては一部操作（ファイル書き換え、ターミナル実行）で手動承認が必要になります。

----

## トラブルシューティング
- `agents/output.txt` が空のまま: `worker.py` 実行ログを確認。`--run` と `--data` を正しく指定しているか確認。
- pandas が無い場合: `pip install pandas` を行うと実データ処理が有効になります。
- Copilot がファイルを書き換えない/実行しない場合: Agent Mode の権限設定を確認。`chat.tools.autoApprove` を一時的に true にして試す。

----

このファイルを参照して Copilot に投げれば、実装から実行までを試すための最小限の自律ワークフローが回せます。必要なら、各ステップの出力テンプレート（ログフォーマット）も作成しますか？
