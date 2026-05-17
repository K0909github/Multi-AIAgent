# Multi-AIAgent

論文PDFを起点に、Copilot Agent Mode で
要約 → 仮説生成 → 実験計画 → コード生成/改良 → 実験 → 論文草案
まで回す汎用研究ワークフローです。

まずは [RUNBOOK.md](RUNBOOK.md) を開いて、手順通りにコマンドを実行してください。

## 構成

- `agents/research_agent_sequence.md`: Copilot に投げる役割分担プロンプト
- `agents/paper_reader.agent.md`: 論文読み取り用の指示書
- `agents/hypothesis.agent.md`: 仮説生成用の指示書
- `agents/experiment.agent.md`: 実験計画用の指示書
- `agents/code_reviewer.agent.md`: コード改良案生成用の指示書
- `agents/paper_writer.agent.md`: 論文ドラフト用の指示書
- `research/research_workflow.py`: 論文PDFから草案と code scaffold を自動生成するCLI
- `research/artifacts/`: 各ステージの生成物
- `research/generated_code/`: 元コードが無い場合に作る baseline scaffold

## 使い方

1. [RUNBOOK.md](RUNBOOK.md) の手順に従って Docker でワークフローを実行する。
2. 生成された `research/artifacts/*.md` と `research/generated_code/` を Copilot に渡して、各役割を順番に実行する。
3. 実験結果を `research/artifacts/final_draft.md` に反映する。

## 元コードが無い論文にも使うには

元実装がなくても、論文から仮説を作り、`research/generated_code/` に baseline scaffold を作って回せます。

```text
@code_reviewer
論文要約と実験計画をもとに、元コードが無い前提で生成すべき最小の code scaffold を提案して。
```

## Copilot に投げる例

```text
@paper_reader
`research/artifacts/summary.md` を読み、論文の要点を3行で説明して。
```

```text
@hypothesis
`research/artifacts/summary.md` を元に、改良仮説を3つ提案して。
```

```text
@experiment
仮説1を検証するための実験計画を作って。評価指標、比較対象、失敗条件も含めて。
```

```text
@code_reviewer
元コードが無い前提で、最小差分の code scaffold と実装方針を提案して。
```

```text
@paper_writer
実験結果をもとに、論文草案の Abstract, Introduction, Method, Results, Discussion を書いて。
```

## 注意

- `research/research_workflow.py` は自動の下書き生成器です。実際の論文化では、Copilot で各段階を精査してから使ってください。
- PDF からの抽出には `pypdf` を使います。Docker ならコンテナ内に依存が入るので、ローカル環境に Python パッケージを入れなくても動かせます。

```powershell
pip install -r requirements.txt
```

- 自動承認が必要なら `.vscode/settings.json` の設定を調整してください。
