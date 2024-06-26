"""Experiment module."""

from __future__ import annotations

from datetime import datetime
from re import compile as recompile
from typing import List, Tuple
from uuid import UUID

from pydantic import BaseModel, Field, validate_call
from typing_extensions import Annotated

from pyaqueduct.client import AqueductClient

_MAX_TITLE_LENGTH = 100
_MAX_DESCRIPTION_LENGTH = 2000
_MAX_TAG_LENGTH = 50

TagString = Annotated[str, Field(..., max_length=_MAX_TAG_LENGTH)]


def is_valid_tag(tag: str) -> bool:
    """Check if consists of only alphanumeric characters, underscore and hyphens"""
    pattern = recompile("^[a-zA-Z0-9_-]+$")

    return bool(pattern.match(tag))


class Experiment(BaseModel):
    """Experiment model."""

    _client: AqueductClient
    "Client object reference."
    id: UUID
    "Unique ID of the experiment."
    alias: str
    "Alias of the experiment."
    created_at: datetime
    "Creation datetime of the experiment."

    def __init__(
        self, experiment_id: UUID, alias: str, created_at: datetime, client: AqueductClient, **data
    ):
        super().__init__(id=experiment_id, alias=alias, created_at=created_at, **data)
        self._client = client

    @property
    def title(self) -> str:
        """Get title of experiment."""
        return self._client.get_experiment(experiment_uuid=self.id).title

    @title.setter
    @validate_call
    def title(self, value: str = Field(..., max_length=_MAX_TITLE_LENGTH)) -> None:
        """Set title of experiment.

        Args:
            value: New title.

        """
        self._client.update_experiment(experiment_uuid=self.id, title=value)

    @property
    def description(self) -> str:
        """Get description of experiment."""
        return self._client.get_experiment(self.id).description

    @description.setter
    @validate_call
    def description(self, value: str = Field(..., max_length=_MAX_DESCRIPTION_LENGTH)) -> None:
        """Set description of experiment.

        Args:
            value: New description.

        """
        self._client.update_experiment(experiment_uuid=self.id, description=value)

    @property
    def tags(self) -> List[str]:
        """Gets tags of experiment."""
        return self._client.get_experiment(self.id).tags

    @validate_call
    def add_tags(self, tags: List[TagString]) -> None:
        """Add new tags to experiment.

        Args:
            tags: List of tags to be added to the experiment.

        """

        invalid_tags = [tag for tag in tags if not is_valid_tag(tag)]
        if invalid_tags:
            raise ValueError(
                f"Tags {invalid_tags} should only contain alphanumeric characters, "
                "underscores or hyphens."
            )

        self._client.add_tags_to_experiment(experiment_uuid=self.id, tags=tags)

    @validate_call
    def remove_tag(self, tag: str = Field(..., max_length=_MAX_TAG_LENGTH)) -> None:
        """Remove tag from experiment."""
        self._client.remove_tag_from_experiment(experiment_uuid=self.id, tag=tag)

    @property
    def files(self) -> List[Tuple[str, datetime]]:
        """Get file names of expriment."""
        return [
            (item.name, item.modified_at) for item in self._client.get_experiment(self.id).files
        ]

    @validate_call
    def download_file(self, file_name: str, destination_dir: str) -> None:
        """Download the specified file of experiment."""
        self._client.download_file(self.id, file_name=file_name, destination_dir=destination_dir)

    @validate_call
    def upload_file(self, file: str) -> None:
        """Upload the specified file to experiment."""
        self._client.upload_file(self.id, file=file)

    @property
    def updated_at(self) -> datetime:
        """Get last updated datetime of the experiment."""
        return self._client.get_experiment(self.id).updated_at
