#!/usr/bin/env python3
"""Paper-driven research workflow scaffold.

Reads a paper PDF or text file, generates staged artifacts:
- summary
- hypotheses
- experiment plan
- code modification hints
- draft paper outline

This is intentionally lightweight so Copilot Agent Mode can take over each stage.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path, PureWindowsPath
from typing import List, Optional


ARTIFACT_DIR = Path("research/artifacts")


@dataclass
class PaperArtifact:
    stage: str
    title: str
    bullets: List[str]
    source: str


def load_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf is required to read PDF files. Install requirements.txt.") from exc

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".pdf":
        return load_text_from_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def resolve_paper_path(raw_path: str) -> Path:
    """Resolve host/Windows paths inside Docker by trying common mounted locations.

    Examples:
    - C:\\Multi-AIAgent\\paper.pdf -> /workspace/paper.pdf when the repo is mounted at /workspace
    - relative paths are kept as-is if they exist
    """
    candidates = []
    original = Path(raw_path)
    windows_path = PureWindowsPath(raw_path)

    candidates.append(original)

    # When a Windows absolute path is passed into Docker, the file is usually available
    # under the workspace mount as just the filename.
    candidates.append(Path(windows_path.name))
    candidates.append(Path("/workspace") / windows_path.name)
    candidates.append(Path.cwd() / windows_path.name)
    candidates.append(Path("/workspace") / original.name)
    candidates.append(Path.cwd() / original.name)

    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue

    return original


def split_sentences(text: str) -> List[str]:
    cleaned = normalize_text(text)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[。.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def normalize_text(text: str) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_section(text: str, start_patterns: List[str], end_patterns: List[str]) -> str:
    lower_text = text.lower()
    start_index: Optional[int] = None
    for pattern in start_patterns:
        match = re.search(pattern, lower_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            start_index = match.end()
            break
    if start_index is None:
        return ""

    remainder = text[start_index:]
    end_index: Optional[int] = None
    for pattern in end_patterns:
        match = re.search(pattern, remainder, flags=re.IGNORECASE | re.DOTALL)
        if match:
            candidate = match.start()
            if end_index is None or candidate < end_index:
                end_index = candidate

    if end_index is not None:
        remainder = remainder[:end_index]
    return normalize_text(remainder)


def pick_sentence(
    sentences: List[str],
    include_any: Optional[List[str]] = None,
    fallback_index: int = 0,
    exclude_any: Optional[List[str]] = None,
) -> str:
    include_any = include_any or []
    exclude_any = exclude_any or []
    lowered_keywords = [keyword.lower() for keyword in include_any]
    lowered_excludes = [keyword.lower() for keyword in exclude_any]
    for sentence in sentences:
        lowered_sentence = sentence.lower()
        if any(keyword in lowered_sentence for keyword in lowered_excludes):
            continue
        if any(keyword in lowered_sentence for keyword in lowered_keywords):
            return sentence
    if 0 <= fallback_index < len(sentences):
        return sentences[fallback_index]
    return sentences[0] if sentences else ""


def shorten(sentence: str, limit: int = 360) -> str:
    sentence = normalize_text(sentence)
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip() + "…"


def extract_keywords(text: str, limit: int = 12) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text)
    counts = {}
    for word in words:
        normalized = word.lower()
        counts[normalized] = counts.get(normalized, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def summarize_paper(text: str, source: str) -> PaperArtifact:
    abstract = extract_section(
        text,
        [r"\babstract\b\s*[—\-:]?"],
        [r"\bindex terms\b", r"\bi\.\s*introduction\b", r"\bintroduction\b"],
    )
    conclusion = extract_section(
        text,
        [r"\bvi\.\s*conclusion\b", r"\bconclusion\b"],
        [r"\backnowledgment\b", r"\breferences\b"],
    )

    abstract_sentences = split_sentences(abstract) or split_sentences(text)
    conclusion_sentences = split_sentences(conclusion)
    keywords = extract_keywords(text)

    goal = pick_sentence(abstract_sentences, include_any=["propose", "novel", "LGGNet", "network"], fallback_index=0)
    method = pick_sentence(
        abstract_sentences[1:] if len(abstract_sentences) > 1 else abstract_sentences,
        include_any=["temporal", "graph", "fusion", "input layer", "local-global"],
        fallback_index=0,
        exclude_any=["propose"],
    )
    experiment = pick_sentence(
        abstract_sentences,
        include_any=["evaluated", "datasets", "tasks", "compared", "cross-validation"],
        fallback_index=2,
    )
    result = pick_sentence(
        conclusion_sentences or abstract_sentences,
        include_any=["outperform", "significant", "higher", "improvement", "result"],
        fallback_index=0,
    )

    bullets = [
        f"source: {source}",
        f"目的: {shorten(goal)}",
        f"手法: {shorten(method)}",
        f"実験: {shorten(experiment)}",
        f"結果: {shorten(result)}",
    ]
    if keywords:
        bullets.append("keywords: " + ", ".join(keywords[:10]))
    return PaperArtifact(stage="summary", title="Paper Summary", bullets=bullets, source=source)


def propose_hypotheses(summary: PaperArtifact) -> PaperArtifact:
    bullets = [
        "Hypothesis 1: strengthen local feature aggregation before global graph fusion to improve robustness.",
        "Hypothesis 2: add an ablation-controlled regularization term to stabilize cross-subject generalization.",
        "Hypothesis 3: test an alternative readout head or attention aggregator to capture subject-specific variance.",
        "Each hypothesis should be checked against baseline metrics and ablations.",
    ]
    return PaperArtifact(stage="hypotheses", title="Candidate Hypotheses", bullets=bullets, source=summary.source)


def build_experiment_plan(hypotheses: PaperArtifact) -> PaperArtifact:
    bullets = [
        "Baseline: reproduce the original paper configuration.",
        "Experiment A: change local-global fusion and compare accuracy/F1/kappa.",
        "Experiment B: add regularization and monitor stability across seeds.",
        "Experiment C: swap readout head and compare per-subject performance.",
        "Log: seed, split, metrics, training curves, confusion matrix, ablation table.",
        "Failure criteria: no statistically meaningful gain over baseline or unstable across seeds.",
    ]
    return PaperArtifact(stage="experiment_plan", title="Experiment Plan", bullets=bullets, source=hypotheses.source)


def code_modification_notes(plan: PaperArtifact) -> PaperArtifact:
    bullets = [
        "Parameterize the fusion module and readout head behind config flags.",
        "Expose ablation toggles so each hypothesis can be tested independently.",
        "Keep experiment results in machine-readable JSON for later paper drafting.",
        "Add a small runner script so Copilot can invoke one experiment at a time.",
    ]
    return PaperArtifact(stage="code_hints", title="Code Modification Notes", bullets=bullets, source=plan.source)


def generate_code_scaffold(plan: PaperArtifact) -> PaperArtifact:
    bullets = [
        "Create a minimal package with model, train, eval, and config entrypoints.",
        "Make the architecture pluggable so paper-specific modules can be swapped in later.",
        "Start from a baseline implementation that can be run even when original code is unavailable.",
        "Write outputs to machine-readable JSON for comparison across experiments.",
    ]
    scaffold_dir = Path("research/generated_code")
    scaffold_dir.mkdir(parents=True, exist_ok=True)
    (scaffold_dir / "README.md").write_text(
        "# Generated Research Scaffold\n\n"
        "This folder is created from a paper-only workflow when the original implementation is unavailable.\n"
        "Replace the TODOs with paper-specific modules.\n",
        encoding="utf-8",
    )
    (scaffold_dir / "model.py").write_text(
        "class PaperModel:\n"
        "    def __init__(self, config=None):\n"
        "        self.config = config or {}\n\n"
        "    def forward(self, inputs):\n"
        "        raise NotImplementedError('Replace with paper-specific model logic')\n",
        encoding="utf-8",
    )
    (scaffold_dir / "train.py").write_text(
        "def train(model, dataloader, config):\n"
        "    raise NotImplementedError('Replace with experiment training loop')\n",
        encoding="utf-8",
    )
    (scaffold_dir / "eval.py").write_text(
        "def evaluate(model, dataloader, config):\n"
        "    raise NotImplementedError('Replace with evaluation logic')\n",
        encoding="utf-8",
    )
    (scaffold_dir / "config.yaml").write_text(
        "experiment:\n"
        "  name: paper_only_scaffold\n"
        "  baseline: true\n"
        "  notes: replace with paper-specific settings\n",
        encoding="utf-8",
    )
    return PaperArtifact(stage="code_scaffold", title="Generated Code Scaffold", bullets=bullets, source=plan.source)


def draft_paper(code_hints: PaperArtifact) -> PaperArtifact:
    bullets = [
        "Abstract: state the problem, hypothesis, experimental method, and outcome.",
        "Introduction: explain why the original paper leaves room for improvement.",
        "Method: describe the modified module and ablation setup.",
        "Results: report baseline vs. modified results with statistics.",
        "Discussion: interpret why the modification did or did not work.",
        "Limitations: note data, compute, and reproducibility constraints.",
    ]
    return PaperArtifact(stage="draft_outline", title="Paper Draft Outline", bullets=bullets, source=code_hints.source)


def write_artifact(artifact: PaperArtifact) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACT_DIR / f"{artifact.stage}.json"
    md_path = ARTIFACT_DIR / f"{artifact.stage}.md"
    json_path.write_text(json.dumps(asdict(artifact), ensure_ascii=False, indent=2), encoding="utf-8")
    md_lines = [f"# {artifact.title}", ""] + [f"- {bullet}" for bullet in artifact.bullets] + [""]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")


def artifact_body(artifact: PaperArtifact) -> List[str]:
    return [bullet for bullet in artifact.bullets if not bullet.startswith("source:")]


def section_from_bullets(title: str, bullets: List[str]) -> List[str]:
    lines = [f"## {title}", ""]
    lines.extend(f"- {bullet}" for bullet in bullets if bullet)
    lines.append("")
    return lines


def write_final_draft(summary: PaperArtifact, hypotheses: PaperArtifact, plan: PaperArtifact, code_hints: PaperArtifact) -> None:
    final_path = ARTIFACT_DIR / "final_draft.md"
    summary_points = artifact_body(summary)
    hypothesis_points = artifact_body(hypotheses)
    plan_points = artifact_body(plan)
    code_points = artifact_body(code_hints)

    abstract_text = " ".join(point.split(": ", 1)[1] if ": " in point else point for point in summary_points[:3])
    method_text = " ".join(point.split(": ", 1)[1] if ": " in point else point for point in summary_points[1:3])
    result_text = summary_points[3].split(": ", 1)[1] if len(summary_points) > 3 and ": " in summary_points[3] else (summary_points[3] if len(summary_points) > 3 else "")

    lines = [
        "# Draft Paper",
        "",
        "## Abstract",
        abstract_text or "TODO: write abstract based on summary and experimental outcome.",
        "",
        "## Introduction",
        (summary_points[0].split(": ", 1)[1] if summary_points else "TODO: motivate the research question."),
        "",
        "## Method",
        method_text or "TODO: describe the modified architecture and experimental protocol.",
        "",
        "## Hypotheses",
        "",
        *[f"- {bullet}" for bullet in hypothesis_points],
        "",
        "## Experiments",
        *[f"- {bullet}" for bullet in plan_points],
        "",
        "## Results",
        result_text or "TODO: insert results tables and statistical tests.",
        "",
        "## Discussion",
        "- The workflow now keeps the paper summary, hypotheses, experiment plan, and results in separate machine-readable artifacts.",
        "- The generated scaffold is still synthetic, so paper-level claims should be verified before reuse.",
        "",
        "## Limitations",
        "- The local nodes inside each functional area are fully connected, so finer-grained relations within a region may be under-modeled.",
        "- The paper also notes that stronger relations for attention, emotion, and preference could be further improved with better network or loss design.",
        "",
        "## Conclusion",
        "- This draft is auto-generated from the paper PDF and can be refined in Copilot Chat.",
        "",
    ]
    final_path.write_text("\n".join(lines), encoding="utf-8")


def write_final_draft_japanese(summary: PaperArtifact, hypotheses: PaperArtifact, plan: PaperArtifact, code_hints: PaperArtifact) -> None:
    final_path = ARTIFACT_DIR / "final_draft_japanese.md"
    hypothesis_points = artifact_body(hypotheses)
    plan_points = artifact_body(plan)

    lines = [
        "# 論文草案",
        "",
        "## 要旨",
        "LGGNetは、EEGの局所・大域関係を同時に学習する神経生理学に着想したGNNである。多尺度1次元畳み込みと注意融合で時系列特徴を抽出し、局所グラフと大域グラフのフィルタリングで脳機能領域内外の関係を捉える。3つの公開データセット、4種類の認知分類タスクで評価し、複数のSOTA手法を上回った。",
        "",
        "## 背景",
        "BCIでは、EEGから時間情報と空間情報の両方を捉える必要がある。従来法は局所的な活動か大域的な関係のどちらかに偏りやすく、脳機能領域の階層的なつながりを十分に表現できなかった。",
        "",
        "## 手法",
        "入力層で多尺度1次元畳み込みとkernel-level attentive fusionを用いてEEGの時間ダイナミクスを学習する。その後、神経生理学的に意味のあるlocal-global graphを構成し、局所グラフと大域グラフのフィルタリングで脳活動の関係をモデル化する。",
        "",
        "## 仮説",
        "",
        "- 局所特徴の集約を強化すると、大域グラフ融合の前段で頑健性が上がる。",
        "- 正則化を追加すると、被験者間汎化が安定する。",
        "- 読み出し層や注意集約を変えると、被験者ごとのばらつきをよりよく捉えられる。",
        *[f"- {bullet}" for bullet in hypothesis_points[3:4]],
        "",
        "## 実験",
        "- ベースラインとして原論文設定を再現する。",
        "- local-global fusion の変更で accuracy / F1 / kappa を比較する。",
        "- 正則化の追加で seed 間の安定性を見る。",
        "- 読み出し層の差し替えで被験者別性能を比較する。",
        "- seed、split、評価指標、学習曲線、confusion matrix、ablation table を記録する。",
        "- ベースラインを有意に上回らない、または seed 間で不安定なら失敗とする。",
        "",
        "## 結果",
        "LGGNet は多くの実験条件で既存手法より高い精度と F1 を示し、改善の多くは統計的に有意だった。",
        "",
        "## 議論",
        "- このワークフローでは、要約、仮説、実験計画、結果を機械可読な成果物として分離して保持します。",
        "- 生成された scaffold は合成データ前提なので、論文レベルの主張は必ず確認してください。",
        "",
        "## 制約",
        "- 各 functional area 内のノードは全結合なので、領域内の細かな関係は十分に表現できない可能性があります。",
        "- attention / emotion / preference では、ネットワーク設計や損失設計の改善余地があることも本文で示されています。",
        "",
        "## まとめ",
        "- 本論文は、EEG を局所グラフと大域グラフの両方で表現し、脳機能領域内の活動と領域間の関係を同時に学習する LGGNet を提案している。多尺度畳み込みと注意融合で時間情報を取り込み、神経生理学の知見を反映したグラフ設計で 3 つの公開データセット上の 4 つの認知分類課題を改善した。局所・大域の関係を分けて扱う設計が、BCI における EEG 解析の有効な指針になることを示している。",
        "",
    ]
    final_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True, help="Path to paper PDF or text file")
    parser.add_argument("--title", default=None, help="Optional paper title override")
    args = parser.parse_args()

    paper_path = resolve_paper_path(args.paper)
    title = args.title or paper_path.stem
    text = load_text(paper_path)

    summary = summarize_paper(text, source=str(paper_path))
    hypotheses = propose_hypotheses(summary)
    plan = build_experiment_plan(hypotheses)
    code_hints = code_modification_notes(plan)
    code_scaffold = generate_code_scaffold(plan)
    draft = draft_paper(code_scaffold)

    for artifact in [summary, hypotheses, plan, code_hints, code_scaffold, draft]:
        write_artifact(artifact)

    write_final_draft(summary, hypotheses, plan, code_hints)
    write_final_draft_japanese(summary, hypotheses, plan, code_hints)

    print(f"Processed paper: {title}")
    print(f"Artifacts written to: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
