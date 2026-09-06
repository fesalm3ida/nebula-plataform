from enum import Enum


class PlaylistStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
