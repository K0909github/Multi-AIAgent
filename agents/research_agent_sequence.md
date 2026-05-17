# 論文駆動研究ワークフロー（Copilot Agent Mode 用）

目的: 論文PDFを起点に、要約・仮説生成・実験計画・コード生成/改良・結果整理・論文草案を一連で回す。

必要な役割:
- `paper_reader`: 論文を読む
- `hypothesis`: 仮説を作る
- `experiment`: 実験計画を作る
- `code_reviewer`: 既存コードの改良点を出す
- `paper_writer`: 論文草案を書く

使い方の推奨順:
1. `paper_reader` が論文PDFから要点を抽出する
2. `hypothesis` が改良仮説を3つ出す
3. `experiment` が検証可能な実験計画に落とす
4. `code_reviewer` が、元コードが無ければ生成すべき scaffold を含めて差分案を出す
5. ユーザーまたは Copilot が scaffold を作成し、実験する
6. `paper_writer` が結果をもとに論文草案を書く

----

## 1) Paper Reader
```
@paper_reader
論文PDFを読み、次の形式で `research/artifacts/summary.md` を作ってください。

- 研究課題
- 提案手法
- 主要な実験設定
- 主要結果
- 限界
- 改良余地

出力は箇条書きで、LGGNet のような脳波・グラフ系モデルなら、どの入力表現・損失・構造が効いているかも明記してください。
```

## 2) Hypothesis
```
@hypothesis
`research/artifacts/summary.md` を読み、元論文を改良できそうな仮説を3つ出してください。

各仮説は次を含めること:
- 何を変えるか
- なぜ効くと考えるか
- どう検証するか
- 失敗した場合に何が分かるか
```

## 3) Experiment
```
@experiment
仮説を検証するための実験計画を作ってください。

各実験について:
- ベースライン
- 変更点
- 評価指標
- 必要なログ
- 期待される結果
- 失敗判定条件
```

## 4) Code Reviewer
```
@code_reviewer
既存コードが無い場合は、最小の code scaffold を生成する観点で提案してください。

出力内容:
- 変更ファイル候補
- 追加する関数/クラス
- どこをパラメータ化するか
- 実験時に切り替えやすいようにする設定
- 元コードが無い場合の baseline scaffold 構成
```

## 5) Paper Writer
```
@paper_writer
実験結果の要約をもとに、論文ドラフトの骨子を作ってください。

構成:
- Abstract
- Introduction
- Method
- Experiments
- Results
- Discussion
- Limitations
- Conclusion
```
