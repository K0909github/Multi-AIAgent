"""Run a minimal synthetic experiment using the generated scaffold.

This script creates synthetic binary classification data, trains the scaffold `PaperModel`,
and writes artifacts to `research/artifacts`.
"""
import numpy as np
import yaml
from pathlib import Path
from model import PaperModel
from train import train
from eval import evaluate

def try_log_mlflow_params(params: dict, mlflow_uri: str | None = None):
    try:
        import mlflow
        if mlflow_uri:
            mlflow.set_tracking_uri(mlflow_uri)
        with mlflow.start_run():
            for k, v in params.items():
                try:
                    mlflow.log_param(k, v)
                except Exception:
                    pass
    except Exception:
        pass


def make_synthetic(n_samples=200, n_features=16, seed=0):
    rng = np.random.RandomState(seed)
    X = rng.normal(size=(n_samples, n_features))
    # create a sparse random linear separator
    true_w = rng.normal(size=(n_features,))
    logits = X.dot(true_w)
    y = (logits + rng.normal(scale=0.5, size=logits.shape) > 0).astype(int)
    return X, y


def main():
    cfg_path = Path('config.yaml')
    cfg = {}
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text())
    exp = cfg.get('experiment', {})
    out_dir = Path(exp.get('out_dir', 'research/artifacts'))
    out_dir.mkdir(parents=True, exist_ok=True)

    X, y = make_synthetic(n_samples=400, n_features=32, seed=exp.get('seed', 0))
    # split
    split = int(0.8 * X.shape[0])
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]

    model = PaperModel(input_dim=X.shape[1], config=exp)
    # log params to MLflow inside Docker if possible
    try_log_mlflow_params({'n_features': X.shape[1], 'n_samples': X.shape[0], **exp}, mlflow_uri=exp.get('mlflow_uri'))

    model, history = train(model, X_tr, y_tr, {**exp, 'out_dir': str(out_dir)})
    metrics = evaluate(model, X_te, y_te, {'out_dir': str(out_dir), 'mlflow_uri': exp.get('mlflow_uri')})

    # Save model weights as artifact
    try:
        np.save(out_dir / 'model_w.npy', model.w)
        # log artifact to mlflow if available
        try:
            import mlflow
            if exp.get('mlflow_uri'):
                mlflow.set_tracking_uri(exp.get('mlflow_uri'))
            with mlflow.start_run():
                mlflow.log_artifact(str(out_dir / 'model_w.npy'))
        except Exception:
            pass
    except Exception:
        pass

    print('Experiment complete. Metrics:', metrics)


if __name__ == '__main__':
    main()
