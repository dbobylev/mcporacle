"""Oracle metadata repository backed by anonymous PL/SQL."""

from typing import Any, Optional

from mcporacle.config import Settings
from mcporacle.errors import (
    OracleAccessError,
    OracleConnectionError,
    OracleDependencyError,
    TableNotFoundError,
)
from mcporacle.models import TableColumnInfo, TableInfo


PLSQL_TABLE_INFO_BLOCK = """
DECLARE
    v_owner      VARCHAR2(128) := UPPER(TRIM(:owner));
    v_table_name VARCHAR2(128) := UPPER(TRIM(:table_name));
BEGIN
    OPEN :table_cursor FOR
        SELECT t.owner,
               t.table_name,
               c.comments AS table_comment
          FROM dba_tables t
          LEFT JOIN dba_tab_comments c
            ON c.owner = t.owner
           AND c.table_name = t.table_name
         WHERE t.owner = v_owner
           AND t.table_name = v_table_name;

    OPEN :column_cursor FOR
        SELECT col.column_id,
               col.column_name,
               col.data_type,
               col.data_length,
               col.data_precision,
               col.data_scale,
               col.nullable,
               comm.comments AS column_comment
          FROM dba_tab_columns col
          LEFT JOIN dba_col_comments comm
            ON comm.owner = col.owner
           AND comm.table_name = col.table_name
           AND comm.column_name = col.column_name
         WHERE col.owner = v_owner
           AND col.table_name = v_table_name
         ORDER BY col.column_id;
END;
""".strip()


class OracleMetadataRepository:
    """Reads metadata from Oracle DBA views via a constrained PL/SQL block."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def fetch_table_info(self, schema_name: str, table_name: str) -> TableInfo:
        oracledb = _import_oracledb()
        connection = None

        try:
            connection = oracledb.connect(
                user=self._settings.oracle_user,
                password=self._settings.oracle_password,
                dsn=self._settings.oracle_dsn,
            )
        except oracledb.DatabaseError as exc:
            raise _map_database_error(exc) from exc

        table_cursor = None
        column_cursor = None
        try:
            with connection.cursor() as cursor:
                table_cursor_var = cursor.var(oracledb.CURSOR)
                column_cursor_var = cursor.var(oracledb.CURSOR)
                cursor.execute(
                    PLSQL_TABLE_INFO_BLOCK,
                    owner=schema_name,
                    table_name=table_name,
                    table_cursor=table_cursor_var,
                    column_cursor=column_cursor_var,
                )
                table_cursor = table_cursor_var.getvalue()
                column_cursor = column_cursor_var.getvalue()

                table_row = table_cursor.fetchone()
                if not table_row:
                    raise TableNotFoundError(
                        "Table {schema}.{table} was not found.".format(
                            schema=schema_name,
                            table=table_name,
                        )
                    )

                column_rows = column_cursor.fetchall()

            columns = [
                TableColumnInfo(
                    name=row[1],
                    data_type=row[2],
                    data_length=row[3],
                    data_precision=row[4],
                    data_scale=row[5],
                    nullable=row[6] == "Y",
                    column_id=row[0],
                    comment=row[7],
                )
                for row in column_rows
            ]
            return TableInfo(
                owner=table_row[0],
                table_name=table_row[1],
                table_comment=table_row[2],
                columns=columns,
            )
        except TableNotFoundError:
            raise
        except oracledb.DatabaseError as exc:
            raise _map_database_error(exc) from exc
        finally:
            _close_quietly(table_cursor)
            _close_quietly(column_cursor)
            _close_quietly(connection)


def _import_oracledb() -> Any:
    try:
        import oracledb  # type: ignore
    except ImportError as exc:
        raise OracleDependencyError(
            "The 'oracledb' package is not installed. Run 'pip install -e .' first."
        ) from exc
    return oracledb


def _close_quietly(resource: Optional[Any]) -> None:
    if resource is None:
        return
    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def _map_database_error(exc: Exception) -> Exception:
    error = exc.args[0] if getattr(exc, "args", None) else exc
    code = getattr(error, "code", None)
    message = str(error)

    if code in (1017, 12154, 12514, 12541):
        return OracleConnectionError(
            "Oracle connection failed. Check credentials, DSN and listener status."
        )
    if code in (942, 1031):
        return OracleAccessError(
            "Oracle user cannot read required DBA views. Grant access to "
            "DBA_TABLES, DBA_TAB_COMMENTS, DBA_TAB_COLUMNS and DBA_COL_COMMENTS."
        )
    return OracleAccessError(
        "Oracle metadata query failed: {message}".format(message=message)
    )
