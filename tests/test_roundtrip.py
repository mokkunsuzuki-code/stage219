# MIT License © 2025 Motohiro Suzuki

from qspcrypto import SessionConfig, make_aead_box


def test_aesgcm_roundtrip():
    cfg = SessionConfig(require_qkd=True)
    box = make_aead_box(
        pqc_shared_secret=b"p" * 32,
        qkd_key=b"q" * 32,
        cfg=cfg,
    )

    aad = b"header"
    plaintext = b"hello-stage207"

    nonce, ciphertext = box.encrypt(plaintext, aad=aad)
    recovered = box.decrypt(nonce, ciphertext, aad=aad)

    assert recovered == plaintext
