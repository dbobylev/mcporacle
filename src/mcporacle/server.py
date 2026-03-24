"""MCP server entrypoint."""

import logging
from typing import Any

from mcporacle.config import Settings
from mcporacle.errors import McpOracleError
from mcporacle.oracle.client import OracleMetadataRepository
from mcporacle.services.dict_item import DictItemService
from mcporacle.services.table_info import TableInfoService


LOGGER = logging.getLogger(__name__)


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The 'mcp' package is not installed. Run 'pip install -e .' first."
        ) from exc

    settings = Settings.from_env()
    _configure_logging(settings.log_level)

    repository = OracleMetadataRepository(settings)
    service = TableInfoService(repository)
    dict_service = DictItemService(repository)
    server = FastMCP("mcporacle")

    @server.tool()
    def get_table_info(schema_name: str, table_name: str) -> dict:
        """Get Oracle database table metadata including columns, data types, nullability, and comments.

        Use this tool when the user asks about table structure, column definitions,
        data types, or schema information for a specific table in an Oracle database.
        Requires schema name (owner) and table name.
        """

        try:
            return service.get_table_info(schema_name, table_name)
        except McpOracleError as exc:
            LOGGER.warning("Tool request failed: %s", exc)
            return {
                "ok": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
            }
        except Exception:  # pragma: no cover - defensive guardrail
            LOGGER.exception("Unhandled server error")
            return {
                "ok": False,
                "error": {
                    "type": "InternalServerError",
                    "message": "Unexpected error while fetching table metadata.",
                },
            }

    @server.tool()
    def get_dict_item(isn: int) -> dict:
        """Get a dictionary entry from ais.dicti by ISN (individual serial number).

        Returns isn, parentisn, shortname, fullname, and constname for the record.
        Use when the user wants to look up a specific dictionary item by its numeric ID.
        """

        try:
            return dict_service.get_dict_item(isn)
        except McpOracleError as exc:
            LOGGER.warning("Tool request failed: %s", exc)
            return {
                "ok": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
            }
        except Exception:  # pragma: no cover - defensive guardrail
            LOGGER.exception("Unhandled server error")
            return {
                "ok": False,
                "error": {
                    "type": "InternalServerError",
                    "message": "Unexpected error while fetching dictionary item.",
                },
            }

    @server.tool()
    def get_dict_item_by_constname(constname: str) -> dict:
        """Get a dictionary entry from ais.dicti by constname (string constant identifier).

        Use this tool when analyzing code that calls c.get('SOME_CONSTANT') or references
        a dictionary item by its symbolic name rather than a numeric ISN.
        The lookup is case-insensitive (constname is matched with UPPER()).
        """

        try:
            return dict_service.get_dict_item_by_constname(constname)
        except McpOracleError as exc:
            LOGGER.warning("Tool request failed: %s", exc)
            return {
                "ok": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
            }
        except Exception:  # pragma: no cover - defensive guardrail
            LOGGER.exception("Unhandled server error")
            return {
                "ok": False,
                "error": {
                    "type": "InternalServerError",
                    "message": "Unexpected error while fetching dictionary item.",
                },
            }

    return server


def main() -> None:
    server = build_server()
    try:
        server.run(transport="stdio")
    except TypeError:
        server.run()


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


if __name__ == "__main__":
    main()
