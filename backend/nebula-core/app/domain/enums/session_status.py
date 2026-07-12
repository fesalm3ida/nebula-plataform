from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    EXPIRED = "expired"
