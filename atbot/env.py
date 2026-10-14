import os


def is_production() -> bool:
    """Production persistence is enabled only when ATBOT_ENV=production (set on Coolify)."""
    return os.getenv("ATBOT_ENV", "").strip().lower() in {"production", "prod"}
