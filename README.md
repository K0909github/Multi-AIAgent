# Multi-AIAgent

論文PDFを起点に、Copilot Agent Mode で
要約 → 仮説生成 → 実験計画 → コード生成/改良 → 実験 → 論文草案
まで回す汎用研究ワークフローです。

まずは [RUNBOOK.md](RUNBOOK.md) を開いて、手順通りにコマンドを実行してください。

## 構成

### 主要コンポーネント

- `agents/research_agent_sequence.md`: Copilot に投げる役割分担プロンプト（ワークフロー全体の実行順と役割を定義）
- `agents/paper_reader.agent.md`: 論文読み取り用の指示書（PDF→要約抽出のルールやチェックポイント）
- `agents/hypothesis.agent.md`: 仮説生成用の指示書（要約を元に改善案・検証可能な仮説を生成するテンプレ）
- `agents/experiment.agent.md`: 実験計画用の指示書（評価指標、比較対象、失敗条件などを含む実験設計テンプレ）
- `agents/code_reviewer.agent.md`: コード改良案生成用の指示書（最小差分での改善案、テスト観点、リファクタ提案）
- `agents/paper_writer.agent.md`: 論文ドラフト用の指示書（Abstract/Introduction/Method/Results/Discussion の骨子生成）
- `research/research_workflow.py`: 論文PDFから草案と code scaffold を自動生成する CLI（PDF 抽出→要約→仮説→スキャフォールド生成の連携）
- `research/artifacts/`: 各ステージの生成物（summary.md, hypotheses.json, experiment_plan.md, final_draft.md 等）
- `research/generated_code/`: 元コードが無い場合に作る baseline scaffold（最小限の実行可能な雛形を格納）

### その他のファイル・フォルダ

- `agents/`（上記以外）: エージェントを補助するスクリプトや追加のプロンプト（`code_generator.py`, `paper_reader.py`, `worker.py` 等）
- `research/`（上記以外）: 自動化スクリプトや生成物の管理（`generated_code/`, `artifacts/` を含む）
- `scripts/`: パイプライン起動用スクリプト（PowerShell / Python）
- `tools/`: 補助ツールや統合用スクリプト（例: `lgg_integration.py`）
- ルート: `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `RUNBOOK.md` — 環境構築と実行手順を定義

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

## リポジトリ構成図（詳細）

以下はこのリポジトリの主要ファイルとフォルダ構成を示す図です。開発フローと成果物の流れを視覚化しています。

![リポジトリ構成図](docs/diagrams/structure.svg)

**図のテキスト版（補助）**

- Multi-AIAgent (ルート)
	- docker-compose.yml
	- Dockerfile
	- multi-aiagent-structure.html
	- requirements.txt
	- RUNBOOK.md
	- agents/  — Copilotエージェント指示書や補助スクリプト
		- agent_run_sequence.md
		- code_generator.py
		- code_reviewer.agent.md
		- experiment.agent.md
		- hypothesis_selector.py
		- hypothesis.agent.md
		- paper_reader.agent.md / paper_reader.py
		- paper_writer.agent.md
		- planner.agent.md
		- worker.py
	- research/ — 実験ワークフロー本体
		- README.md
		- research_workflow.py
		- artifacts/ (出力: summary, hypotheses, plan, draft 等)
		- generated_code/ (自動生成される scaffold)
	- scripts/ (パイプライン実行スクリプト)
	- tools/ (補助ツール)

このテキスト版は図の補助説明です。画像が小さい・レンダリングされない場合はこちらを参照してください。

### フォルダと主なファイルの説明

- **トップレベル**: `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `RUNBOOK.md` — 環境構築と実行手順を定義します。
- **agents/**: Copilot エージェント向けの指示書（`.agent.md`）と、役割を補助する Python スクリプト。ワークフロー（論文読み取り→仮説→実験→コード生成→論文作成）に沿ったプロンプト群が格納されています。
- **research/**: 自動化スクリプト (`research_workflow.py`) と、各ステージの出力を保存する `artifacts/`、および自動生成する `generated_code/` を含みます。
- **scripts/**: パイプライン起動用の PowerShell や Python スクリプト（例: `run_orchestrator.ps1` など）。
- **tools/**: 補助ツールや統合用スクリプト（例: `lgg_integration.py`）。

### 開発／実行の概略ワークフロー

1. `RUNBOOK.md` の手順に従って環境を起動する（`docker-compose up` 等）。
2. `agents/` の指示書を順に実行し、`research/artifacts/` に生成物を蓄積する。
3. `research/research_workflow.py` で論文から草案や code scaffold を自動生成する。
4. 実験を実行し、結果を `research/artifacts/` に反映して `paper_writer.agent.md` などで論文草案を生成する。

---

必要なら、このMermaid図を画像化して `docs/` に保存するワークフローも追加できます。続けますか？
