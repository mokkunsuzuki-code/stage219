# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from qsp_demo.protocol import Endpoint, FailClosed
from qsp_demo.wire import Frame, MsgType


def main() -> None:
    print("=== HAPPY PATH ===")
    c = Endpoint("client")
    s = Endpoint("server")
    c.new_session()

    ch = c.client_hello()
    sh = s.server_recv(ch)
    c.client_recv(sh)

    fin = Frame(version=1, mtype=MsgType.FINISH, session_id=c.session_id, payload=b"fin").encode()
    fin_ack = s.server_recv(fin)
    c.client_recv(fin_ack)

    print("Client state:", c.state.name)
    print("Server state:", s.state.name)

    print("\n=== FAIL-CLOSED (wrong version) ===")
    bad = Frame(version=99, mtype=MsgType.CLIENT_HELLO, session_id=c.session_id, payload=b"x").encode()
    try:
        s2 = Endpoint("server")
        s2.server_recv(bad)
        print("ERROR: should have fail-closed")
    except FailClosed as e:
        print("Fail-Closed triggered:", e)


if __name__ == "__main__":
    main()
