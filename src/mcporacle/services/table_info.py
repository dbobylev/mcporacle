"""Business logic for the get_table_info MCP tool."""

from typing import Protocol

from mcporacle.models import TableInfo
from mcporacle.validation import normalize_oracle_identifier


class TableMetadataRepository(Protocol):
    """Small repository contract used by the table info service."""

    def fetch_table_info(self, schema_name: str, table_name: str) -> TableInfo:
        """Return table metadata for a normalized schema and table name."""


class TableInfoService:
    """Coordinates validation and Oracle metadata lookup."""

    def __init__(self, repository: TableMetadataRepository) -> None:
        self._repository = repository

    def get_table_info(self, schema_name: str, table_name: str) -> dict:
        normalized_schema = normalize_oracle_identifier(schema_name, "schema_name")
        normalized_table = normalize_oracle_identifier(table_name, "table_name")
        table_info = self._repository.fetch_table_info(
            normalized_schema,
            normalized_table,
        )
        return table_info.to_dict()
