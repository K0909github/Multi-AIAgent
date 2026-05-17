import numpy as np
import json
from pathlib import Path

def train(model, X_train, y_train, config):
    lr = float(config.get('lr', 0.1))
    epochs = int(config.get('epochs', 50))
    batch_size = int(config.get('batch_size', 32))
    n = X_train.shape[0]

    history = {'loss': []}
    for ep in range(epochs):
        idx = np.random.permutation(n)
        X_shuff = X_train[idx]
        y_shuff = y_train[idx]
        epoch_loss = 0.0
        for i in range(0, n, batch_size):
            xb = X_shuff[i:i+batch_size]
            yb = y_shuff[i:i+batch_size]
            preds = model.predict_proba(xb)
            error = preds - yb
            grad_w = xb.T.dot(error) / xb.shape[0]
            grad_b = error.mean()
            model.w -= lr * grad_w
            model.b -= lr * grad_b
            batch_loss = -(yb * np.log(preds + 1e-12) + (1 - yb) * np.log(1 - preds + 1e-12)).mean()
            epoch_loss += batch_loss * xb.shape[0]
        epoch_loss /= n
        history['loss'].append(float(epoch_loss))

    out = Path(config.get('out_dir', 'research/artifacts'))
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'train_history.json').open('w', encoding='utf-8') as fh:
        json.dump(history, fh, indent=2)

    return model, history
