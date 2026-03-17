# MIT License © 2025 Motohiro Suzuki

from crypto.merkle import (
    build_merkle_levels,
    hash_leaf,
    inclusion_proof,
    merkle_root,
    verify_inclusion_proof,
)


def test_merkle_root_and_inclusion_proofs() -> None:
    records = [
        b'{"index":0,"path":"a.txt","sha256":"aaa","size_bytes":1}',
        b'{"index":1,"path":"b.txt","sha256":"bbb","size_bytes":2}',
        b'{"index":2,"path":"c.txt","sha256":"ccc","size_bytes":3}',
    ]
    leaves = [hash_leaf(r) for r in records]
    levels = build_merkle_levels(leaves)
    root_hex = merkle_root(levels).hex()

    for i, leaf in enumerate(leaves):
        proof = inclusion_proof(i, levels)
        assert verify_inclusion_proof(leaf.hex(), proof, root_hex)
