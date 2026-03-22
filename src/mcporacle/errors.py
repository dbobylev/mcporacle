"""Domain errors for the mcporacle server."""


class McpOracleError(Exception):
    """Base project exception."""


class ConfigurationError(McpOracleError):
    """Raised when application configuration is missing or invalid."""


class InputValidationError(McpOracleError):
    """Raised when a tool input fails validation."""


class TableNotFoundError(McpOracleError):
    """Raised when the requested table does not exist or is invisible."""


class OracleDependencyError(McpOracleError):
    """Raised when required Oracle dependencies are unavailable."""


class OracleConnectionError(McpOracleError):
    """Raised when the application cannot connect to Oracle."""


class OracleAccessError(McpOracleError):
    """Raised when Oracle rejects metadata access."""
