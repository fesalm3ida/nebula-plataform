from enum import Enum


class PlaylistFormat(str, Enum):
    M3U = "m3u"
    XTREAM_CODES = "xtream_codes"
    STALKER = "stalker"
