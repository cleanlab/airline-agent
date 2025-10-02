from typing import Literal

from pydantic import BaseModel, Field


class Metadata(BaseModel, frozen=True):
    title: str = Field(..., description="Title of the document")


class KBArticle(BaseModel, frozen=True):
    path: str = Field(..., description="Absolute path of the document")
    metadata: Metadata = Field(..., description="Metadata of the document")
    content: str = Field(..., description="Content of the document")


class DirectoryEntry(BaseModel, frozen=True):
    name: str = Field(..., description="Name of the file or directory")
    kind: Literal["file", "directory"] = Field(..., description="Type of the entry")


class SearchResult(BaseModel, frozen=True):
    title: str = Field(..., description="Title of the document")
    snippet: str = Field(..., description="The snippet of the document that matches the search query")
    snippet_start: int = Field(..., description="The start character index of the snippet in the document")
    snippet_end: int = Field(..., description="The end character index of the snippet in the document")
    more: bool = Field(..., description="Whether the document has more content beyond what is included in the snippet")
    path: str = Field(..., description="Absolute path of the document")
