"""Tests for identifier validation."""

import unittest

from mcporacle.errors import InputValidationError
from mcporacle.validation import normalize_oracle_identifier


class NormalizeOracleIdentifierTests(unittest.TestCase):
    def test_normalizes_valid_identifier(self) -> None:
        self.assertEqual(
            normalize_oracle_identifier(" hr_employees ", "table_name"),
            "HR_EMPLOYEES",
        )

    def test_rejects_empty_identifier(self) -> None:
        with self.assertRaises(InputValidationError):
            normalize_oracle_identifier("   ", "schema_name")

    def test_rejects_non_identifier_characters(self) -> None:
        with self.assertRaises(InputValidationError):
            normalize_oracle_identifier("users;drop table x", "table_name")


if __name__ == "__main__":
    unittest.main()
