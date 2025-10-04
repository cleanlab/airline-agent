import json
import logging

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding  # type: ignore[import-untyped]
from pydantic_ai import ModelRetry

from airline_agent.constants import RAG_EMBED_MODEL
from airline_agent.types.knowledge_base import DirectoryEntry, KBArticle, SearchResult

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, kb_path: str, vector_index_path: str):
        with open(kb_path) as f:
            kb_entries: list[KBArticle] = [KBArticle(**article) for article in json.load(f)]
        self._kb: dict[str, KBArticle] = {article.path: article for article in kb_entries}

        storage_context = StorageContext.from_defaults(persist_dir=vector_index_path)
        self._vector_index = load_index_from_storage(
            storage_context, embed_model=OpenAIEmbedding(model_name=RAG_EMBED_MODEL)
        )
        if not isinstance(self._vector_index, VectorStoreIndex):
            msg = "index is not a VectorStoreIndex"
            raise TypeError(msg)

    def get_article(self, path: str) -> str:
        """
        Get a knowledge base article by its path.

        Args:
            path: The absolute path of the knowledge base article.

        Returns:
            The contents of the knowledge base article.
        """
        logger.info("getting knowledge base article: %r", path)
        if path not in self._kb:
            msg = f"knowledge base article not found: {path}"
            raise ModelRetry(msg)
        return self._kb[path].content

    _DEFAULT_MAX_RESULTS = 5
    _MAX_RESULTS_LIMIT = 10

    def search(self, query: str, max_results: int = _DEFAULT_MAX_RESULTS) -> list[SearchResult]:
        """
        Search the knowledge base for entries matching the given query.

        Args:
            query: The search query.
            max_results: The maximum number of results to return. Must be between 1 and 10.

        Returns:
            A list of search results.
        """
        logger.info("searching knowledge base for query: %r (max results=%d)", query, max_results)
        if max_results < 1 or max_results > self._MAX_RESULTS_LIMIT:
            msg = f"max_results must be between 1 and {self._MAX_RESULTS_LIMIT}: {max_results}"
            raise ValueError(msg)
        retriever = self._vector_index.as_retriever(similarity_top_k=max_results)
        docs = retriever.retrieve(query)
        return [
            SearchResult(
                title=doc.metadata["title"],
                snippet=doc.text,
                snippet_start=doc.node.start_char_idx,  # type: ignore[attr-defined]
                snippet_end=doc.node.end_char_idx,  # type: ignore[attr-defined]
                more=(doc.text != self._kb[doc.metadata["path"]].content),
                path=doc.metadata["path"],
            )
            for doc in docs
        ]

    def list_directory(self, directory: str) -> list[DirectoryEntry]:
        """
        List all the files and directories in a given directory.

        Args:
            directory: The absolute path of the directory to list.

        Returns:
            A list of files and directories in the given directory.
        """
        # Our kb doesn't really have a directory structure, individual items have paths that may contain `/` characters
        # (e.g., like S3), so we simulate the directory structure. The KB is small enough that we can do O(n) operations
        # over the whole KB.
        logger.info("listing directory: %r", directory)
        if not directory.startswith("/"):
            msg = f"directory must be an absolute path starting with '/': {directory}"
            raise ValueError(msg)
        if not directory.endswith("/"):
            directory += "/"  # ensure directory ends with "/" for uniform handling
        entries: set[DirectoryEntry] = set()
        for path in self._kb:
            if not path.startswith(directory):
                continue
            suffix = path[len(directory) :]
            if "/" not in suffix:
                # found a file
                entries.add(DirectoryEntry(name=suffix, kind="file"))
            else:
                # found a directory
                dir_name = suffix.split("/", 1)[0]
                entries.add(DirectoryEntry(name=dir_name, kind="directory"))
        return sorted(entries, key=lambda e: e.name)
