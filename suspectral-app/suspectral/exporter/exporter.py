from abc import ABC, abstractmethod

import numpy as np


class Exporter(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def export(self, spectra: np.ndarray, wavelengths: np.ndarray | None = None):
        ...
