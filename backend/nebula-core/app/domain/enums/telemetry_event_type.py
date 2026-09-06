from enum import Enum


class TelemetryEventType(str, Enum):
    PLAYBACK_STARTED = "playback_started"
    PLAYBACK_ENDED = "playback_ended"
    BUFFER_UNDERRUN = "buffer_underrun"
    CHANNEL_CHANGED = "channel_changed"
    QOS_REPORT = "qos_report"
    PLAYBACK_ERROR = "playback_error"
