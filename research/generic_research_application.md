# 汎用研究ワークフロー適用メモ

対象:
- 論文PDFだけはあるが、元の実装コードがない研究テーマ

使い方:
1. 論文PDFを `research/research_workflow.py` に渡す
2. 仮説と実験計画を作る
3. `research/generated_code/` に baseline scaffold を生成する
4. scaffold を Copilot で実装しながら改良する
5. 実験結果をもとに論文草案を作る

ポイント:
- 元コードが無くても、まず動く最小構成を作る
- その後に論文の仮説を差し込んで比較実験する
- 研究テーマごとの特殊ロジックは後から差し替える
