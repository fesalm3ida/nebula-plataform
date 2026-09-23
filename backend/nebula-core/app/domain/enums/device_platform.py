from enum import Enum


class DevicePlatform(str, Enum):
    """Plataformas suportadas pelo Nebula Player."""

    ANDROID = "android"
    ANDROID_TV = "android_tv"
    # App da LG Smart TV (webOS) — frontend/nebula-tv
    WEBOS_TV = "webos_tv"
    # App iOS (frontend/nebula-player, plataforma ios/)
    IOS = "ios"
