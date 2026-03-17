# MIT License © 2025 Motohiro Suzuki

import os
from dataclasses import dataclass

from .errors import FailClosed
from .hkdf import hkdf_sha256
from .aead import AEADBox


@dataclass
class SessionConfig:
    require_qkd: bool = True
    context_info: bytes = b"QSP-Stage207/crypto-min/v0.1"


def derive_aesgcm_key(
    pqc_shared_secret: bytes | None,
    qkd_key: bytes | None,
    cfg: SessionConfig,
) -> bytes:
    if not pqc_shared_secret:
        raise FailClosed("derive fail-closed: PQC shared secret missing")

    if cfg.require_qkd and not qkd_key:
        raise FailClosed("derive fail-closed: QKD key missing but required")

    ikm = pqc_shared_secret + (qkd_key or b"")
    salt = os.urandom(16)

    return hkdf_sha256(
        ikm=ikm,
        salt=salt,
        info=cfg.context_info,
        length=32,
    )


def make_aead_box(
    pqc_shared_secret: bytes | None,
    qkd_key: bytes | None,
    cfg: SessionConfig,
) -> AEADBox:
    key = derive_aesgcm_key(
        pqc_shared_secret=pqc_shared_secret,
        qkd_key=qkd_key,
        cfg=cfg,
    )
    return AEADBox(key=key)
