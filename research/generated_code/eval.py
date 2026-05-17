import numpy as np
import json
from pathlib import Path

def evaluate(model, X, y, config):
    probs = model.predict_proba(X)
    preds = (probs >= 0.5).astype(int)
    acc = float((preds == y).mean())
    out = Path(config.get('out_dir', 'research/artifacts'))
    out.mkdir(parents=True, exist_ok=True)
    metrics = {'accuracy': acc}
    with (out / 'metrics.json').open('w', encoding='utf-8') as fh:
        json.dump(metrics, fh, indent=2)
    return metrics
