from abc import ABC, abstractmethod

class Writer(ABC):
    """Abstract base class for writing exported spectral data to a destination."""

    @abstractmethod
    def write(self, name: str, data: str | bytes) -> None:
        """Write formatted spectral data to a destination.

        Parameters
        ----------
        name : str
            A base name to identify the exported data (e.g., used in file naming).

        data : str or bytes
            The formatted spectral data to be written.
        """
        ...
