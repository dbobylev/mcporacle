"""Business logic for the get_dict_item MCP tool."""

from typing import Protocol

from mcporacle.models import DictItemInfo


class DictRepository(Protocol):
    """Small repository contract used by the dict item service."""

    def fetch_dict_item(self, isn: int) -> DictItemInfo:
        """Return dictionary item for the given ISN."""

    def fetch_dict_item_by_constname(self, constname: str) -> DictItemInfo:
        """Return dictionary item for the given constname."""


class DictItemService:
    """Coordinates Oracle dictionary lookup by ISN or constname."""

    def __init__(self, repository: DictRepository) -> None:
        self._repository = repository

    def get_dict_item(self, isn: int) -> dict:
        return self._repository.fetch_dict_item(isn).to_dict()

    def get_dict_item_by_constname(self, constname: str) -> dict:
        return self._repository.fetch_dict_item_by_constname(constname).to_dict()
