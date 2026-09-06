from enum import Enum


class PlaylistAssignmentStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
