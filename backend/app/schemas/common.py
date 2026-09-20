def require_non_blank(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("cannot be blank")
    return stripped


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_optional_email(value: str | None) -> str | None:
    cleaned = blank_to_none(value)
    if cleaned is None:
        return None
    return normalize_email(cleaned)
