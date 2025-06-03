import hashlib
from io import BytesIO
from typing import cast

import numpy as np
import pytest
import pytestqt
from PySide6.QtCore import QResource

from suspectral.model.hypercube import Hypercube
from suspectral.view.image.coloring_mode_cie import SynthesizerCIE

import resources
assert resources


def md5(arr: np.ndarray) -> str:
    return hashlib.md5(np.ascontiguousarray(arr).tobytes()).hexdigest()


@pytest.fixture(scope="session")
def hypercube():
    return Hypercube(f'{__file__}/../../../flower.hdr')


@pytest.fixture(scope="session")
def cmf():
    resource = QResource("/data/sensitivities/CIE_XYZ_1931.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


@pytest.fixture(scope="session")
def d65():
    resource = QResource("/data/illuminants/CIE_std_illum_D65.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


def test_cie_default(qtbot, hypercube, cmf):
    victim = SynthesizerCIE(cmf=cmf, hypercube=hypercube)

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "b9a5aeb8cce687e71fb89215c80bcf22"


def test_cie_srgb(qtbot, hypercube, cmf):
    victim = SynthesizerCIE(
        cmf=cmf,
        hypercube=hypercube,
        apply_srgb_transform=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "b792551383a50a961efa2c653f08ee8b"


def test_cie_srgb_contrast(qtbot, hypercube, cmf):
    victim = SynthesizerCIE(
        cmf=cmf,
        hypercube=hypercube,
        apply_srgb_transform=True,
        apply_per_channel_contrast=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "da3e14815baab4558845aca9b974816d"


def test_cie_srgb_gamma_contrast(qtbot, hypercube, cmf):
    victim = SynthesizerCIE(
        cmf=cmf,
        hypercube=hypercube,
        apply_srgb_transform=True,
        apply_gamma_encoding=True,
        apply_per_channel_contrast=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "e09674f6277e669e2ec2cc7b94b57ba7"


def test_cie_srgb_d65(qtbot, hypercube, cmf, d65):
    victim = SynthesizerCIE(
        cmf=cmf,
        spd=d65,
        hypercube=hypercube,
        apply_srgb_transform=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "21794c38b835e1523c6382fa7b9c201a"


def test_cie_srgb_white_d65(qtbot, hypercube, cmf, d65):
    white_ref = hypercube.read_pixel(57, 244)

    victim = SynthesizerCIE(
        cmf=cmf,
        spd=d65,
        hypercube=hypercube,
        white_ref=white_ref,
        apply_srgb_transform=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "2ce54bb1b2ca3c71cb0ed5877ed31653"


def test_cie_srgb_white_black_d65(qtbot, hypercube, cmf, d65):
    white_ref = hypercube.read_pixel(57, 244)
    black_ref = hypercube.read_pixel(212, 89)

    victim = SynthesizerCIE(
        cmf=cmf,
        spd=d65,
        hypercube=hypercube,
        white_ref=white_ref,
        black_ref=black_ref,
        apply_srgb_transform=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "b34a80dd27acd0f74e1d3e11ed1cc7c9"


def test_cie_stopped(qtbot, hypercube, cmf):
    victim = SynthesizerCIE(cmf=cmf, hypercube=hypercube)
    victim.stop()

    with pytest.raises(pytestqt.exceptions.TimeoutError):
        with qtbot.waitSignal(victim.produced, timeout=500):
            victim.run()
