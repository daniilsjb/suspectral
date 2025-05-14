from abc import ABC, abstractmethod

import numpy as np


class Exporter(ABC):
    def __init__(self, label: str):
        self.label = label

    @abstractmethod
    def export(self,
               name: str,
               spectra: np.ndarray,
               wavelengths: np.ndarray | None = None):
        ...
