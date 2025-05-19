from PySide6.QtCore import QObject, Signal

from suspectral.view.image.coloring_mode_imx import ColoringModeIMX


class DummyHypercube:
    def __init__(self, num_bands=5, wavelengths=None, default_bands=None, wavelengths_unit="nm"):
        self.num_bands = num_bands
        self.wavelengths = wavelengths
        self.default_bands = default_bands or [0]
        self.wavelengths_unit = wavelengths_unit


class DummyHypercubeContainer(QObject):
    opened = Signal(object)

    def __init__(self):
        super().__init__()
        self.hypercube = None

    def emit_opened(self, hypercube):
        self.hypercube = hypercube
        self.opened.emit(hypercube)


class DummySynthesizerIMX(QObject):
    progress = Signal(int)
    finished = Signal()
    produced = Signal(str)

    def __init__(self, hypercube):
        super().__init__()
        self.hypercube = hypercube
        self.stopped = False

    def run(self):
        pass

    def stop(self):
        self.stopped = True


def test_handle_hypercube_opened_emits_status_changed(qtbot):
    model = DummyHypercubeContainer()
    widget = ColoringModeIMX(model)
    qtbot.addWidget(widget)

    hypercube_with_wavelengths = DummyHypercube(wavelengths=[500, 600, 700])
    with qtbot.waitSignal(widget.statusChanged, timeout=1000) as blocker:
        widget._handle_hypercube_opened(hypercube_with_wavelengths)
    assert blocker.args == [True]

    hypercube_without_wavelengths = DummyHypercube(wavelengths=None)
    with qtbot.waitSignal(widget.statusChanged, timeout=1000) as blocker:
        widget._handle_hypercube_opened(hypercube_without_wavelengths)
    assert blocker.args == [False]


def test_handle_cancel_stops_worker(qtbot, monkeypatch):
    model = DummyHypercubeContainer()
    widget = ColoringModeIMX(model)
    qtbot.addWidget(widget)

    mock_worker = DummySynthesizerIMX(model.hypercube)
    widget._worker = mock_worker

    widget._handle_cancel()
    assert mock_worker.stopped
