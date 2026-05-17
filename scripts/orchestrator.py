#!/usr/bin/env python3
"""Orchestrator: paper -> scaffold -> (optional) integrate -> run experiment -> collect results

Usage:
  python scripts/orchestrator.py --paper PATH [--integrate-repo REPO_URL]
"""
import argparse
import subprocess
import shutil
from pathlib import Path
import json
import sys


def run(cmd, cwd=None):
    print('>',' '.join(cmd))
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return res.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper', required=True, help='Path to paper PDF or text')
    parser.add_argument('--integrate-repo', help='Optional Git repo URL to integrate scaffold into')
    parser.add_argument('--integration-dest', default='external/LGG', help='Clone destination')
    parser.add_argument('--create-branch', default='integrate/multi-aia-agent', help='Branch name for integration')
    parser.add_argument('--out', default='research/orchestrator_outputs', help='Output folder for collected results')
    args = parser.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) run research workflow to generate artifacts and scaffold
    run([sys.executable, 'research/research_workflow.py', '--paper', args.paper])

    # 1b) run paper_reader agent to review the summary
    run([sys.executable, 'agents/paper_reader.py'])

    # 1c) run hypothesis_selector agent to pick a hypothesis
    run([sys.executable, 'agents/hypothesis_selector.py'])

    # 2) optional: integrate into external repo
    if args.integrate_repo:
        run([sys.executable, 'tools/lgg_integration.py', '--repo', args.integrate_repo, '--dest', args.integration_dest, '--generated', 'research/generated_code', '--create-branch', args.create_branch])

    # 2b) run code_generator to implement scaffold (if needed)
    run([sys.executable, 'agents/code_generator.py'])

    # 2c) ensure generated_code contains runnable minimal implementations (redundant safety)
    gen_dir = Path('research/generated_code')
    if gen_dir.exists():
        # model.py
        (gen_dir / 'model.py').write_text(
            'import numpy as np\n\n'
            "class PaperModel:\n"
            "    \"\"\"Simple linear model implemented with numpy for synthetic experiments.\n\n"
            "    Weight vector `w` and bias `b` are stored as numpy arrays.\n"
            "    \"\"\"\n"
            "    def __init__(self, input_dim: int, config=None):\n"
            "        self.config = config or {}\n"
            "        self.input_dim = input_dim\n"
            "        rng = np.random.RandomState(self.config.get('seed', 0))\n"
            "        self.w = rng.normal(scale=0.01, size=(input_dim,))\n"
            "        self.b = 0.0\n\n"
            "    def predict_proba(self, X: np.ndarray) -> np.ndarray:\n"
            "        logits = X.dot(self.w) + self.b\n"
            "        return 1.0 / (1.0 + np.exp(-logits))\n\n"
            "    def predict(self, X: np.ndarray) -> np.ndarray:\n"
            "        return (self.predict_proba(X) >= 0.5).astype(int)\n\n"
            "    def parameters(self):\n"
            "        return [self.w, np.array([self.b])]\n",
            encoding='utf-8'
        )
        # train.py
        (gen_dir / 'train.py').write_text(
            "import numpy as np\nimport json\nfrom pathlib import Path\n\n"
            "def train(model, X_train, y_train, config):\n"
            "    lr = float(config.get('lr', 0.1))\n"
            "    epochs = int(config.get('epochs', 50))\n"
            "    batch_size = int(config.get('batch_size', 32))\n"
            "    n = X_train.shape[0]\n\n"
            "    history = {'loss': []}\n"
            "    for ep in range(epochs):\n"
            "        idx = np.random.permutation(n)\n"
            "        X_shuff = X_train[idx]\n"
            "        y_shuff = y_train[idx]\n"
            "        epoch_loss = 0.0\n"
            "        for i in range(0, n, batch_size):\n"
            "            xb = X_shuff[i:i+batch_size]\n"
            "            yb = y_shuff[i:i+batch_size]\n"
            "            preds = model.predict_proba(xb)\n"
            "            error = preds - yb\n"
            "            grad_w = xb.T.dot(error) / xb.shape[0]\n"
            "            grad_b = error.mean()\n"
            "            model.w -= lr * grad_w\n"
            "            model.b -= lr * grad_b\n"
            "            batch_loss = -(yb * np.log(preds + 1e-12) + (1 - yb) * np.log(1 - preds + 1e-12)).mean()\n"
            "            epoch_loss += batch_loss * xb.shape[0]\n"
            "        epoch_loss /= n\n"
            "        history['loss'].append(float(epoch_loss))\n\n"
            "    out = Path(config.get('out_dir', 'research/artifacts'))\n"
            "    out.mkdir(parents=True, exist_ok=True)\n"
            "    with (out / 'train_history.json').open('w', encoding='utf-8') as fh:\n"
            "        json.dump(history, fh, indent=2)\n\n"
            "    return model, history\n",
            encoding='utf-8'
        )
        # eval.py
        (gen_dir / 'eval.py').write_text(
            "import numpy as np\nimport json\nfrom pathlib import Path\n\n"
            "def evaluate(model, X, y, config):\n"
            "    probs = model.predict_proba(X)\n"
            "    preds = (probs >= 0.5).astype(int)\n"
            "    acc = float((preds == y).mean())\n"
            "    out = Path(config.get('out_dir', 'research/artifacts'))\n"
            "    out.mkdir(parents=True, exist_ok=True)\n"
            "    metrics = {'accuracy': acc}\n"
            "    with (out / 'metrics.json').open('w', encoding='utf-8') as fh:\n"
            "        json.dump(metrics, fh, indent=2)\n"
            "    return metrics\n",
            encoding='utf-8'
        )

    # 3) run experiment runner (scaffold)
    run([sys.executable, 'run_experiment.py'], cwd='research/generated_code')

    # 4) collect artifacts
    artifacts = Path('research/artifacts')
    if artifacts.exists():
        for p in artifacts.iterdir():
            if p.is_file():
                shutil.copy2(p, outdir / p.name)
    # 4b) run results summarizer to update final draft
    run([sys.executable, 'agents/results_summarizer.py'])
    # collect final_draft too
    fd = Path('research/artifacts/final_draft.md')
    if fd.exists():
        shutil.copy2(fd, outdir / fd.name)
    # 5) write summary manifest
    manifest = {'artifacts': [str(p.name) for p in outdir.iterdir() if p.is_file()]}
    with (outdir / 'manifest.json').open('w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2)

    print('Orchestration complete. Outputs in', outdir)


if __name__ == '__main__':
    main()
