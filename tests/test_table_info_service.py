"""Tests for the table info service."""

import unittest

from mcporacle.models import TableColumnInfo, TableInfo
from mcporacle.services.table_info import TableInfoService


class _FakeRepository:
    def __init__(self) -> None:
        self.calls = []

    def fetch_table_info(self, schema_name: str, table_name: str) -> TableInfo:
        self.calls.append((schema_name, table_name))
        return TableInfo(
            owner=schema_name,
            table_name=table_name,
            table_comment="Employee master data",
            columns=[
                TableColumnInfo(
                    name="EMPLOYEE_ID",
                    data_type="NUMBER",
                    nullable=False,
                    data_length=22,
                    data_precision=10,
                    data_scale=0,
                    column_id=1,
                    comment="Primary key",
                )
            ],
        )


class TableInfoServiceTests(unittest.TestCase):
    def test_service_normalizes_inputs_and_returns_json_like_payload(self) -> None:
        repository = _FakeRepository()
        service = TableInfoService(repository)

        result = service.get_table_info("hr", "employees")

        self.assertEqual(repository.calls, [("HR", "EMPLOYEES")])
        self.assertTrue(result["ok"])
        self.assertEqual(result["table"]["owner"], "HR")
        self.assertEqual(result["table"]["table_name"], "EMPLOYEES")
        self.assertEqual(result["table"]["columns"][0]["name"], "EMPLOYEE_ID")


if __name__ == "__main__":
    unittest.main()
