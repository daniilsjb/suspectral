import hashlib

import numpy as np
import pytest

from suspectral.model.hypercube import Hypercube
from suspectral.view.image.coloring_mode_cie import SynthesizerCIE

import resources
assert resources


def md5(arr: np.ndarray) -> str:
    return hashlib.md5(arr.tobytes()).hexdigest()


@pytest.fixture(scope="session")
def hypercube():
    return Hypercube(f'{__file__}/../../../flower.hdr')


def test_cie_no_transform(qtbot, hypercube):
    synth = SynthesizerCIE(hypercube, apply_srgb=False, apply_gamma=False)

    result = []
    synth.produced.connect(lambda img: result.append(img))

    qtbot.waitSignal(synth.produced, timeout=10000)
    synth.run()

    assert result, "No image produced"
    assert md5(result[0]) == "1020813d534f18639578a4b4dd142a3e"


def test_cie_srgb_only(qtbot, hypercube):
    synth = SynthesizerCIE(hypercube, apply_srgb=True, apply_gamma=False)

    result = []
    synth.produced.connect(lambda img: result.append(img))

    qtbot.waitSignal(synth.produced, timeout=10000)
    synth.run()

    assert result, "No image produced"
    assert md5(result[0]) == "e060036be82dd4c7898130a64b01557a"
