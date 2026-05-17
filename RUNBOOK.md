# Runbook

このリポジトリは、論文PDFから研究用の下書きを作るための実行手順をまとめたものです。

## 1. 最初にやること

1. VS Code でこのワークスペースを開く
2. Copilot Chat を Agent Mode にする
3. 使いたい論文PDFをワークスペース直下か任意の場所に置く

## 2. Docker でワークフローを動かす

```powershell
docker build -t multi-agent-research .
docker run --rm -v ${PWD}:/workspace -w /workspace multi-agent-research --paper "path/to/your_paper.pdf"
```

PowerShell ラッパーを使う場合:

```powershell
.\scripts\run_research_pipeline.ps1 -PaperPath "path/to/your_paper.pdf"
```

## 3. 出力されるもの

実行すると次が生成されます。

- `research/artifacts/summary.md`
- `research/artifacts/hypotheses.md`
- `research/artifacts/experiment_plan.md`
- `research/artifacts/code_hints.md`
- `research/generated_code/`
- `research/artifacts/draft_outline.md`
- `research/artifacts/final_draft.md`

## 4. その後に自分でやること

1. `research/artifacts/summary.md` を確認する
2. `research/artifacts/hypotheses.md` を見て、実験したい仮説を選ぶ
3. `research/generated_code/` の scaffold を Copilot で実装する
4. 実験を回して結果を保存する
5. `research/artifacts/final_draft.md` を実験結果で埋める

## 5. Copilot に投げる順番

```text
@paper_reader
`research/artifacts/summary.md` を読んで、論文の要点を要約して。
```

```text
@hypothesis
`research/artifacts/summary.md` を元に、改良仮説を3つ提案して。
```

```text
@experiment
仮説1を検証する実験計画を、評価指標・比較対象・失敗条件つきで作って。
```

```text
@code_reviewer
元コードが無い前提で、最小の code scaffold を実装する方針を提案して。
```

```text
@paper_writer
実験結果をもとに、Abstract, Introduction, Method, Results, Discussion を埋める草案を書いて。
```
