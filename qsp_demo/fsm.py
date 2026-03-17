# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from enum import Enum, auto


class State(Enum):
    INIT = auto()
    WAIT_SERVER_HELLO = auto()
    WAIT_FINISH = auto()
    ESTABLISHED = auto()
    CLOSED = auto()


class Event(Enum):
    SEND_CLIENT_HELLO = auto()
    RECV_SERVER_HELLO = auto()
    RECV_FINISH = auto()
    FAIL = auto()


_ALLOWED = {
    (State.INIT, Event.SEND_CLIENT_HELLO): State.WAIT_SERVER_HELLO,
    (State.WAIT_SERVER_HELLO, Event.RECV_SERVER_HELLO): State.WAIT_FINISH,
    (State.WAIT_FINISH, Event.RECV_FINISH): State.ESTABLISHED,
}


def transition(state: State, event: Event) -> State:
    if state == State.CLOSED:
        return State.CLOSED
    if event == Event.FAIL:
        return State.CLOSED

    nxt = _ALLOWED.get((state, event))
    return nxt if nxt is not None else State.CLOSED
