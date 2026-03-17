# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

import os
from dataclasses import dataclass

from .fsm import Event, State, transition
from .wire import Frame, MsgType, decode_frame


SPEC_VERSION = 1  # Stage206 fixed demo version


class FailClosed(Exception):
    """Raised when any spec violation occurs and the endpoint closes."""


@dataclass
class Endpoint:
    role: str  # "client" or "server"
    state: State = State.INIT
    session_id: bytes = b""

    def _fail(self, reason: str) -> None:
        self.state = transition(self.state, Event.FAIL)
        raise FailClosed(f"{self.role}: fail-closed: {reason}")

    def new_session(self) -> None:
        if self.role != "client":
            self._fail("only client can start a new session in this minimal demo")
        self.session_id = os.urandom(16)
        self.state = State.INIT

    # ---- client ----
    def client_hello(self) -> bytes:
        if self.role != "client":
            self._fail("role mismatch for client_hello")
        self.state = transition(self.state, Event.SEND_CLIENT_HELLO)
        return Frame(SPEC_VERSION, MsgType.CLIENT_HELLO, self.session_id, b"ch").encode()

    def client_recv(self, data: bytes) -> None:
        if self.role != "client":
            self._fail("role mismatch for client_recv")
        try:
            fr = decode_frame(data)
        except Exception as e:
            self._fail(f"wire decode error: {e}")

        if fr.version != SPEC_VERSION:
            self._fail("version mismatch")
        if fr.session_id != self.session_id:
            self._fail("session_id mismatch")

        if fr.mtype == MsgType.SERVER_HELLO:
            self.state = transition(self.state, Event.RECV_SERVER_HELLO)
            return

        if fr.mtype == MsgType.FINISH:
            self.state = transition(self.state, Event.RECV_FINISH)
            return

        self._fail(f"unexpected msg type: {fr.mtype.name}")

    # ---- server ----
    def server_recv(self, data: bytes) -> bytes:
        if self.role != "server":
            self._fail("role mismatch for server_recv")

        try:
            fr = decode_frame(data)
        except Exception as e:
            self._fail(f"wire decode error: {e}")

        if fr.version != SPEC_VERSION:
            self._fail("version mismatch")

        if self.state == State.INIT:
            if fr.mtype != MsgType.CLIENT_HELLO:
                self._fail("expected CLIENT_HELLO in INIT")
            self.session_id = fr.session_id
            self.state = State.WAIT_FINISH
            return Frame(SPEC_VERSION, MsgType.SERVER_HELLO, self.session_id, b"sh").encode()

        if fr.session_id != self.session_id:
            self._fail("session_id mismatch")

        if fr.mtype == MsgType.FINISH:
            self.state = State.ESTABLISHED
            return Frame(SPEC_VERSION, MsgType.FINISH, self.session_id, b"ok").encode()

        self._fail(f"unexpected msg type: {fr.mtype.name}")
