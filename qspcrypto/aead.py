# MIT License © 2025 Motohiro Suzuki

import os
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .errors import FailClosed


@dataclass
class AEADBox:
    key: bytes

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
        if len(self.key) != 32:
            raise FailClosed("AEAD fail-closed: AES-GCM key must be 32 bytes")

        nonce = os.urandom(12)
        ciphertext = AESGCM(self.key).encrypt(nonce, plaintext, aad)
        return nonce, ciphertext

    def decrypt(self, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
        if len(self.key) != 32:
            raise FailClosed("AEAD fail-closed: AES-GCM key must be 32 bytes")

        if not nonce or len(nonce) != 12:
            raise FailClosed("AEAD fail-closed: nonce must be 12 bytes")

        return AESGCM(self.key).decrypt(nonce, ciphertext, aad)
