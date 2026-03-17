# MIT License © 2025 Motohiro Suzuki

import pytest

from qspcrypto import FailClosed, SessionConfig, make_aead_box


def test_fail_closed_missing_pqc_secret():
    cfg = SessionConfig(require_qkd=True)
    with pytest.raises(FailClosed):
        make_aead_box(
            pqc_shared_secret=None,
            qkd_key=b"x" * 32,
            cfg=cfg,
        )


def test_fail_closed_missing_qkd_when_required():
    cfg = SessionConfig(require_qkd=True)
    with pytest.raises(FailClosed):
        make_aead_box(
            pqc_shared_secret=b"x" * 32,
            qkd_key=None,
            cfg=cfg,
        )


def test_allow_no_qkd_when_not_required():
    cfg = SessionConfig(require_qkd=False)
    box = make_aead_box(
        pqc_shared_secret=b"x" * 32,
        qkd_key=None,
        cfg=cfg,
    )
    assert len(box.key) == 32
