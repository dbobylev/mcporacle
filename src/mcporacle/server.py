"""MCP server entrypoint."""

import logging
from typing import Any

from mcporacle.config import Settings
from mcporacle.errors import McpOracleError
from mcporacle.oracle.client import OracleMetadataRepository
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
    server = FastMCP("mcporacle")

    @server.tool()
    def get_table_info(schema_name: str, table_name: str) -> dict:
        """Return Oracle table metadata from a fixed DBA-view backed lookup."""

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
