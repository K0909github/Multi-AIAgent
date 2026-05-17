import numpy as np

class PaperModel:
    """Simple linear model implemented with numpy for synthetic experiments.

    Weight vector `w` and bias `b` are stored as numpy arrays.
    """
    def __init__(self, input_dim: int, config=None):
        self.config = config or {}
        self.input_dim = input_dim
        rng = np.random.RandomState(self.config.get('seed', 0))
        self.w = rng.normal(scale=0.01, size=(input_dim,))
        self.b = 0.0

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        logits = X.dot(self.w) + self.b
        return 1.0 / (1.0 + np.exp(-logits))

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) >= 0.5).astype(int)

    def parameters(self):
        return [self.w, np.array([self.b])]
