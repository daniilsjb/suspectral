import numpy as np


class OLS:
    """
    Based on the following publication:

    Lin, Y.-T. and Finlayson, G.D. (2021) “On the optimization of regression-
    based spectral reconstruction,” Sensors, 21(16), p. 5586.
    """

    def __init__(self, n_features: int, n_bands: int):
        self.n_features_ = n_features
        self.n_bands_ = n_bands

        self._XX = np.zeros((self.n_features_, self.n_features_))
        self._XY = np.zeros((self.n_features_, self.n_bands_))

        self._M = np.zeros((self.n_features_, self.n_bands_))
        self.alpha_ = 0.0

    def add(self, X: np.ndarray, y: np.ndarray):
        self._XX += X.T @ X
        self._XY += X.T @ y

    def fit(self, *, alpha: float = 0.0):
        self._M = np.linalg.inv(self._XX + alpha * np.eye(self.n_features_)) @ self._XY
        self.alpha_ = alpha

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self._M


class RELS:
    """
    Based on the following publication:

    Lin, Y.-T. and Finlayson, G.D. (2021) “On the optimization of regression-
    based spectral reconstruction,” Sensors, 21(16), p. 5586.
    """

    def __init__(self, n_features: int, n_bands: int, epsilon: float = 1e-3):
        self.n_features_ = n_features
        self.n_bands_ = n_bands
        self.epsilon_ = epsilon

        self._HH = np.zeros((n_bands, n_features, n_features))
        self._H1 = np.zeros((n_features, n_bands))

        self._M = np.zeros((n_features, n_bands))
        self.alphas_ = np.zeros(n_bands)

    def add(self, X: np.ndarray, y: np.ndarray):
        for band in range(self.n_bands_):
            H = 1.0 / (y[:, band].reshape(len(X), 1) + self.epsilon_) * X
            k = y[:, band] / (y[:, band] + self.epsilon_)

            self._HH[band, ...] += H.T @ H
            self._H1[..., band] += H.T @ k

        return self

    def fit(self, *, alphas: list[float]):
        self.alphas_ = np.array(alphas.copy())

        for band, alpha in enumerate(alphas):
            penalty = alpha * np.eye(self.n_features_)
            inverse = np.linalg.inv(self._HH[band] + penalty)
            self._M[:, band] = inverse @ self._H1[:, band]

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self._M
