from pathlib import Path
import re

GEN_DIR = Path('research/generated_code')
LOG = Path('research/artifacts/code_generation.log')


def ensure_minimal_impl():
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    # model
    (GEN_DIR / 'model.py').write_text(
        'import numpy as np\n\n'
        'class PaperModel:\n'
        '    def __init__(self, input_dim: int, config=None):\n'
        '        self.config = config or {}\n'
        '        self.input_dim = input_dim\n'
        '        rng = np.random.RandomState(self.config.get("seed", 0))\n'
        '        self.w = rng.normal(scale=0.01, size=(input_dim,))\n'
        '        self.b = 0.0\n\n'
        '    def predict_proba(self, X):\n'
        '        logits = X.dot(self.w) + self.b\n'
        '        return 1.0 / (1.0 + np.exp(-logits))\n\n'
        '    def predict(self, X):\n'
        '        return (self.predict_proba(X) >= 0.5).astype(int)\n',
        encoding='utf-8'
    )
    # train
    (GEN_DIR / 'train.py').write_text(
        'import numpy as np\nimport json\nfrom pathlib import Path\n\n'
        'def train(model, X_train, y_train, config):\n'
        '    lr = float(config.get("lr", 0.1))\n'
        '    epochs = int(config.get("epochs", 10))\n'
        '    for ep in range(epochs):\n'
        '        preds = model.predict_proba(X_train)\n'
        '        error = preds - y_train\n'
        '        grad_w = X_train.T.dot(error) / X_train.shape[0]\n'
        '        grad_b = error.mean()\n'
        '        model.w -= lr * grad_w\n'
        '        model.b -= lr * grad_b\n'
        '    out = Path(config.get("out_dir", "research/artifacts"))\n'
        '    out.mkdir(parents=True, exist_ok=True)\n'
        '    with (out / "train_history.json").open("w", encoding="utf-8") as fh:\n'
        '        json.dump({"status":"ok"}, fh)\n'
        '    return model, {}\n',
        encoding='utf-8'
    )
    # eval
    (GEN_DIR / 'eval.py').write_text(
        'import json\nfrom pathlib import Path\n\n'
        'def evaluate(model, X, y, config):\n'
        '    probs = model.predict_proba(X)\n'
        '    preds = (probs >= 0.5).astype(int)\n'
        '    acc = float((preds == y).mean())\n'
        '    out = Path(config.get("out_dir", "research/artifacts"))\n'
        '    out.mkdir(parents=True, exist_ok=True)\n'
        '    with (out / "metrics.json").open("w", encoding="utf-8") as fh:\n'
        '        json.dump({"accuracy": acc}, fh)\n'
        '    return {"accuracy": acc}\n',
        encoding='utf-8'
    )


def main():
    ensure_minimal_impl()
    LOG.write_text('code_generator: scaffold ensured', encoding='utf-8')
    print('code_generator: scaffold implemented')


if __name__ == '__main__':
    main()
