# MIT License © 2025 Motohiro Suzuki

class QSPCryptoError(Exception):
    """Base error for Stage207 crypto integration."""


class FailClosed(QSPCryptoError):
    """Raised when a required security precondition is not met (fail-closed)."""
