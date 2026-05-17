# Research Workflow

目的: 論文PDFやテキストを起点に、Copilot Agent Mode で次の流れを回すための実験用ワークフロー。

流れ:
1. 論文を読み込む
2. 要点を抽出する
3. 仮説を作る
4. 実験計画を作る
5. 元コードが無ければ新規コード scaffold を生成する
6. コード改良を指示する
7. 実験結果を要約する
8. 論文ドラフトを作る

元の実装コードが無い場合でも、`research/generated_code/` に baseline scaffold を作ってから仮説検証を始められます。

使い方:
```powershell
python research/research_workflow.py --paper "path/to/your_paper.pdf"
```

または、`RUNBOOK.md` の順に従って Docker で実行できます。

出力:
- `research/artifacts/` に各ステージのJSON/Markdownを保存する
- `research/artifacts/final_draft.md` に論文草案を保存する

Copilot 用の推奨プロンプトは `agents/research_agent_sequence.md` を参照してください。
