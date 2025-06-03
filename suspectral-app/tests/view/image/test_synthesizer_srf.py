import hashlib
from io import BytesIO
from typing import cast

import numpy as np
import pytest
import pytestqt
from PySide6.QtCore import QResource

from suspectral.model.hypercube import Hypercube
from suspectral.view.image.coloring_mode_srf import SynthesizerSRF

import resources
assert resources


def md5(arr: np.ndarray) -> str:
    return hashlib.md5(np.ascontiguousarray(arr).tobytes()).hexdigest()


@pytest.fixture(scope="session")
def hypercube():
    return Hypercube(f'{__file__}/../../../flower.hdr')


@pytest.fixture(scope="session")
def srf_imx():
    resource = QResource("/data/sensitivities/SRF_SonyIMX219.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


@pytest.fixture(scope="session")
def srf_ace():
    resource = QResource("/data/sensitivities/SRF_BaslerAce2.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


@pytest.fixture(scope="session")
def illum_a():
    resource = QResource("/data/illuminants/CIE_std_illum_A.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


@pytest.fixture(scope="session")
def illum_d65():
    resource = QResource("/data/illuminants/CIE_std_illum_D65.csv")
    with BytesIO(cast(bytes, resource.data())) as file:
        return np.genfromtxt(file, delimiter=",", names=True)


def test_srf_imx(qtbot, hypercube, srf_imx):
    victim = SynthesizerSRF(srf=srf_imx, hypercube=hypercube)

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "a4f04dbe9aae7edad6329a734899a170"


def test_srf_ace(qtbot, hypercube, srf_ace):
    victim = SynthesizerSRF(srf=srf_ace, hypercube=hypercube)

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "a5feac661e03799d8d842b10fab63031"


def test_srf_imx_contrast(qtbot, hypercube, srf_imx):
    victim = SynthesizerSRF(
        srf=srf_imx,
        hypercube=hypercube,
        apply_per_channel_contrast=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "cbe2b3c8e4da867b8c2a043921aec557"


def test_srf_imx_d65(qtbot, hypercube, srf_imx, illum_d65):
    victim = SynthesizerSRF(
        srf=srf_imx,
        spd=illum_d65,
        hypercube=hypercube,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "6a16779461f8caff8639fc4fcb3fec2c"


def test_srf_imx_a(qtbot, hypercube, srf_imx, illum_a):
    victim = SynthesizerSRF(
        srf=srf_imx,
        spd=illum_a,
        hypercube=hypercube,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "5e6fa9f3fd395e9c183650745e3461bd"


def test_srf_imx_white_black(qtbot, hypercube, srf_imx, illum_a):
    white_ref = hypercube.read_pixel(57, 244)
    black_ref = hypercube.read_pixel(212, 89)

    victim = SynthesizerSRF(
        srf=srf_imx,
        white_ref=white_ref,
        black_ref=black_ref,
        hypercube=hypercube,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "b4ece58ee87823a2b16333c807fc6b76"


def test_srf_imx_white(qtbot, hypercube, srf_imx, illum_a):
    white_ref = hypercube.read_pixel(57, 244)

    victim = SynthesizerSRF(
        srf=srf_imx,
        white_ref=white_ref,
        hypercube=hypercube,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "6c352d0da9b49d812496ae9b63b048f6"


def test_srf_imx_white_contrast(qtbot, hypercube, srf_imx, illum_a):
    white_ref = hypercube.read_pixel(57, 244)

    victim = SynthesizerSRF(
        srf=srf_imx,
        white_ref=white_ref,
        hypercube=hypercube,
        apply_per_channel_contrast=True,
    )

    with qtbot.waitSignal(victim.produced, timeout=500) as blocker:
        victim.run()

    image = blocker.args[0]
    assert md5(image) == "817035d377601007b2638ae46217aae8"


def test_srf_stopped(qtbot, hypercube, srf_imx):
    victim = SynthesizerSRF(srf=srf_imx, hypercube=hypercube)
    victim.stop()

    with pytest.raises(pytestqt.exceptions.TimeoutError):
        with qtbot.waitSignal(victim.produced, timeout=500):
            victim.run()
