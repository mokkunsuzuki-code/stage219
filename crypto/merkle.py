# MIT License © 2025 Motohiro Suzuki

from __future__ import annotations

import hashlib
from typing import Dict, List


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_leaf(record_bytes: bytes) -> bytes:
    # Domain separation for leaves
    return sha256_bytes(b"\x00" + record_bytes)


def hash_node(left: bytes, right: bytes) -> bytes:
    # Domain separation for internal nodes
    return sha256_bytes(b"\x01" + left + right)


def build_merkle_levels(leaf_hashes: List[bytes]) -> List[List[bytes]]:
    if not leaf_hashes:
        raise ValueError("leaf_hashes must not be empty")

    levels: List[List[bytes]] = [leaf_hashes[:]]
    current = leaf_hashes[:]

    while len(current) > 1:
        nxt: List[bytes] = []
        i = 0
        while i < len(current):
            left = current[i]
            if i + 1 < len(current):
                right = current[i + 1]
            else:
                # duplicate last node when odd
                right = current[i]
            nxt.append(hash_node(left, right))
            i += 2
        levels.append(nxt)
        current = nxt

    return levels


def merkle_root(levels: List[List[bytes]]) -> bytes:
    if not levels or not levels[-1]:
        raise ValueError("invalid merkle levels")
    return levels[-1][0]


def inclusion_proof(index: int, levels: List[List[bytes]]) -> List[Dict[str, str]]:
    if index < 0 or index >= len(levels[0]):
        raise IndexError("leaf index out of range")

    proof: List[Dict[str, str]] = []
    current_index = index

    for level in levels[:-1]:
        if current_index % 2 == 0:
            sibling_index = current_index + 1
            if sibling_index >= len(level):
                sibling_index = current_index
            sibling_position = "right"
        else:
            sibling_index = current_index - 1
            sibling_position = "left"

        proof.append(
            {
                "position": sibling_position,
                "hash": level[sibling_index].hex(),
            }
        )
        current_index //= 2

    return proof


def verify_inclusion_proof(
    leaf_hash_hex: str,
    proof: List[Dict[str, str]],
    expected_root_hex: str,
) -> bool:
    current = bytes.fromhex(leaf_hash_hex)

    for step in proof:
        sibling = bytes.fromhex(step["hash"])
        position = step["position"]

        if position == "left":
            current = hash_node(sibling, current)
        elif position == "right":
            current = hash_node(current, sibling)
        else:
            raise ValueError(f"invalid proof position: {position}")

    return current.hex() == expected_root_hex


def levels_as_hex(levels: List[List[bytes]]) -> List[List[str]]:
    return [[node.hex() for node in level] for level in levels]
