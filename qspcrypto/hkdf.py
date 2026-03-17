# MIT License © 2025 Motohiro Suzuki

import hashlib
import hmac


def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    if length <= 0:
        raise ValueError("length must be positive")
    if length > 32 * 255:
        raise ValueError("length too large for HKDF-SHA256")

    okm = b""
    t = b""
    counter = 1

    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1

    return okm[:length]


def hkdf_sha256(ikm: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    prk = hkdf_extract(salt=salt, ikm=ikm)
    return hkdf_expand(prk=prk, info=info, length=length)
