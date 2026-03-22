"""Response models for table metadata."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TableColumnInfo:
    """Column metadata returned by the Oracle metadata tool."""

    name: str
    data_type: str
    nullable: bool
    data_length: Optional[int]
    data_precision: Optional[int]
    data_scale: Optional[int]
    column_id: int
    comment: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data_type": self.data_type,
            "nullable": self.nullable,
            "data_length": self.data_length,
            "data_precision": self.data_precision,
            "data_scale": self.data_scale,
            "column_id": self.column_id,
            "comment": self.comment,
        }


@dataclass(frozen=True)
class TableInfo:
    """Structured table metadata returned to MCP clients."""

    owner: str
    table_name: str
    table_comment: Optional[str]
    columns: List[TableColumnInfo]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "table": {
                "owner": self.owner,
                "table_name": self.table_name,
                "comment": self.table_comment,
                "columns": [column.to_dict() for column in self.columns],
            },
        }
