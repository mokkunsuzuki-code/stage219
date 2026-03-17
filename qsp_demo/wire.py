# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class MsgType(IntEnum):
    CLIENT_HELLO = 1
    SERVER_HELLO = 2
    FINISH = 3
    ALERT = 255


@dataclass(frozen=True)
class Frame:
    version: int
    mtype: MsgType
    session_id: bytes  # 16 bytes
    payload: bytes

    def encode(self) -> bytes:
        # version(1) | type(1) | session_id(16) | payload_len(2) | payload(n)
        if not (0 <= self.version <= 255):
            raise ValueError("version out of range")
        if len(self.session_id) != 16:
            raise ValueError("session_id must be 16 bytes")
        if len(self.payload) > 65535:
            raise ValueError("payload too large")

        header = (
            bytes([self.version, int(self.mtype)])
            + self.session_id
            + len(self.payload).to_bytes(2, "big")
        )
        return header + self.payload


def decode_frame(data: bytes) -> Frame:
    if len(data) < 1 + 1 + 16 + 2:
        raise ValueError("truncated frame")

    version = data[0]
    mtype_raw = data[1]
    try:
        mtype = MsgType(mtype_raw)
    except ValueError as e:
        raise ValueError("unknown msg type") from e

    session_id = data[2:18]
    payload_len = int.from_bytes(data[18:20], "big")
    payload = data[20:]

    if len(payload) != payload_len:
        raise ValueError("payload length mismatch")

    return Frame(version=version, mtype=mtype, session_id=session_id, payload=payload)
