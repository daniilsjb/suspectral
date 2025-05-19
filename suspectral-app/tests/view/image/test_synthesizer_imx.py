import hashlib

import numpy as np
import pytest
from pytestqt.qtbot import QtBot

from suspectral.model.hypercube import Hypercube
from suspectral.view.image.coloring_mode_imx import SynthesizerIMX

import resources
assert resources


def md5(arr: np.ndarray) -> str:
    return hashlib.md5(arr.tobytes()).hexdigest()


@pytest.fixture(scope="session")
def hypercube():
    return Hypercube(f'{__file__}/../../../flower.hdr')


def test_synthesizer_imx_output(qtbot: QtBot, hypercube: Hypercube):
    synth = SynthesizerIMX(hypercube)

    result_image = []

    def on_produced(image: np.ndarray):
        result_image.append(image)

    qtbot.waitSignal(synth.produced, timeout=10000, raising=True, check_params_cb=lambda img: True)
    synth.produced.connect(on_produced)
    synth.run()

    assert result_image, "No image was produced."

    md5_hash = md5(result_image[0])
    expected_md5 = "cbe2b3c8e4da867b8c2a043921aec557"

    assert md5_hash == expected_md5, f"MD5 mismatch: got {md5_hash}, expected {expected_md5}"
