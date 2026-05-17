# Runbook

このリポジトリは、論文PDFから研究用の下書きを自動生成するワークフローをまとめたものです。

## 1. 最初にやること

1. VS Code でこのワークスペースを開く
2. Copilot Chat を Agent Mode にする（手元で Copilot を利用する場合）
3. 使いたい論文PDFをワークスペース直下か任意の場所に置く

## 2. Docker でワークフローを動かす（推奨）

依存はすべてコンテナ内でインストールされます。まずイメージをビルドしてください:

```powershell
docker build -t multi-agent-research .
```

オーケストレーター（paper → agents → 実験 → 結果取りまとめ）を実行する例:

```powershell
docker run --rm -v ${PWD}:/workspace -w /workspace --entrypoint python multi-agent-research scripts/orchestrator.py --paper "C:\Multi-AIAgent\your_paper.pdf"
```

補足: 結果トラッキングは MLflow を利用します（コンテナ内に `mlruns/` が作られます）。MLflow UI を確認するには:

```powershell
docker run --rm -v ${PWD}:/workspace -w /workspace -p 5000:5000 --entrypoint mlflow multi-agent-research ui --host 0.0.0.0 --port 5000
```

PowerShell ラッパー（ローカル実行）:

```powershell
.\scripts\run_orchestrator.ps1 -paperPath "C:\Multi-AIAgent\your_paper.pdf"
```

## 3. 自動で出力されるもの

実行すると次が生成されます（例）:

- `research/artifacts/summary.md` — 論文要約
- `research/artifacts/summary.reviewed.md` — 自動レビュー
- `research/artifacts/hypotheses.md` — 仮説候補
- `research/artifacts/selected_hypothesis.json` — 自動選択された仮説
- `research/generated_code/` — scaffold（自動生成/実装）
- `research/artifacts/train_history.json`, `research/artifacts/metrics.json`
- `research/artifacts/final_draft.md` — 自動で結果を反映した草案
- `research/orchestrator_outputs/` — 集約された出力と `manifest.json`
- `mlruns/`（コンテナ内） — MLflow トラッキングデータ

## 4. その後に自分でやること（自動化済みだが確認ポイント）

ワークフローは一気通貫で自動実行できますが、重要箇所は必ず人が確認してください。手順:

1. 生成された `research/artifacts/summary.md` を確認し、要点が妥当かチェックする（必要なら `research/artifacts/summary.reviewed.md` を参照）
2. `research/artifacts/selected_hypothesis.json` を確認して自動選択された仮説を承認または差し戻す（承認が必要な場合は `agents/hypothesis_selector.py` を手動実行して候補を再選択）
3. `research/generated_code/` に生成された scaffold を確認する。Copilot で細部を実装・強化する場合はここを編集する（自動パッチを適用する前に差分をレビューしてください）
4. オーケストレーターは自動で実験を回し結果を保存します（MLflow に記録）。手動で実行するには `scripts/orchestrator.py` または上の Docker コマンドを使ってください
5. `research/artifacts/final_draft.md` を確認し、必要に応じて結果や考察を手で補強する

注意: 自動変更はデフォルトでワークスペース内のファイルを上書きします。重要な変更を自動適用させたくない場合は、オーケストレーターを使わず個別の agent スクリプトを順に手動実行してください（例: `python agents/paper_reader.py` → `python agents/hypothesis_selector.py` → `python agents/code_generator.py` → `python agents/results_summarizer.py`）。

## 5. Copilot / Agent 呼び出しのテンプレート

手作業で Copilot に投げる場合の簡易テンプレート例:

```text
@paper_reader
`research/artifacts/summary.md` を読んで、主要な貢献と実験のポイントを400字以内で要約してください。
```

```text
@hypothesis
`research/artifacts/summary.md` を元に、検証可能な改良仮説を3つ提案し、それぞれの簡単な評価方法を添えてください。
```

```text
@code_reviewer / @code_generator
`research/generated_code/` の scaffold に対して、具体的な実装パッチを示してください（`train.py` と `eval.py` を実行可能にするための最小変更）。
```

## LGG リポジトリ統合

外部リポジトリ `yi-ding-cs/LGG` へ scaffold を自動適用する場合の手順:

```powershell
.\scripts\integrate_lgg.ps1
```

オプション指定例／注意点は `integrate_lgg.ps1` のヘルプを参照してください。自動適用後は `external/LGG` にバックアップ（`.magent.bak`）と統合用ブランチができます。変更は必ずレビュー・手動 push してください。

