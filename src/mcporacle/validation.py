"""Validation helpers for constrained Oracle identifiers."""

import re

from mcporacle.errors import InputValidationError


_IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_$#]{0,127}$")


def normalize_oracle_identifier(value: str, field_name: str) -> str:
    """Normalize and validate a simple Oracle identifier."""

    if value is None:
        raise InputValidationError("{field} is required.".format(field=field_name))

    normalized = value.strip().upper()
    if not normalized:
        raise InputValidationError("{field} cannot be empty.".format(field=field_name))
    if not _IDENTIFIER_RE.match(normalized):
        raise InputValidationError(
            "{field} must be a simple Oracle identifier containing only letters, "
            "numbers, _, $, # and must start with a letter.".format(field=field_name)
        )
    return normalized
