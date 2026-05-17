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
from pathlib import Path
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


def split_sentences(text: str) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[。.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def extract_keywords(text: str, limit: int = 12) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text)
    counts = {}
    for word in words:
        normalized = word.lower()
        counts[normalized] = counts.get(normalized, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def summarize_paper(text: str, source: str) -> PaperArtifact:
    sentences = split_sentences(text)
    keywords = extract_keywords(text)
    bullets = []
    bullets.append(f"source: {source}")
    if sentences:
        bullets.append(f"first_sentence: {sentences[0][:240]}")
    if len(sentences) > 1:
        bullets.append(f"second_sentence: {sentences[1][:240]}")
    if keywords:
        bullets.append("keywords: " + ", ".join(keywords[:10]))
    bullets.append("TODO: replace this automatic summary with Copilot-edited scientific summary")
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


def write_final_draft(draft: PaperArtifact) -> None:
    final_path = ARTIFACT_DIR / "final_draft.md"
    lines = [
        "# Draft Paper",
        "",
        "## Abstract",
        "TODO: write abstract based on summary and experimental outcome.",
        "",
        "## Introduction",
        "TODO: motivate the research question.",
        "",
        "## Method",
        "TODO: describe the modified architecture and experimental protocol.",
        "",
        "## Experiments",
        "TODO: list baselines, metrics, and ablations.",
        "",
        "## Results",
        "TODO: insert results tables and statistical tests.",
        "",
        "## Discussion",
        "TODO: interpret findings and compare with the original paper.",
        "",
        "## Limitations",
        "TODO: describe constraints and future work.",
        "",
        "## Conclusion",
        "TODO: summarize the contribution.",
        "",
    ]
    final_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True, help="Path to paper PDF or text file")
    parser.add_argument("--title", default=None, help="Optional paper title override")
    args = parser.parse_args()

    paper_path = Path(args.paper)
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

    write_final_draft(draft)

    print(f"Processed paper: {title}")
    print(f"Artifacts written to: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
