from markupsafe import escape


def sanitize_text(value: str | None) -> str:
    if not value:
        return ""
    return str(escape(value.strip()))
