"""normalize(): output shape, shoulder centring/scaling, missing hand stays zero."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ml"))
from normalize import C, FLAGS, KP, L_SH, LEFT_HAND, NUM_FEATURES, POSE, R_SH, RIGHT_HAND, normalize  # noqa: E402


def fake_clip(n):
    """n frames: shoulders at (1,1) and (3,1) -> midpoint (2,1), width 2. Right hand seen, left missing."""
    rng = np.random.default_rng(0)
    seq = np.zeros((n, NUM_FEATURES), np.float32)
    pose = rng.uniform(0.5, 3.5, (n, (POSE.stop - POSE.start) // C, C)).astype(np.float32)
    pose[:, L_SH, :2], pose[:, R_SH, :2] = (1, 1), (3, 1)
    seq[:, POSE] = pose.reshape(n, -1)
    seq[:, RIGHT_HAND] = rng.uniform(0.5, 3.5, (n, RIGHT_HAND.stop - RIGHT_HAND.start))
    seq[:, FLAGS.start + 1] = 1
    return seq


@pytest.mark.parametrize("n", [10, 32, 80])  # shorter, equal, longer than T
def test_normalize(n):
    out = normalize(fake_clip(n))
    assert out.shape == (KP["T"], NUM_FEATURES)

    pose = out[:, POSE].reshape(len(out), -1, C)
    mid = (pose[:, L_SH, :2] + pose[:, R_SH, :2]) / 2
    width = np.linalg.norm(pose[:, L_SH, :2] - pose[:, R_SH, :2], axis=1)
    assert np.allclose(mid, 0, atol=1e-5) and np.allclose(width, 1, atol=1e-5)

    assert not out[:, LEFT_HAND].any()          # missing hand stays exactly zero
    assert (out[:, FLAGS.start + 1] == 1).all()  # flags untouched


def test_bad_shape():
    with pytest.raises(ValueError):
        normalize(np.zeros((0, NUM_FEATURES)))
