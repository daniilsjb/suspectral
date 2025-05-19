import numpy as np


class RegressionLS:
    def __init__(self, n_features, n_channels):
        self._n_features = n_features
        self._n_channels = n_channels

        self._XX = np.zeros((self._n_features, self._n_features))
        self._XY = np.zeros((self._n_features, self._n_channels))

        self._M = np.zeros((self._n_features, self._n_channels))
        self.alpha_ = 0.0

    def update(self, X, y):
        self._XX += X.T @ X
        self._XY += X.T @ y

    def build(self, *, alpha=0.0):
        self._M = np.linalg.inv(self._XX + alpha * np.eye(self._n_features)) @ self._XY
        self.alpha_ = alpha

    def predict(self, X):
        return X @ self._M


class RegressionRELS:
    def __init__(self, n_features, n_channels):
        self.n_features_ = n_features
        self.n_channels_ = n_channels

        self._XX = [np.zeros((n_features, n_features)) for _ in range(n_channels)]
        self._XY = np.zeros((n_features, n_channels))

        self._M = np.zeros((n_features, n_channels))
        self.alphas_ = np.zeros(n_channels)

    def build_channel(self, *, channel: int, alpha: float):
        self._M[:, channel] = np.linalg.inv(self._XX[channel] + alpha * np.eye(self.n_features_)) @ self._XY[:, channel]
        self.alphas_[channel] = alpha

    def update(self, X, y):
        n = X.shape[0]

        for channel in range(self.n_channels_):
            H = 1.0 / y[:, channel].reshape(n, 1) * X

            self._XX[channel] += H.T @ H
            self._XY[:, channel] += H.T @ np.ones(n)

    def transform(self, X):
        return X @ self._M

    def transform_channel(self, X, *, channel: int):
        return X @ self._M[:, channel].reshape(-1, 1)
