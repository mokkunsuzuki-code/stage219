# MIT License © 2025 Motohiro Suzuki

import os
from dataclasses import dataclass
from .errors import FailClosed


@dataclass
class PQCShared:
    """
    PQC KEMのスタブ（仮実装）
    本物のPQCではなく統合テスト用
    """
    shared_secret: bytes
    encapsulated: bytes


def kem_encapsulate(peer_public_key: bytes | None) -> PQCShared:
    """
    相手公開鍵を使って共有秘密を作る（スタブ）
    """
    if not peer_public_key:
        raise FailClosed("PQC fail-closed: peer public key missing")

    shared = os.urandom(32)
    encapsulated = os.urandom(64)

    return PQCShared(shared, encapsulated)


def kem_decapsulate(private_key: bytes | None, encapsulated: bytes | None) -> bytes:
    """
    カプセルから共有秘密を復元（スタブ）
    """
    if not private_key:
        raise FailClosed("PQC fail-closed: private key missing")

    if not encapsulated:
        raise FailClosed("PQC fail-closed: encapsulated data missing")

    return os.urandom(32)
